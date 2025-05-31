import streamlit as st 
import pandas as pd
import mysql.connector as mysqlc
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

st.set_page_config(
    page_title= "Dashboard Solus",
    initial_sidebar_state= "expanded",
    layout= "wide"
)

def conexao():
    return mysqlc.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def query(sql):
    conn = conexao()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

st.title("Dashboard para loja Solus")

def tabelaCliente():
    st.header("Clientes")
    clientes = query("SELECT * FROM clientes")
    st.dataframe(clientes)
    
    
def tabelaProdutos():
    st.header("Produtos")
    produtos = query("SELECT * FROM produtos")
    st.dataframe(produtos)
    
col1, col2 = st.columns(2)

with col1:
    tabelaCliente()

with col2:
    tabelaProdutos()
