import streamlit as st
import requests
import pandas as pd
import time

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

@st.cache_data # Deixar o arquivo em cache
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

st.title('DADOS BRUTOS')

URL = 'https://labdados.com/produtos'

response = requests.get(URL)
df = pd.DataFrame.from_dict(response.json())
df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format = '%d/%m/%Y')


with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(df.columns), list(df.columns))


st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', df['Produto'].unique(), df['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', df['Categoria do Produto'].unique(), df['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (df['Data da Compra'].min(), df['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', df['Vendedor'].unique(), df['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', df['Local da compra'].unique(), df['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',df['Tipo de pagamento'].unique(), df['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))
    
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

df_filtrados = df.query(query)
df_filtrados = df_filtrados[colunas]

st.dataframe(df_filtrados)

st.markdown(f'A tabela possui :blue[{df_filtrados.shape[0]}] linhas e :blue[{df_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')


coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', 
                       data = converte_csv(df_filtrados), 
                       file_name = nome_arquivo, 
                       mime = 'text/csv', 
                       on_click = mensagem_sucesso)