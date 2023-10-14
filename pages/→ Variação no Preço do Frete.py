import streamlit as st
import pandas as pd
import locale
import plotly.graph_objects as go

locale.setlocale(locale.LC_ALL, 'pt_BR')
### Configuração da Página ###
st.set_page_config(
    page_title='EVOLUÇÂO FRETES BRASIL',
    page_icon='💲',
    layout='wide',
    initial_sidebar_state='collapsed',
    menu_items={
        'Get Help': 'http://www.meusite.com.br',
        'Report a bug': "http://www.meuoutrosite.com.br",
        'About': "Esse app foi desenvolvido no nosso Curso."
    }
)

### Carregamento dos dataframes ###
df_ipca = pd.read_excel("./TABELAS/IPCA.xlsx")
df_ipca['DATA'] = df_ipca['DATA'].dt.strftime('%b/%y')

df_diesel = pd.read_excel("./TABELAS/DIESEL_S10.xlsx")
df_diesel['DATA INICIAL'] = df_diesel['DATA INICIAL'].dt.strftime('%b/%y')

### Colunas de seleção do período ###
st.header('CALCULADORA DA EVOLUÇÃO DO CUSTO DE FRETE - BRASIL')
col_per1, col_per2, col_UF = st.columns([1,1,1])
with col_UF:
    sel_UF = st.selectbox('Selecione o estado:',
        options=df_diesel['ESTADO'].unique())
with col_per1:
    periodo_inicial = st.selectbox('Selecione o período inicial:',
             options=df_ipca['DATA'].unique())
    
    ipca_inicial = df_ipca['INDICE'].shift(1).loc[(
        df_ipca['DATA'] == periodo_inicial
    )].sum()
    
    if ipca_inicial == 0:
        ipca_inicial = 4916.46
    st.write(f'Índice IPCA: {ipca_inicial}')
    
    
    diesel_inicial = df_diesel['média mês -1'].loc[(
        df_diesel['DATA INICIAL'] == periodo_inicial) &(
        df_diesel['ESTADO'] == sel_UF
    )].sum()
    st.write(f'Preço Diesel: {diesel_inicial}')
   
with col_per2:
    periodo_final = st.selectbox('Selecione o período final:',
             options=df_ipca['DATA'].unique())
    
    ipca_final = df_ipca['INDICE'].loc[(
        df_ipca['DATA'] == periodo_final
    )].sum()
    st.write(f'Índice IPCA: {ipca_final}')    

    diesel_final = df_diesel['média mês'].loc[(
        df_diesel['DATA INICIAL'] == periodo_final) &(
        df_diesel['ESTADO'] == sel_UF
    )].sum()
    st.write(f'Preço Diesel: {diesel_final}')


### Cálculo da variação do IPCA e DIESEL % ###
evolução_ipca = round((ipca_final / ipca_inicial -1) *100,2)

evolução_diesel = round((diesel_final / diesel_inicial -1) *100,2)

### Gráfico de Model Change
referencia = 1000
gap_inflação = referencia * 0.4 * evolução_ipca / 100
gap_diesel = round(referencia * 0.6 * evolução_diesel / 100,2)
Novo_Custo = referencia + gap_inflação + gap_diesel
taxa_evolução_total = round((0.40 * evolução_ipca + 0.6*evolução_diesel),2)

fig = go.Figure(go.Waterfall(
    name = "Model Change",
    orientation = "v",
    measure = ["absolute", "relative", "relative", "total"],
    x = ["Referência", "Gap Inflação", "Gap Diesel", "Novo Custo"],
    textposition = "outside",
    text = [referencia, gap_inflação, gap_diesel,Novo_Custo],
    y = [referencia, gap_inflação, gap_diesel, Novo_Custo],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
))
fig.update_layout(
    title = "Model Change Custo de Fretes",
    showlegend = False
)
fig.update_yaxes(range=[referencia*0.5, Novo_Custo*1.1])
st.plotly_chart(fig,use_container_width=True)

st.write(f'No período selecionado, no estado **{sel_UF}**, o frete apresentou uma evolução de **{taxa_evolução_total}%**. \
         Isso se deve pela variação do IPCA no período (**{evolução_ipca}%**) e Diesel (**{evolução_diesel}%**).')

st.warning('Para uma abertura detalhada deste cálculo, assine nossa versão premium.')