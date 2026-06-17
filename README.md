# Nexus

Projeto de analytics para o dataset Brazilian E-commerce da Olist, com pipeline de dados, EDA e dashboard executivo.

## Fluxo do sistema

1. `src/main.py` baixa os dados da Olist, feriados nacionais e estados/regioes do IBGE.
2. `src/pipeline/build_analytics.py` consolida a base final em `data/processed/orders_analytics.csv`.
3. `src/eda_nexus.py` gera estatisticas e figuras em `reports/`.
4. `src/api/dashboard_api.py` expoe uma API HTTP para alimentar o dashboard.
5. `src/design/dashboard.html` consome `/api/dashboard` e renderiza os indicadores.

## Rodar o pipeline

```powershell
uv run python src/main.py
uv run python src/pipeline/build_analytics.py
uv run python -m src.eda_nexus
```

## Rodar a API e o dashboard

```powershell
uv run python -m src.api.dashboard_api
```

Ao iniciar, a API executa automaticamente:

1. extracao dos dados da Olist, feriados e IBGE;
2. construcao de `data/processed/orders_analytics.csv`;
3. geracao das estatisticas e figuras em `reports/`;
4. publicacao do dashboard e dos endpoints HTTP.

Depois acesse:

- Dashboard: http://127.0.0.1:8000/dashboard
- API: http://127.0.0.1:8000/api/dashboard
- Health check: http://127.0.0.1:8000/api/health

Para desenvolvimento, se voce quiser subir a API apenas validando os artefatos ja existentes, use:

```powershell
uv run python -m src.api.dashboard_api --no-pipeline
```
