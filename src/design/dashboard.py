from __future__ import annotations

import argparse
import io
import math
import warnings
from dataclasses import dataclass
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
import streamlit as st

warnings.filterwarnings("ignore")

# ── CONFIGURAÇÃO DO TEMA EXECUTIVO CLARO ─────────────────────
@dataclass(frozen=True)
class DashboardTheme:
    BG: str       = "#ffffff" # Fundo geral puro
    SURFACE: str  = "#ffffff" # Cartões puros
    SURFACE2: str = "#f8fafc" # Fundo de apoio (Slate 50 - um cinza frio muito sutil)
    BORDER: str   = "#e2e8f0" # Bordas nítidas, mas não agressivas
    ACCENT: str   = "#2563eb" # Azul Profissional (confiança/primário)
    CORAL: str    = "#ef4444" # Vermelho Vibrante (alerta/atrasos)
    AMBER: str    = "#f59e0b" # Âmbar (mediano/atenção - legível no branco)
    VIOLET: str   = "#7c3aed" # Roxo Profundo (qualidade/destaque secundário)
    GREEN: str    = "#10b981" # Esmeralda (sucesso/entregue)
    TEXT: str     = "#1e293b" # Chumbo escuro (quase preto, altíssimo contraste)
    MUTED: str    = "#64748b" # Cinza médio-escuro (perfeito para legendas)
    DIM: str      = "#cbd5e1" # Cinza claro (para divisórias discretas)

THEME = DashboardTheme()

# ── RESOLUÇÃO DE CAMINHOS DA BASE DE DADOS ────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SCRIPT_DIR.parent
_DEFAULT_CSV_PATHS = [
    _ROOT_DIR / "data" / "processed" / "orders_analytics.csv",
    Path.cwd() / "data" / "processed" / "orders_analytics.csv",
    _SCRIPT_DIR / "orders_analytics.csv",
]

def resolve_csv_path(override: str | None = None) -> Path | None:
    if override:
        p = Path(override)
        return p if p.exists() else None
    return next((p for p in _DEFAULT_CSV_PATHS if p.exists()), None)

# ── CAMADA DE DADOS E CACHE BASE ─────────────────────────────
@st.cache_data(show_spinner="A carregar base analítica…")
def load_data(csv_path: str) -> pd.DataFrame:
    date_cols = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "purchase_date",
    ]
    return pd.read_csv(csv_path, parse_dates=date_cols)

# ── FORMATADORES AUXILIARES ───────────────────────────────────
def safe_round(v, dec=2) -> float | None:
    if v is None or (isinstance(v, float) and (math.isnan(v) or not math.isfinite(v))):
        return None
    return round(float(v), dec)

def fmt_int(v) -> str:
    return f"{int(v):,}".replace(",", ".") if v is not None else "0"

def fmt_dec(v, dec=2) -> str:
    val = safe_round(v, dec)
    if val is None:
        return "0"
    return f"{val:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(v, dec=2) -> str:
    return f"{fmt_dec(v, dec)}%"

def calc_pct(v, dec=2) -> float | None:
    val = safe_round(v, dec + 2)
    return round(float(val) * 100, dec) if val is not None else None

# ── PROCESSAMENTO DE MÉTRICAS DINÂMICO ───────────────────────
@st.cache_data(show_spinner=False)
def compute_dashboard_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {k: {"value": 0, "fmt": "0"} for k in [
            "orders_total", "delivered_total", "delivered_rate", "late_rate", 
            "delivery_days_mean", "delivery_days_median", "freight_mean", 
            "freight_max", "distance_mean", "distance_p75", "distance_completeness",
            "duplicate_orders", "invalid_delivery", "null_delivery_pct", "null_distance_pct"
        ]}

    delivered = df[df["is_delivered"] == True]

    delivered_rate = len(delivered) / len(df) if len(df) else 0
    late_rate = delivered["is_late"].mean() if len(delivered) else 0
    dist_complete = df["distance_km"].notna().mean()

    return {
        "orders_total": {"value": len(df), "fmt": fmt_int(len(df))},
        "delivered_total": {"value": len(delivered), "fmt": fmt_int(len(delivered))},
        "delivered_rate": {"value": calc_pct(delivered_rate), "fmt": fmt_pct(calc_pct(delivered_rate))},
        "late_rate": {"value": calc_pct(late_rate), "fmt": fmt_pct(calc_pct(late_rate))},
        "delivery_days_mean": {"fmt": f"{fmt_dec(delivered['delivery_days'].mean())} dias"},
        "delivery_days_median": {"fmt": f"{fmt_dec(delivered['delivery_days'].median())} dias"},
        "freight_mean": {"fmt": f"R$ {fmt_dec(df['total_freight_value'].mean())}"},
        "freight_max": {"fmt": f"R$ {fmt_dec(df['total_freight_value'].max())}"},
        "distance_mean": {"fmt": f"{fmt_dec(df['distance_km'].mean())} km"},
        "distance_p75": {"fmt": f"{fmt_dec(df['distance_km'].quantile(0.75))} km"},
        "distance_completeness": {"value": calc_pct(dist_complete), "fmt": fmt_pct(calc_pct(dist_complete))},
        "duplicate_orders": {"fmt": fmt_int(df.get("order_id", pd.Series()).duplicated().sum())},
        "invalid_delivery": {"fmt": fmt_int((delivered["delivery_days"] < 0).sum())},
        "null_delivery_pct": {"fmt": fmt_pct(calc_pct(df["order_delivered_customer_date"].isna().mean()))},
        "null_distance_pct": {"fmt": fmt_pct(calc_pct(df["distance_km"].isna().mean()))},
    }

# ── FABRICAÇÃO DE GRÁFICOS (MATPLOTLIB/SEABORN) ───────────────
def create_base_figure(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=THEME.BG)
    ax.set_facecolor(THEME.SURFACE)
    for spine in ax.spines.values():
        spine.set_edgecolor(THEME.BORDER)
    ax.tick_params(colors=THEME.MUTED, labelsize=9)
    ax.xaxis.label.set_color(THEME.MUTED)
    ax.yaxis.label.set_color(THEME.MUTED)
    return fig, ax

def convert_fig_to_png(fig) -> bytes:
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, facecolor=THEME.BG, bbox_inches="tight")
        return buf.getvalue()
    finally:
        plt.close(fig)

@st.cache_data(show_spinner=False)
def render_monthly_orders(df: pd.DataFrame) -> bytes | None:
    if df.empty: return None
    monthly = df.groupby(df["order_purchase_timestamp"].dt.to_period("M")).size().reset_index(name="orders")
    monthly["date"] = monthly["order_purchase_timestamp"].dt.to_timestamp()
    monthly = monthly[(monthly["date"] >= "2017-01-01") & (monthly["date"] <= "2018-08-31")]

    fig, ax = create_base_figure(9, 3.4)
    ax.fill_between(monthly["date"], monthly["orders"], alpha=0.15, color=THEME.ACCENT)
    ax.plot(monthly["date"], monthly["orders"], color=THEME.ACCENT, linewidth=2.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}".replace(",", ".")))
    ax.grid(axis="y", color=THEME.BORDER, linewidth=1, linestyle="--")
    return convert_fig_to_png(fig)

@st.cache_data(show_spinner=False)
def render_delivery_histogram(df: pd.DataFrame) -> bytes | None:
    delivered = df[df["is_delivered"] == True]
    if delivered.empty: return None
    
    fig, ax = create_base_figure(7, 3.4)
    ax.hist(delivered["delivery_days"].dropna().clip(0, 45), bins=42, color=THEME.ACCENT, alpha=0.8, edgecolor=THEME.SURFACE)
    ax.axvline(delivered["delivery_days"].median(), color=THEME.AMBER, linewidth=2, linestyle="--", label="Mediana")
    ax.legend(facecolor=THEME.SURFACE, edgecolor=THEME.BORDER, labelcolor=THEME.TEXT, fontsize=8)
    ax.set_xlabel("Dias de entrega")
    ax.grid(axis="y", color=THEME.BORDER, linewidth=1, linestyle="--")
    return convert_fig_to_png(fig)

@st.cache_data(show_spinner=False)
def render_freight_by_region(df: pd.DataFrame) -> bytes | None:
    if df.empty or "customer_region" not in df.columns: return None
    region_order = df.groupby("customer_region")["total_freight_value"].median().sort_values(ascending=False).index.tolist()
    data_box = [df[df["customer_region"] == r]["total_freight_value"].dropna().clip(0, 150).values for r in region_order]
    
    fig, ax = create_base_figure(7, 3.4)
    ax.boxplot(data_box, patch_artist=True, 
               medianprops={"color": THEME.ACCENT, "linewidth": 2},
               whiskerprops={"color": THEME.MUTED}, capprops={"color": THEME.MUTED},
               flierprops={"marker": ".", "color": THEME.MUTED, "alpha": 0.3, "markersize": 3},
               boxprops={"facecolor": THEME.SURFACE2, "edgecolor": THEME.BORDER})
    ax.set_xticklabels(region_order, fontsize=8, color=THEME.TEXT)
    ax.set_ylabel("Frete (R$)")
    ax.grid(axis="y", color=THEME.BORDER, linewidth=1, linestyle="--")
    return convert_fig_to_png(fig)

@st.cache_data(show_spinner=False)
def render_scatter_distance(df: pd.DataFrame) -> bytes | None:
    delivered = df[df["is_delivered"] == True]
    if delivered.empty: return None
    
    clean_data = delivered[["distance_km", "delivery_days", "is_late"]].dropna()
    if clean_data.empty: return None
    
    sample_size = min(3000, len(clean_data))
    sample = clean_data.sample(n=sample_size, random_state=42)
    
    colors = [THEME.CORAL if late else THEME.ACCENT for late in sample["is_late"]]
    
    fig, ax = create_base_figure(7, 3.4)
    ax.scatter(sample["distance_km"], sample["delivery_days"], c=colors, s=8, alpha=0.5, edgecolors="none")
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=THEME.ACCENT, markersize=7, label="No prazo"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=THEME.CORAL,  markersize=7, label="Atrasado"),
    ]
    ax.legend(handles=legend_elements, facecolor=THEME.SURFACE, edgecolor=THEME.BORDER, labelcolor=THEME.TEXT, fontsize=8)
    ax.set_xlabel("Distância (km)")
    ax.set_ylabel("Dias de entrega")
    ax.grid(color=THEME.BORDER, linewidth=1, linestyle="--")
    return convert_fig_to_png(fig)

@st.cache_data(show_spinner=False)
def render_correlation_matrix(df: pd.DataFrame) -> bytes | None:
    delivered = df[df["is_delivered"] == True]
    if delivered.empty: return None
    cols = ["delivery_days", "total_freight_value", "distance_km", "payment_value", "review_score"]
    labels = ["Entrega\n(dias)", "Frete\n(R$)", "Distância\n(km)", "Valor\npago", "Review"]
    corr = delivered[cols].corr()
    
    fig, ax = create_base_figure(6.2, 4.8)
    sns.heatmap(corr, annot=True, fmt=".2f", ax=ax, cmap="Blues",
                xticklabels=labels, yticklabels=labels, linewidths=1, linecolor=THEME.SURFACE,
                annot_kws={"size": 9, "color": THEME.TEXT}, vmin=-1, vmax=1)
    ax.tick_params(colors=THEME.TEXT, labelsize=8)
    return convert_fig_to_png(fig)

# ── COMPONENTES DE INTERFACE REUTILIZÁVEIS ───────────────────
def inject_custom_css():
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: {THEME.BG}; }}
    [data-testid="stSidebar"] {{ background: {THEME.SURFACE}; border-right: 1px solid {THEME.BORDER}; }}
    [data-testid="stSidebar"] * {{ color: {THEME.TEXT} !important; }}
    [data-testid="stSidebar"] .sidebar-title {{ color: {THEME.TEXT} !important; font-weight: 700; }}
    hr {{ border-color: {THEME.BORDER} !important; }}
    p, li {{ color: {THEME.MUTED}; }}
    h1, h2, h3 {{ color: {THEME.TEXT} !important; }}
    /* Ajuste fino nas bordas dos containers nativos do Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {THEME.BORDER} !important; background-color: {THEME.SURFACE} !important; }}
    /* Clarear métricas do Streamlit */
    [data-testid="stMetricValue"] {{ color: {THEME.TEXT} !important; font-weight: 700; }}
    </style>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = ""):
    sub_html = f'<div style="font-size:12px;color:{THEME.MUTED};margin-top:2px">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div style="margin-bottom:14px"><div style="font-size:16px;font-weight:700;color:{THEME.TEXT}">{title}</div>{sub_html}</div>', unsafe_allow_html=True)

def render_progress_indicator(label: str, value: float, color: str = THEME.ACCENT):
    clamped = max(0.0, min(100.0, value)) if value is not None else 0
    st.markdown(f"""
    <div style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;font-size:13px;color:{THEME.TEXT};margin-bottom:4px;font-weight:500;">
        <span>{label}</span><span>{clamped:.2f}%</span>
      </div>
      <div style="background:{THEME.DIM};border-radius:99px;height:8px;overflow:hidden">
        <div style="width:{clamped}%;height:100%;background:{color};border-radius:99px"></div>
      </div>
    </div>""", unsafe_allow_html=True)

def render_insight_card(color: str, title: str, body: str):
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;gap:12px;align-items:flex-start;">
          <div style="width:4px;height:36px;border-radius:99px;background:{color};flex-shrink:0;margin-top:2px"></div>
          <div>
            <div style="font-size:13px;font-weight:700;color:{THEME.TEXT};margin-bottom:2px">{title}</div>
            <div style="font-size:12px;color:{THEME.MUTED};line-height:1.5">{body}</div>
          </div>
        </div>""", unsafe_allow_html=True)


# ── EXECUÇÃO PRINCIPAL DO ECOSSISTEMA ────────────────────────
def run_dashboard(csv_path: str):
    st.set_page_config(
        page_title="Nexus | Dashboard Executivo",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()

    raw_df = load_data(csv_path)

    # ── BANDEJA LATERAL (SIDEBAR) FUNCIONAL ───────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:24px">
          <div style="width:34px;height:34px;display:grid;place-items:center;background:{THEME.ACCENT};color:#fff;font-weight:700;font-size:16px;border-radius:6px;flex-shrink:0">N</div>
          <div>
            <div class="sidebar-title" style="font-size:15px;font-weight:700;color:{THEME.TEXT}">Nexus Analytics</div>
            <div style="font-size:12px;color:{THEME.MUTED}">Filtros Globais</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### Região Geográfica")
        available_regions = sorted(raw_df["customer_region"].dropna().unique()) if "customer_region" in raw_df.columns else []
        selected_regions = st.multiselect(
            "Selecione as regiões para análise:",
            options=available_regions,
            default=available_regions,
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Status da Entrega")
        status_filter = st.radio(
            "Filtrar por status do pedido:",
            ["Todos os Pedidos", "Apenas Entregues", "Atrasados"],
            label_visibility="collapsed"
        )

        st.divider()
        st.markdown(f"<p style='font-size:11px;color:{THEME.DIM};line-height:1.6'>Filtros aplicados recarregam automaticamente toda a volumetria e gráficos do dashboard.</p>", unsafe_allow_html=True)

    # ── APLICAÇÃO DOS FILTROS NO DATAFRAME ───────────────────
    filtered_df = raw_df.copy()
    
    if selected_regions:
        filtered_df = filtered_df[filtered_df["customer_region"].isin(selected_regions)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    if status_filter == "Apenas Entregues":
        filtered_df = filtered_df[filtered_df["is_delivered"] == True]
    elif status_filter == "Atrasados":
        filtered_df = filtered_df[filtered_df["is_late"] == True]

    # ── CABEÇALHO DO PAINEL ─────────────────────────────────
    col_title, col_status = st.columns([6, 1])
    with col_title:
        st.markdown(f"<p style='font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:{THEME.ACCENT};margin-bottom:4px;font-weight:700;'>Fase 2 · Análise exploratória</p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:24px;font-weight:800;color:{THEME.TEXT};margin-bottom:4px'>Operação, entrega e valor executivo.</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:14px;color:{THEME.MUTED}'>Desempenho do e-commerce brasileiro unificado para tomadas de decisão estruturadas.</p>", unsafe_allow_html=True)
    with col_status:
        st.markdown(f"<div style='float:right; display:flex;align-items:center;gap:7px;padding:6px 12px;background:{THEME.SURFACE};border:1px solid {THEME.BORDER};border-radius:999px;font-size:12px;color:{THEME.TEXT};font-weight:500;margin-top:12px'><span style='width:8px;height:8px;border-radius:50%;background:{THEME.GREEN};display:inline-block'></span>Base validada</div>", unsafe_allow_html=True)

    st.divider()

    # ── GRID DE MÉTRICAS NATIVAS ─────────────────────────────
    metrics = compute_dashboard_metrics(filtered_df)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        with st.container(border=True):
            st.metric("Pedidos filtrados", metrics["orders_total"]["fmt"], "Volume analisado")
    with c2:
        with st.container(border=True):
            st.metric("Pedidos entregues", metrics["delivered_total"]["fmt"], f'{metrics["delivered_rate"]["fmt"]} do escopo')
    with c3:
        with st.container(border=True):
            st.metric("Taxa de atraso", metrics["late_rate"]["fmt"], "Acima do estimado")
    with c4:
        with st.container(border=True):
            st.metric("Tempo médio", metrics["delivery_days_mean"]["fmt"], f'Mediana: {metrics["delivery_days_median"]["fmt"]}')

    st.divider()

    # ── TENDÊNCIAS, INSIGHTS E SAÚDE OPERACIONAL ─────────────
    col_chart, col_right = st.columns([3, 2], gap="medium")

    with col_chart:
        render_section_header("Tendência mensal de pedidos", "Volume de vendas por mês a partir de 2017.")
        img_monthly = render_monthly_orders(filtered_df)
        if img_monthly: st.image(img_monthly, width="stretch")
        else: st.warning("Dados insuficientes para este gráfico com os filtros atuais.")

    with col_right:
        render_section_header("Leituras-chave", "Sinais mais importantes para priorização.")
        render_insight_card(THEME.ACCENT, "Entrega como centro da experiência", f'O prazo médio consolidado fixa-se em {metrics["delivery_days_mean"]["fmt"]}.')
        render_insight_card(THEME.CORAL, "Frete concentrado com outliers", f'O frete médio é de {metrics["freight_mean"]["fmt"]}, alcançando máximos de {metrics["freight_max"]["fmt"]}.')
        render_insight_card(THEME.AMBER, "Distância relevante na operação", f'A distância média calculada é {metrics["distance_mean"]["fmt"]}, com 75% da volumetria abaixo de {metrics["distance_p75"]["fmt"]}.')
        
        st.divider()
        render_section_header("Saúde operacional do recorte", "Indicadores de completude.")
        render_progress_indicator("Pedidos entregues", metrics["delivered_rate"]["value"] or 0, THEME.ACCENT)
        render_progress_indicator("Pedidos em atraso", metrics["late_rate"]["value"] or 0, THEME.CORAL)
        render_progress_indicator("Dados de distância completos", metrics["distance_completeness"]["value"] or 0, THEME.VIOLET)

    st.divider()

    # ── DIAGRÁSTICAS E DISPERSÃO ─────────────────────────────
    col_hist, col_box = st.columns(2, gap="medium")
    with col_hist:
        render_section_header("Distribuição do tempo de entrega", "Concentração, mediana e cauda longa de atrasos.")
        img_hist = render_delivery_histogram(filtered_df)
        if img_hist: st.image(img_hist, width="stretch")
    with col_box:
        render_section_header("Frete por região", "Distribuição regional e dispersão de custos logísticos.")
        img_box = render_freight_by_region(filtered_df)
        if img_box: st.image(img_box, width="stretch")

    st.divider()

    col_scat, col_heat = st.columns(2, gap="medium")
    with col_scat:
        render_section_header("Distância versus entrega", "Relação entre quilometragem estimada e prazo real de entrega.")
        img_scat = render_scatter_distance(filtered_df)
        if img_scat: st.image(img_scat, width="stretch")
    with col_heat:
        render_section_header("Correlações numéricas", "Cruzamento de sinais entre valor, frete, distância e pontuação de review.")
        img_corr = render_correlation_matrix(filtered_df)
        if img_corr: st.image(img_corr, width="stretch")

    st.divider()

    st.markdown(f"<p style='text-align:center;font-size:12px;color:{THEME.MUTED};margin-top:24px'>Fontes: Olist, Feriados Nacionais e Regiões IBGE.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--csv", default=None)
    args, _ = parser.parse_known_args()

    csv_file = resolve_csv_path(args.csv)
    if csv_file is None:
        st.error("Base analítica não encontrada. Especifique o caminho correto utilizando o parâmetro --csv.")
        raise SystemExit(1)

    run_dashboard(str(csv_file))