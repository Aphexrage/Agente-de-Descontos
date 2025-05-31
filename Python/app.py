import streamlit as st 
import pandas as pd
import mysql.connector as mysqlc
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

st.set_page_config(
    page_title="Dashboard Solus",
    layout="wide"
)

st.sidebar.image("./assets/icone.png", width=800)

def conexao():
    return mysqlc.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def query(sql):
    conn = conexao()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

with st.sidebar:
    st.header("Ordenação")
    ordem_compras = st.radio(
        "Ordenar clientes por:",
        ("Mais compras", "Menos compras"),
        index=0
    )
    
    st.markdown("---")
    st.write("Filtros:")
    mostrar_uma_compra = st.checkbox("Mostrar clientes com 1 compra", True)

clientes = query("SELECT id, nome, email FROM clientes")
produtos = query("SELECT id_cliente, data_compra FROM produtos")

compras_por_cliente = produtos.groupby("id_cliente").size().reset_index(name='Total Compras')
dados_completos = compras_por_cliente.merge(clientes, left_on='id_cliente', right_on='id')

if ordem_compras == "Mais compras":
    dados_ordenados = dados_completos.sort_values('Total Compras', ascending=False)
else:
    dados_ordenados = dados_completos.sort_values('Total Compras')
    
st.title("Análise de compras por Cliente")
st.dataframe(
    dados_ordenados[['nome', 'email', 'Total Compras']]
        .rename(columns={
            'nome': 'Cliente',
            'email': 'E-mail',
            'Total Compras': 'Total de Compras'
        }),
    height=500,
    use_container_width=True,
    hide_index=True,
    column_config={
        "E-mail": st.column_config.TextColumn(width="large") 
    }
)

if mostrar_uma_compra:
    st.title("Clientes com 1 compra que não retornaram")
    clientes_uma_compra = dados_completos[dados_completos['Total Compras'] == 1]
    
    if not clientes_uma_compra.empty:
        ultima_compra = produtos.groupby('id_cliente')['data_compra'].max().reset_index()
        clientes_uma_compra = clientes_uma_compra.merge(
            ultima_compra,
            on='id_cliente'
        )
        clientes_uma_compra['Dias desde compra'] = (datetime.datetime.now() - pd.to_datetime(clientes_uma_compra['data_compra'])).dt.days
        
        st.dataframe(
            clientes_uma_compra[['nome', 'email', 'Dias desde compra']] 
                .rename(columns={
                    'nome': 'Cliente',
                    'email': 'E-mail'
                })
                .sort_values('Dias desde compra', ascending=False),
            height=300,
            use_container_width=True,
            hide_index=True,
            column_config={
                "E-mail": st.column_config.TextColumn(width="large"),
                "Dias desde compra": st.column_config.NumberColumn(
                    format="%d dias",
                    help="Quantidade de dias desde a ultima compra"
                )
            }
        )
    else:
        st.info("Nao foi encontrado nenhum cliente.")