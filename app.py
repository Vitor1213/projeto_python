import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Análise de Vendas",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/Vitor1213/projeto_python/main/projeto_python.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['Data_Venda'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Clientes
clientes_disponiveis = sorted(df['Cliente'].unique())
clientes_selecionados = st.sidebar.multiselect("Clientes", clientes_disponiveis, default=clientes_disponiveis)

# Filtro por Canal de Venda
canal_vendas_disponiveis = sorted(df['Canal_Venda'].unique())
canal_vendas_selecionados = st.sidebar.multiselect("Canal de Venda", canal_vendas_disponiveis, default=canal_vendas_disponiveis)

# Filtro por Status
status_disponiveis = sorted(df['Status'].unique())
status_selecionados = st.sidebar.multiselect("Status", status_disponiveis, default=status_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df = df[
    (df['Data_Venda'].isin(anos_selecionados)) &
    (df['Cliente'].isin(clientes_selecionados)) &
    (df['Canal_Venda'].isin(canal_vendas_selecionados)) &
    (df['Status'].isin(status_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Vendas")
st.markdown("Explore os dados de vendas nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Vendas)")

if not df.empty:
    vendas_medias = df['Receita_Total'].sum()
    vendas_maximas = df['Receita_Total'].max()
    total_vendas = df.shape[0]
    canal_vendas = df["Canal_Venda"].mode()[0]
else:
    vendas_medias, vendas_maximas, total_vendas, canal_vendas = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendas médias", f"${vendas_medias:,.0f}")
col2.metric("Vendas máximas", f"${vendas_maximas:,.0f}")
col3.metric("Total de vendas", f"{total_vendas:,}")
col4.metric("Canal de vendas mais frequente", canal_vendas)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df.empty:
        top_produtos = df.groupby('Produto')['Receita_Total'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_produtos = px.bar(
            top_produtos,
            x='Receita_Total',
            y='Produto',
            orientation='h',
            title="Top 10 média de produtos mais vendidos",
            labels={'Receita_Total': 'Média de produtos vendidos', 'Produto': ''}
        )
        grafico_produtos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_produtos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de produtos.")

with col_graf2:
    if not df.empty:
        grafico_hist = px.histogram(
            df,
            x='Receita_Total',
            nbins=30,
            title="Distribuição de vendas",
            labels={'Receita_Total': 'Faixa de vendas', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df.empty:
        canal_venda_contagem = df['Canal_Venda'].value_counts().reset_index()
        canal_venda_contagem.columns = ['Categoria', 'quantidade']
        grafico_canal_venda = px.pie(
            canal_venda_contagem,
            names='Categoria',
            values='quantidade',
            title='Proporção de Vendas por Canal',
            hole=0.5
        )
        grafico_canal_venda.update_traces(textinfo='percent+label')
        grafico_canal_venda.update_layout(title_x=0.1)
        st.plotly_chart(grafico_canal_venda, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df.empty:
        # Filtrar produto Notebook
        df_ds = df[df['Produto'] == 'Notebook']
        # Calcular média por cidade
        media_ds_produto = df_ds.groupby('Cidade')['Quantidade'].mean().reset_index()
        # Carregar GeoJSON com estados do Brasil
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        geojson = requests.get(url).json()
        # Criar gráfico
        grafico_estados = px.choropleth(
            media_ds_produto,
            geojson=geojson,
            locations='Cidade',                # Coluna do DF (sigla ex: SP, RJ)
            featureidkey="properties.sigla",   # Nome da chave no GeoJSON
            color='Quantidade',
            color_continuous_scale='RdYlGn',
            title='Quantidade média de Notebooks vendidos por Cidade',
            labels={'Quantidade': 'Média vendida'}
        )
        grafico_estados.update_geos(fitbounds="locations", visible=False)
        grafico_estados.update_layout(title_x=0.1)
        # Mostrar no Streamlit
        st.plotly_chart(grafico_estados, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cidades.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df)
