import os
import pandas as pd
import mysql.connector as mysqlc
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()

class AgenteEmail:
    def __init__(self):
        self.conn = mysqlc.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        self.cursor = self.conn.cursor()

        # Dados de e-mail agora vêm do .env
        self.email_remetente = os.getenv("EMAIL_REMETENTE")
        self.senha_app = os.getenv("SENHA_APP")

    def obter_dados(self):
        clientes = pd.read_sql("SELECT id, nome, email FROM clientes", self.conn)
        produtos = pd.read_sql("SELECT id_cliente, data_compra FROM produtos", self.conn)
        return clientes, produtos

    def enviar_emails(self):
        clientes, produtos = self.obter_dados()

        compras = produtos.groupby("id_cliente").size().reset_index(name="Total Compras")
        ultimas_compras = produtos.groupby("id_cliente")["data_compra"].max().reset_index()

        dados = clientes.merge(compras, left_on="id", right_on="id_cliente", how="left")
        dados = dados.merge(ultimas_compras, on="id_cliente", how="left")
        dados["Total Compras"] = dados["Total Compras"].fillna(0).astype(int)
        dados["Dias desde ultima compra"] = (
            datetime.now() - pd.to_datetime(dados["data_compra"])
        ).dt.days.fillna(9999).astype(int)

        for _, row in dados.iterrows():
            email = row["email"]
            nome = row["nome"]
            compras = row["Total Compras"]
            dias = row["Dias desde ultima compra"]

            if compras >= 5:
                self._enviar_email_promocao(email, nome, tipo='sorteio')
            elif dias > 30:
                self._enviar_email_promocao(email, nome, tipo='desconto')

    def _enviar_email_promocao(self, destinatario, nome, tipo='sorteio'):
        msg = EmailMessage()
        msg['Subject'] = "Temos uma oferta especial pra você!"
        msg['From'] = self.email_remetente
        msg['To'] = destinatario

        if tipo == 'sorteio':
            texto = f"""
Olá {nome}!

Você está entre os nossos melhores clientes 🎉 e foi selecionado para participar de um sorteio exclusivo de produtos.

Boa sorte!
"""
        elif tipo == 'desconto':
            texto = f"""
Olá {nome}!

Sentimos sua falta! Que tal voltar com 15% de desconto e frete grátis no seu próximo pedido?

Aproveite agora! 🚀
"""

        msg.set_content(texto.strip())

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.email_remetente, self.senha_app)
                smtp.send_message(msg)

            print(f"E-mail enviado para {destinatario} ({tipo})")
        except Exception as e:
            print(f"Erro ao enviar e-mail para {destinatario}: {e}")

    def fechar(self):
        self.conn.close()
