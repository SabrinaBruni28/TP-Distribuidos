import smtplib
from email.mime.text import MIMEText

def enviar_email_mailtrap():
    smtp_server = "sandbox.smtp.mailtrap.io"
    smtp_port = 587
    login = "441dc67f5a72c9"
    senha = "1ad21d439d5114"

    remetente = "testecaldeirao@gmail.com"
    destinatario = "sabrinabrunisouza416@gmail.com"

    mensagem = MIMEText("Olá, isso é um teste do Mailtrap.")
    mensagem["Subject"] = "Teste"
    mensagem["From"] = remetente
    mensagem["To"] = destinatario

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(login, senha)
        server.send_message(mensagem)

enviar_email_mailtrap()
