import socket
import threading
from Operacoes import server_operation as op
from Operacoes import thread_email as correio

class Cadastramento():
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexaoCliente = socket_cliente
        self.conexaoServidor = socket_servidor
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        self.cadastrar()

    def cadastrar(self):
        dados = self.mensagemCliente.camposMensagem[1]
        mensagemServidor = op.codifica("criar | usuario | " + str(dados))

        print("[Servidor] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoServidor)
        resposta = self.conexaoServidor.recv(2048).decode("utf-8")

        self.signupHandler(dados, resposta)

    def signupHandler(self, dados_json, resposta_banco):
        if resposta_banco[0] == "ok":
            emailCliente = dados_json.get("email")

            while True:
                email = correio.ThreadEmail("confirmacao cadastro", emailCliente).start()
                codigoConfirmacao = email.codigo
                codigoCliente = self.conexaoServidor.recv(2048).decode("utf-8")

                if codigoCliente[1] == codigoConfirmacao:
                    mensagemAoCliente = op.codifica("ok | " +str(dados_json))

                    self.conexaoCliente.sendall(mensagemAoCliente)
                    break

        else:
            mensagemAoCliente = op.codifica("erro | " + str(resposta_banco[1]))

            print("[Servidor] Reportando erro de cadastro...")
            self.conexaoCliente.sendall(mensagemAoCliente)