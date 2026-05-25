from __future__ import annotations
import math
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "brazilian-ecommerce"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT_DIR / "reports"

def haversine_km(
    lat1: pd.Series,
    lng1: pd.Series,
    lat2: pd.Series,
    lng2: pd.Series,
) -> pd.Series:
    earth_radius_km = 6371.0
    lat1_rad = lat1.map(math.radians)
    lng1_rad = lng1.map(math.radians)
    lat2_rad = lat2.map(math.radians)
    lng2_rad = lng2.map(math.radians)

    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    a = (dlat / 2).map(math.sin) ** 2 + lat1_rad.map(math.cos) * lat2_rad.map(math.cos) * (dlng / 2).map(math.sin) ** 2
    return 2 * earth_radius_km * a.map(math.sqrt).map(math.asin)


def read_sources() -> dict[str, pd.DataFrame]:
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    return {
        "orders": pd.read_csv(RAW_DIR / "olist_orders_dataset.csv", parse_dates=date_cols),
        "customers": pd.read_csv(RAW_DIR / "olist_customers_dataset.csv"),
        "items": pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"]),
        "payments": pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv"),
        "reviews": pd.read_csv(RAW_DIR / "olist_order_reviews_dataset.csv"),
        "products": pd.read_csv(RAW_DIR / "olist_products_dataset.csv"),
        "sellers": pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv"),
        "categories": pd.read_csv(RAW_DIR / "product_category_name_translation.csv"),
        "geolocation": pd.read_csv(RAW_DIR / "olist_geolocation_dataset.csv"),
        "holidays": pd.read_csv(DATA_DIR / "brazil_holidays.csv", parse_dates=["date"]),
        "ibge": pd.read_csv(DATA_DIR / "ibge_states_regions.csv"),
    }

def build_orders_analytics(sources: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = sources["orders"].copy()
    customers = sources["customers"].copy()
    items = sources["items"].copy()
    payments = sources["payments"].copy()
    reviews = sources["reviews"].copy()
    products = sources["products"].copy()
    sellers = sources["sellers"].copy()
    categories = sources["categories"].copy()
    geolocation = sources["geolocation"].copy()
    holidays = sources["holidays"].copy()
    ibge = sources["ibge"].copy()

    geo_by_zip = (
        geolocation.groupby("geolocation_zip_code_prefix", as_index=False)
        .agg(
            lat=("geolocation_lat", "mean"),
            lng=("geolocation_lng", "mean"),
        )
    )

    products["product_volume_cm3"] = (
        products["product_length_cm"] * products["product_height_cm"] * products["product_width_cm"]
    )

    items_with_products = items.merge(products, on="product_id", how="left").merge(
        categories, on="product_category_name", how="left"
    )

    item_order = (
        items_with_products.groupby("order_id", as_index=False)
        .agg(
            items_qty=("order_item_id", "max"),
            products_qty=("product_id", "nunique"),
            sellers_qty=("seller_id", "nunique"),
            total_products_value=("price", "sum"),
            total_freight_value=("freight_value", "sum"),
            avg_product_weight_g=("product_weight_g", "mean"),
            avg_product_volume_cm3=("product_volume_cm3", "mean"),
            main_product_category=("product_category_name_english", lambda x: x.dropna().mode().iloc[0] if not x.dropna().mode().empty else "unknown"),
            first_seller_id=("seller_id", "first"),
        )
    )

    payments_order = (
        payments.groupby("order_id", as_index=False)
        .agg(
            payment_value=("payment_value", "sum"),
            installments=("payment_installments", "max"),
            payment_type=("payment_type", lambda x: x.mode().iloc[0] if not x.mode().empty else "unknown"),
        )
    )

    reviews_order = (
        reviews.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            reviews_qty=("review_id", "nunique"),
        )
    )

    customer_regions = ibge.rename(
        columns={
            "state_abbr": "customer_state",
            "state_name": "customer_state_name",
            "region_name": "customer_region",
            "region_abbr": "customer_region_abbr",
        }
    )[["customer_state", "customer_state_name", "customer_region", "customer_region_abbr"]]

    seller_regions = ibge.rename(
        columns={
            "state_abbr": "seller_state",
            "state_name": "seller_state_name",
            "region_name": "seller_region",
            "region_abbr": "seller_region_abbr",
        }
    )[["seller_state", "seller_state_name", "seller_region", "seller_region_abbr"]]

    customers_geo = customers.merge(
        geo_by_zip.add_prefix("customer_"),
        left_on="customer_zip_code_prefix",
        right_on="customer_geolocation_zip_code_prefix",
        how="left",
    ).merge(customer_regions, on="customer_state", how="left")

    sellers_geo = sellers.merge(
        geo_by_zip.add_prefix("seller_"),
        left_on="seller_zip_code_prefix",
        right_on="seller_geolocation_zip_code_prefix",
        how="left",
    ).merge(seller_regions, on="seller_state", how="left")

    analytics = (
        orders.merge(customers_geo, on="customer_id", how="left")
        .merge(item_order, on="order_id", how="left")
        .merge(sellers_geo, left_on="first_seller_id", right_on="seller_id", how="left")
        .merge(payments_order, on="order_id", how="left")
        .merge(reviews_order, on="order_id", how="left")
    )

    analytics["purchase_date"] = analytics["order_purchase_timestamp"].dt.normalize()
    analytics["order_year"] = analytics["order_purchase_timestamp"].dt.year
    analytics["order_month"] = analytics["order_purchase_timestamp"].dt.to_period("M").astype(str)
    analytics["order_weekday"] = analytics["order_purchase_timestamp"].dt.day_name()
    analytics["is_holiday_purchase"] = analytics["purchase_date"].isin(holidays["date"].dt.normalize())

    analytics["delivery_days"] = (
        analytics["order_delivered_customer_date"] - analytics["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    analytics["estimated_days"] = (
        analytics["order_estimated_delivery_date"] - analytics["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    analytics["late_days"] = (
        analytics["order_delivered_customer_date"] - analytics["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    analytics["is_delivered"] = analytics["order_delivered_customer_date"].notna()
    analytics["is_late"] = (analytics["late_days"] > 0).astype("boolean")
    analytics.loc[~analytics["is_delivered"], "is_late"] = pd.NA

    analytics["same_state"] = analytics["customer_state"] == analytics["seller_state"]
    analytics["same_region"] = analytics["customer_region"] == analytics["seller_region"]
    analytics["route_region"] = analytics["seller_region"].fillna("Unknown") + " -> " + analytics["customer_region"].fillna("Unknown")
    analytics["distance_km"] = haversine_km(
        analytics["seller_lat"],
        analytics["seller_lng"],
        analytics["customer_lat"],
        analytics["customer_lng"],
    )

    selected_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "purchase_date",
        "order_year",
        "order_month",
        "order_weekday",
        "is_holiday_purchase",
        "is_delivered",
        "delivery_days",
        "estimated_days",
        "late_days",
        "is_late",
        "customer_state",
        "customer_state_name",
        "customer_region",
        "customer_city",
        "customer_lat",
        "customer_lng",
        "seller_state",
        "seller_state_name",
        "seller_region",
        "seller_city",
        "seller_lat",
        "seller_lng",
        "same_state",
        "same_region",
        "route_region",
        "distance_km",
        "items_qty",
        "products_qty",
        "sellers_qty",
        "total_products_value",
        "total_freight_value",
        "avg_product_weight_g",
        "avg_product_volume_cm3",
        "payment_value",
        "installments",
        "payment_type",
        "main_product_category",
        "review_score",
        "reviews_qty",
    ]

    return analytics[selected_columns].copy()

def quality_report(sources: dict[str, pd.DataFrame], analytics: pd.DataFrame) -> str:
    source_rows = "\n".join(
        f"| {name} | {len(df):,} | {len(df.columns):,} |"
        for name, df in sources.items()
    )

    nulls = analytics.isna().mean().sort_values(ascending=False).head(12)
    null_rows = "\n".join(f"| `{col}` | {pct:.2%} |" for col, pct in nulls.items())

    delivered = analytics[analytics["is_delivered"] == True]
    invalid_delivery = delivered[delivered["delivery_days"] < 0]
    duplicate_orders = analytics["order_id"].duplicated().sum()
    late_rate = delivered["is_late"].mean()

    return f"""# Relatório de Qualidade dos Dados

                ## Volume das fontes

                | Fonte | Linhas | Colunas |
                | --- | ---: | ---: |
                {source_rows}

                ## Base final

                - Arquivo: `data/processed/orders_analytics.csv`
                - Granularidade: uma linha por pedido (`order_id`)
                - Linhas: {len(analytics):,}
                - Colunas: {len(analytics.columns):,}
                - Pedidos entregues com data valida: {len(delivered):,}
                - Taxa de atraso em pedidos entregues: {late_rate:.2%}
                - Pedidos duplicados na base final: {duplicate_orders:,}
                - Entregas com prazo negativo: {len(invalid_delivery):,}

                ## Maiores percentuais de nulos na base final

                | Coluna | Percentual nulo |
                | --- | ---: |
                {null_rows}

                ## Observações de qualidade

                - Pedidos nao entregues foram mantidos na base, mas `is_late` fica vazio porque nao ha como calcular atraso real sem data de entrega.
                - A geolocalizacao foi agregada por prefixo de CEP para evitar duplicidade tecnica no arquivo original.
                - A distancia entre vendedor e cliente e aproximada, baseada nos centroides dos prefixos de CEP.
            """

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    sources = read_sources()
    analytics = build_orders_analytics(sources)
    analytics.to_csv(PROCESSED_DIR / "orders_analytics.csv", index=False)

    report = quality_report(sources, analytics)
    (REPORTS_DIR / "phase1_quality_report.md").write_text(report, encoding="utf-8")

    print(f"Saved analytics dataset: {PROCESSED_DIR / 'orders_analytics.csv'}")
    print(f"Saved quality report: {REPORTS_DIR / 'phase1_quality_report.md'}")


if __name__ == "__main__":
    main()
