import streamlit as st
import requests
import pandas as pd 
import plotly.express as px 

URL = 'https://labdados.com/produtos'

REGIOES = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

def get_data(query_string=None) -> pd.DataFrame:
    """
        Retorna o dataframe já tratado
    """
    response = requests.get(URL, params=query_string)
    df = pd.DataFrame.from_dict(response.json())
    df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format= '%d/%m/%Y') 
    return df

def format_number(valor: float, prefixo = '') -> str:
    """
        Retorna o valor de forma descritiva resumida
    """
    if valor < 1000:  
        return f'{prefixo} {valor:.2f}' 

    valor /= 1000
    if valor < 1000: 
        return f'{prefixo} {(valor):.2f} mil'
    
    valor /= 1000
    return f'{prefixo} {valor:.2f} milhões' 

### Tabelas for Receitas
def group_by_receita_estados(df: pd.DataFrame) -> pd.DataFrame:
    """
        Retorna um dataframe com as colunas de 'Local da compra', 'lat', 'lon', 'Preço'
    """
    receita_estados = df.groupby('Local da compra')[['Preço']].sum()
    localizacao_estados = df.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']]
    
    df_merge = localizacao_estados.merge(receita_estados, left_on='Local da compra', right_index=True)
    df_merge = df_merge.sort_values(by='Preço', ascending=False)

    return df_merge

def group_by_receita_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """
        Retorna um dataframe com as colunas de 'Data da Compra', 'Preço', 'Ano', 'Mês'
    """
    receita_mensal = df.groupby(pd.Grouper(key='Data da Compra', 
                                           freq='M')) # Agrupando por mês
    
    receita_mensal = receita_mensal['Preço'].sum()
    receita_mensal = receita_mensal.reset_index()

    receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
    receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

    return receita_mensal

def group_by_receita_categorias(df: pd.DataFrame) -> pd.DataFrame:
    """
        Retorna um dataframe com as colunas de 'Categoria do Produto', 'Preço'
    """
    receita_categorias = df.groupby('Categoria do Produto')['Preço'].sum()
    receita_categorias = receita_categorias.reset_index()
    return receita_categorias


### Tabelas for Vendedores
def group_by_vendedores(df: pd.DataFrame) -> pd.DataFrame:
    """
        Return é um dataframe com Vendedor como index e as colunas 'sum', 'count'
    """
    vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg(['sum', 'count']))
    return vendedores

def fig_receita_vendedores(qtd_vendedores: int) -> px.bar:
    receita_vendedores = group_by_vendedores(df)
    receita_vendedores = receita_vendedores[['sum']].sort_values(by='sum', ascending=False).head(qtd_vendedores)
    fig_receita_vendedores = px.bar(receita_vendedores,
                                    x = 'sum',
                                    y = receita_vendedores.index,
                                    text_auto=True,
                                    title=f'Top {qtd_vendedores} Vendedores (receita)')
    return fig_receita_vendedores
    
def fig_vendas_vendedores(qtd_vendedores: int) -> px.bar:
    vendas_vendedores = group_by_vendedores(df)
    vendas_vendedores = vendas_vendedores[['count']].sort_values(by='count', ascending=False).head(qtd_vendedores)
    fig_vendas_vendedores = px.bar(vendas_vendedores,
                                    x = 'count',
                                    y = vendas_vendedores.index,
                                    text_auto=True,
                                    title=f'Top {qtd_vendedores} Vendedores (qtd de vendas)')
    return fig_vendas_vendedores
        


### Stramlit
def dash_view(df: pd.DataFrame, 
              receita_total: float, 
              fig_mapa_receita: px.scatter_geo,
              fig_receita_estados: px.bar,
              fig_receita_mensal: px.line,
              fig_receita_categorias: px.bar):
    
    st.set_page_config(layout='wide')
    st.title("Dashboard de venda :shopping_trolley:")
    
    st.sidebar.title('Filtros')
    
    # target_regiao = st.sidebar.selectbox('Região', REGIOES)
    # if target_regiao != 'Brasil': 
    #     df = df[df['Região'] == target_regiao]
    
    todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
    if todos_anos != True:
        ano = st.sidebar.slider('Ano', 2020, 2023)  
        df = df[df['Data da Compra'].dt.year == ano]

    
    filtro_vendedores = st.sidebar.multiselect('Vendedores', df['Vendedor'].unique())
    if filtro_vendedores:
        df = df[df['Vendedor'].isin(filtro_vendedores)]
    
    aba1, aba2 = st.tabs(['Receita', 'Vendedores'])
    with aba1:
        col1, col2 = st.columns(2)
        with col1: 
            st.metric('Receita total', format_number(receita_total, 'R$'))
            st.plotly_chart(fig_mapa_receita, use_container_width=True)
            st.plotly_chart(fig_receita_estados, use_container_width=True)
        with col2:
            st.metric('Quantidade de venda', format_number(df.shape[0]))
            st.plotly_chart(fig_receita_mensal, use_container_width=True)
            st.plotly_chart(fig_receita_categorias, use_container_width=True)
    with aba2:
        qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
        col1, col2 = st.columns(2)
        with col1: 
            st.plotly_chart(fig_receita_vendedores(qtd_vendedores))
        with col2:
            st.plotly_chart(fig_vendas_vendedores(qtd_vendedores))

    st.write(df )

if __name__ == "__main__":
    df = get_data()

    receita_total = df['Preço'].sum()

    df_estados = group_by_receita_estados(df)
    fig_mapa_receita = px.scatter_geo(df_estados, 
                                      lat = 'lat', 
                                      lon = 'lon',
                                      scope = 'south america',
                                      size = 'Preço',
                                      template = 'seaborn',
                                      hover_name ='Local da compra',
                                      hover_data = {'lat': False, 'lon': False},
                                      title = 'Receita por estado')
    
    fig_receita_estados = px.bar(df_estados[:5],
                                 x = 'Local da compra',
                                 y = 'Preço',
                                 text_auto = True,
                                 title = 'Top Estados (Receitas)')
    fig_receita_estados.update_layout(yaxis_title='Receita')


    df_receita_mensal= group_by_receita_mensal(df)
    fig_receita_mensal = px.line(df_receita_mensal,
                                 x = 'Mês',
                                 y = 'Preço',
                                 markers = True,
                                 range_y = (0, df_receita_mensal.max()),
                                 color = 'Ano',
                                 line_dash = 'Ano',
                                 title = 'Receita Mensal')
    fig_receita_mensal.update_layout(yaxis_title='Receita')


    df_receita_categorias = group_by_receita_categorias(df)
    fig_receita_categorias = px.bar(df_receita_categorias,
                                    x='Categoria do Produto',
                                    y='Preço',
                                    text_auto=True,
                                    title='Receita por categoria')
    fig_receita_categorias.update_layout(yaxis_title='Receita')

    dash_view(df, 
              receita_total, 
              fig_mapa_receita, 
              fig_receita_estados, 
              fig_receita_mensal,
              fig_receita_categorias)
