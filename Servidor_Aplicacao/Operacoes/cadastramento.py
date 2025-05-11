import socket
import threading
import json
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
        dadosJson = json.loads(dados)
        mensagemServidor = op.codifica("criar | usuario | " + json.dumps(dadosJson))

        print("[Servidor] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoServidor)
        resposta = self.conexaoServidor.recv(2048).decode("utf-8")

        self.signupHandler(dados, dadosJson, resposta)

    def signupHandler(self, dados, dados_json, resposta_banco):
        if resposta_banco[0] == "ok":
            emailCliente = dados_json.get("email")

            email = correio.ThreadEmail("confirmacao cadastro", emailCliente).start()
            codigoConfirmacao = email.codigo

            tentativas = 0

            while tentativas < 3:
                tentativas += 1
                codigoCliente = self.conexaoServidor.recv(2048).decode("utf-8")

                if codigoCliente[1] == codigoConfirmacao:
                    mensagemAoCliente = op.codifica("ok | " +str(dados))

                    self.conexaoCliente.sendall(mensagemAoCliente)
                    return

                else:
                    mensagemAoCliente = op.codifica("erro | codigo_invalido")
                    self.conexaoCliente.sendall(mensagemAoCliente)

            mensagemAoCliente = op.codifica("erro | limite_excedido")
            self.conexaoCliente.sendall(mensagemAoCliente)

        else:
            mensagemAoCliente = op.codifica("erro | " + str(resposta_banco[1]))

            print("[Servidor] Reportando erro de cadastro...")
            self.conexaoCliente.sendall(mensagemAoCliente)