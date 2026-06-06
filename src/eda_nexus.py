import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent 

DATA_DIR = ROOT_DIR / "data" / "processed"
REPORTS_DIR = ROOT_DIR / "reports" / "figures"
REPORTS_DIR.mkdir(parents=True, exist_ok=True) 


sns.set_theme(style="whitegrid", palette="muted")

print("Carregando base de dados analítica...")

df = pd.read_csv(DATA_DIR / "orders_analytics.csv")
df['purchase_date'] = pd.to_datetime(df['purchase_date'])



print("\n" + "="*50)
print(" FASE 2: ANÁLISE EXPLORATÓRIA E DESCRITIVA (EDA)")
print("="*50)


print("\n[1] Estatística Descritiva (Médias, Medianas, Quartis e Desvio Padrão)")
metricas_chave = ['total_products_value', 'total_freight_value', 'delivery_days', 'distance_km']
estatisticas = df[metricas_chave].describe().round(2)
print(estatisticas)


with open("reports/estatisticas_descritivas.txt", "w") as f:
    f.write("Estatisticas Descritivas - Variaveis Principais\n")
    f.write(estatisticas.to_string())


print("\n[2] Gerando Visualizações Iniciais...")

plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='delivery_days', bins=50, kde=True, color='#0c3b5e')
plt.title('Distribuição do Tempo de Entrega (Dias)', fontsize=14, pad=15)
plt.xlabel('Dias para Entrega')
plt.ylabel('Quantidade de Pedidos')
plt.xlim(0, 60) 
plt.savefig(REPORTS_DIR / 'hist_tempo_entrega.png', bbox_inches='tight')
plt.close()


plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='customer_region', y='total_freight_value', palette='Blues_r')
plt.title('Dispersão do Valor do Frete por Região do Cliente', fontsize=14, pad=15)
plt.xlabel('Região do Cliente')
plt.ylabel('Valor do Frete (R$)')
plt.ylim(0, 150)
plt.savefig(REPORTS_DIR / 'box_frete_regiao.png', bbox_inches='tight')
plt.close()


print("\n[3] Identificando Padrões e Correlações...")


plt.figure(figsize=(10, 6))
sns.scatterplot(data=df.sample(10000, random_state=42), # Amostra de 10k para otimizar plotagem
                x='distance_km', y='delivery_days', 
                alpha=0.3, color='#00a8e8')
plt.title('Relação: Distância (KM) vs Tempo de Entrega (Dias)', fontsize=14, pad=15)
plt.xlabel('Distância Estimada (KM)')
plt.ylabel('Tempo de Entrega (Dias)')
plt.savefig(REPORTS_DIR / 'scatter_distancia_tempo.png', bbox_inches='tight')
plt.close()


plt.figure(figsize=(8, 6))
cols_correlacao = ['total_products_value', 'total_freight_value', 'distance_km', 'delivery_days', 'review_score']
matriz_corr = df[cols_correlacao].corr()

sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, fmt=".2f")
plt.title('Matriz de Correlação - Variáveis Numéricas', fontsize=14, pad=15)
plt.savefig(REPORTS_DIR / 'heatmap_correlacao.png', bbox_inches='tight')
plt.close()


vendas_mes = df.groupby('order_month')['order_id'].count().reset_index()
vendas_mes = vendas_mes[vendas_mes['order_month'] >= '2017-01']

plt.figure(figsize=(14, 6))
sns.lineplot(data=vendas_mes, x='order_month', y='order_id', marker='o', color='#0c3b5e', linewidth=2)
plt.title('Tendência Temporal: Volume de Pedidos por Mês', fontsize=14, pad=15)
plt.xlabel('Mês do Pedido')
plt.ylabel('Quantidade de Pedidos')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(REPORTS_DIR / 'linha_tendencia_vendas.png', bbox_inches='tight')
plt.close()

print(f"✅ Análise concluída! Todos os gráficos foram salvos na pasta: {REPORTS_DIR}")