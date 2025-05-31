import streamlit as st 
import pandas as pd
import mysql.connector as mysqlc
from dotenv import load_dotenv
import os
import datetime
import base64
from agente import AgenteEmail

load_dotenv()

st.set_page_config(
    page_title="Dashboard Solus",
    page_icon= "./assets/icone2.png",
    initial_sidebar_state="expanded",   
    layout="wide"
)

def imagemBase64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = imagemBase64("./assets/icone.png")
    
st.sidebar.markdown(
    f"""
    <div style="margin-top: -90px;">
        <img src='data:image/png;base64,{logo_base64}' style='height: 200px; margin-right: 10px;'/>
        
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    if st.button("Enviar e-mails para clientes"):
        with st.spinner("Enviando e-mails..."):
            agente = AgenteEmail()
            agente.enviar_emails()
            agente.fechar()
        st.success("E-mails enviados com sucesso!")

icone_base64 = imagemBase64("./assets/icone2.png")

def esconderHeader():
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

esconderHeader()

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
    
st.markdown( 
    f"""
    <div style='
        font-size: 35px;
        text-align: center;
        font-weight: bold;
        margin-top: -70px;
        margin-bottom: 5px;
        display: flex;
        justify-content: center;
        align-items: center;
    '>
        <img src='data:image/png;base64,{icone_base64}' style='height: 40px; width: auto; margin-right: 10px;'/>
        Dashboard de Analise de Clientes!
    </div>
    
    <br></br>
    
    <div style='
        font-size: 16px;
        text-align: center;
        font-weight: normal;
        margin-bottom: 10px;
        margin-top: -60px;
    '>
        Total de Compras por cliente:
    </div>
    """,
    unsafe_allow_html=True
)

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
    
    st.markdown( 
    f"""
    
    <div style='
        font-size: 16px;
        text-align: center;
        font-weight: normal;
        margin-bottom: 10px;
        margin-top: 10px;
    '>
        Clientes que compraram apenas uma vez:
    </div>
    """,
    unsafe_allow_html=True
)
    
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