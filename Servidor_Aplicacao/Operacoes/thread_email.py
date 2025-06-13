from email.mime.text import MIMEText
import threading
import smtplib
import random

class ThreadEmail(threading.Thread):
    def __init__(self, tipo, email_destinatario):
        threading.Thread.__init__(self)
        self.email_destinatario = email_destinatario
        self.codigo = None
        
        if tipo == "confirmacao cadastro":
            self.assunto = "Confirmação de Cadastro"
            self.codigo = random.randint(100000, 999999)
            self.mensagem = f"""
            ========================================
                    CONFIRMAÇÃO DE CADASTRO
            ========================================

            Olá! Aqui é a equipe Caldeirão.

            Seu código de confirmação é:

                >>> {self.codigo} <<<

            Use este código para ativar sua conta no sistema.
            
            NÃO COMPARTILHE ESSE CÓDIGO COM NINGUÉM.

            ----------------------------------------
            Se você não solicitou este código, ignore esta mensagem.

            Atenciosamente,  
            Equipe Caldeirão
            """


        elif tipo == "confirmacao pedido":
            self.assunto = "Confirmação de Pedido"
            self.mensagem = f"""
            ========================================
                    CONFIRMAÇÃO DE PEDIDO
            ========================================

            Olá! Aqui é a equipe Caldeirão.
            
            Seu pedido foi confirmado com sucesso!

            ----------------------------------------
            Atenciosamente,  
            Equipe Caldeirão
            """


        elif tipo == "cancelamento pedido":
            self.assunto = "Cancelamento de Pedido"
            self.mensagem = f"""
            ========================================
                    CANCELAMENTO DE PEDIDO
            ========================================

            Olá! Aqui é a equipe Caldeirão.

            O vendedor cancelou seu pedido!

            ----------------------------------------
            Atenciosamente,  
            Equipe Caldeirão
            """


        elif tipo == "pedido realizado":
            self.assunto = "Pedido Realizado"
            self.mensagem = f"""
            ========================================
                        PEDIDO REALIZADO
            ========================================

            Olá! Aqui é a equipe Caldeirão.

            Um pedido foi realizado em sua loja!
            Você pode ir lá para conferir. Não deixe seu cliente esperando!

            ----------------------------------------
            Atenciosamente,  
            Equipe Caldeirão
            """


    def run(self):
        try:
            self.enviar_email_gmail(self.email_destinatario, self.assunto, self.mensagem)
        except Exception as e:
            print(f"Erro ao enviar email: {e}")

    def enviar_email_gmail(self, email_destinatario, assunto, mensagem):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_remetente = "testecaldeirao@gmail.com"
        senha_app = "olyq xgjv eykm hndj".replace(" ", "")  # Remover espaços

        email_destinatario = email_destinatario

        msg = MIMEText(mensagem)
        msg["Subject"] = assunto
        msg["From"] = email_remetente
        msg["To"] = email_destinatario

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_remetente, senha_app)
            server.send_message(msg)
