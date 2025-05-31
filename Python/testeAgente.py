import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['Subject'] = "Teste direto para Gustavo"
msg['From'] = "aphexragebot@gmail.com"
msg['To'] = "aphexragedev@gmail.com"
msg.set_content("Esse é um teste de entrega direta, sem HTML.")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login("aphexragebot@gmail.com", "tcbs wtxb nvjk xayr")
    smtp.send_message(msg)

print("E-mail enviado.")
