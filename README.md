# 📊 Nexus - Pipeline ETL para Análise de Dados em E-commerce (Trabalho A3)

Este projeto implementa um pipeline ETL (Extract, Transform and Load) desenvolvido em Python para coleta, tratamento, enriquecimento e consolidação de dados de comércio eletrônico brasileiro.

A solução integra diferentes fontes de dados, incluindo datasets do Kaggle, APIs externas e dados oficiais do IBGE, permitindo a construção de uma base analítica robusta para exploração de dados, geração de métricas e apoio à tomada de decisão.

O projeto foi desenvolvido para a Avaliação A3 da disciplina **Análise de Dados e Big Data**, aplicando conceitos de Engenharia de Dados, Qualidade de Dados, Estatística Descritiva e Business Intelligence.

---

# 👥 Equipe e Identificação

| Nome do Integrante                         | Registro Acadêmico (RA) |
| ------------------------------------------ | ----------------------- |
| Arthur Andrade Silva                       | 12724119792             |
| Eduardo de Andrade do Bomfim Júnior        | 12724142791             |
| Maria Julia Rodrigues Pereira              | 1272324889              |
| Tais Lisboa Leite                          | 1272320035              |
| Valentin Eduardo Carvalho Bispo dos Santos | 1272415745              |

---

# 🎯 Tema do Projeto

**E-commerce**

O projeto utiliza o dataset **Brazilian E-Commerce Public Dataset by Olist**, enriquecido com informações geográficas e calendários de feriados nacionais, possibilitando análises relacionadas a vendas, logística, comportamento do consumidor e desempenho operacional.

---

# 🚀 Como Executar o Projeto

Você pode visualizar e executar as análises deste projeto diretamente na nuvem ou configurá-lo no seu ambiente local.

Opção 1: Execução via Google Colab (Rápido)
Para visualizar as análises exploratórias (EDA) e rodar o projeto diretamente no navegador, sem precisar instalar nada na sua máquina:

🔗 Google Colab: https://colab.research.google.com/drive/17aK9Gap1pUsegNQNlLXvPLoi4iR-NjHc?usp=sharing

Opção 2: Execução Local
O projeto foi desenvolvido em Python e pode ser executado em qualquer ambiente compatível com Python 3.10.0 ou superior.

## Pré-requisitos

* Python 3.10.0+
* Git
* Kaggle API configurada
* Gerenciador de pacotes UV

## Clonando o Repositório

```bash
git clone https://github.com/AlphaLab2025/Nexus.git
cd Nexus
```

## Instalação das Dependências

```bash
uv sync
```

## Execução do Pipeline

```bash
uv run streamlit run src/design/dashboard.py -- --csv data/processed/orders_analytics.csv
```

---

# ⚙️ Funcionalidades e Requisitos Atendidos

A seguir estão descritas as funcionalidades implementadas para atender aos requisitos da Avaliação A3.

## 1. Extração de Dados (ETL - Fase 1)

O sistema realiza a coleta automatizada de dados provenientes de diferentes fontes.

### Dataset Principal (Kaggle)

O módulo `kaggle_download.py` realiza:

* Autenticação automática na API do Kaggle.
* Download do dataset Olist.
* Verificação de downloads já existentes.
* Extração automática dos arquivos.

### API Externa de Feriados

O projeto coleta informações sobre feriados nacionais utilizados para enriquecer as análises temporais.

### API Oficial do IBGE

O módulo `extract_ibge_locations.py` realiza:

* Consulta à API oficial do IBGE.
* Obtenção de estados brasileiros.
* Obtenção de regiões geográficas.
* Geração de base auxiliar para enriquecimento geográfico.

---

## 2. Transformação e Tratamento dos Dados

Durante a etapa de transformação são realizados:

* Limpeza dos dados.
* Padronização de formatos.
* Conversão de datas.
* Integração de múltiplas tabelas.
* Tratamento de valores ausentes.
* Enriquecimento geográfico.
* Criação de variáveis analíticas.

---

## 3. Construção da Base Analítica

O módulo `build_analytics.py` consolida informações provenientes de:

* Pedidos
* Clientes
* Produtos
* Itens dos pedidos
* Pagamentos
* Avaliações
* Vendedores
* Geolocalização
* Feriados nacionais
* Estados e regiões do IBGE

Gerando uma base analítica única para exploração dos dados.

---

## 4. Métricas e Indicadores Gerados

O sistema produz diversos indicadores relevantes para análise de e-commerce:

### Logística

* Tempo de entrega
* Prazo estimado
* Atraso de entrega
* Distância entre vendedor e cliente
* Entrega dentro ou fora do prazo

### Comercial

* Valor total dos produtos
* Valor total do frete
* Quantidade de itens por pedido
* Quantidade de produtos por pedido

### Clientes e Mercado

* Estado do cliente
* Região do cliente
* Cidade do cliente
* Estado do vendedor
* Região do vendedor
* Rotas logísticas entre regiões

### Pagamentos

* Valor pago
* Tipo de pagamento
* Quantidade de parcelas

### Experiência do Cliente

* Nota média das avaliações
* Quantidade de avaliações por pedido

---

## 5. Qualidade dos Dados

O projeto gera automaticamente um relatório de qualidade contendo:

* Volume das fontes de dados.
* Quantidade de linhas e colunas.
* Percentual de valores nulos.
* Taxa de atraso das entregas.
* Identificação de registros duplicados.
* Validação das datas de entrega.
* Observações sobre consistência dos dados.

---

## 6. Preparação para Análise Exploratória (EDA)

A base gerada permite a realização de análises como:

* Distribuição temporal das vendas.
* Impacto dos feriados nas compras.
* Avaliação do desempenho logístico.
* Comparação entre regiões.
* Identificação de padrões de consumo.
* Relação entre distância e prazo de entrega.

---

## 7. Suporte ao Storytelling e Dashboards

Os dados processados podem ser utilizados para:

* Dashboards interativos.
* Visualizações analíticas.
* Relatórios gerenciais.
* Apresentações executivas.
* Geração de insights estratégicos.

---

# 🛠️ Tecnologias Utilizadas

* Python
* Pandas
* Kaggle API
* APIs REST
* IBGE API
* CSV
* Docker
* UV Package Manager
* Colab

---

# 📁 Estrutura do Projeto

```text
NEXUS/
│
├── reports/
│   ├── figures/
│   │   ├── box_frete_regiao.png
│   │   ├── heatmap_correlacao.png
│   │   ├── hist_tempo_entrega.png
│   │   ├── linha_tendencia_vendas.png
│   │   └── scatter_distancia_tempo.png
│   ├── estatisticas_descritivas.txt
│   └── phase1_quality_report.md
│
├── src/
│   ├── design/
│   │   └── assets/
│   ├── pipeline/
│   │   ├── __pycache__/
│   │   │   └── kaggle_download.cpython-314.pyc
│   │   ├── build_analytics.py
│   │   ├── extract_external.py
│   │   ├── extract_ibge_locations.py
│   │   └── kaggle_download.py
│   ├── eda_nexus.py
│   └── main.py
│
├── .gitignore
├── .python-version
├── Dockerfile
├── LICENSE
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

---

# 🔄 Fluxo do Pipeline

```text
Kaggle Dataset (Olist)
            │
            ▼
    Extração de Dados
            │
            ├────────────► API de Feriados
            │
            └────────────► API do IBGE
            │
            ▼
   Transformação e Limpeza
            │
            ▼
 Enriquecimento Geográfico
            │
            ▼
 Construção da Base Analítica
            │
            ▼
 Relatório de Qualidade
            │
            ▼
 Dashboard e Storytelling
```

---

# 📈 Objetivos da Análise

O projeto busca:

* Aplicar conceitos de ETL em um cenário real.
* Integrar múltiplas fontes de dados.
* Garantir qualidade e consistência das informações.
* Construir uma base confiável para análise.
* Identificar padrões relevantes no setor de e-commerce.
* Produzir insights que apoiem a tomada de decisão.

---

# 📚 Contexto Acadêmico

Este projeto foi desenvolvido para a Avaliação A3 da disciplina **Análise de Dados e Big Data**, atendendo às etapas propostas:

* Processo ETL e Qualidade dos Dados.
* Análise Exploratória de Dados (EDA).
* Storytelling com Dados.
* Governança e Qualidade da Informação.

---

Este documento atende aos requisitos de documentação da Avaliação A3 da disciplina Análise de Dados e Big Data.
