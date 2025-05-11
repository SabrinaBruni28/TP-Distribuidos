import socket
import threading
from Operacoes import server_operation as op

class Login():
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexaoCliente = socket_cliente
        self.conexaoServidor = socket_servidor
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.logar()

    def logar(self):
        dados = self.mensagemCliente.camposMensagem[1]
        mensagemServidor = op.codifica("login | " + str(dados))

        print("[Servidor] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoServidor)
        resposta = self.conexaoServidor.recv(2048).decode("utf-8")

        if resposta[0] == "ok":
            mensagemAoCliente = op.codifica("ok | " + str(resposta[1]))

            print("[Servidor] Confirmando login do cliente...")
            self.conexaoCliente.sendall(mensagemAoCliente)

        else:
            mensagemAoCliente = op.codifica("erro | " + str(resposta[1]))

            print("[Servidor] Reportando erro de login ao cliente...")
            self.conexaoCliente.sendall(mensagemAoCliente)
    