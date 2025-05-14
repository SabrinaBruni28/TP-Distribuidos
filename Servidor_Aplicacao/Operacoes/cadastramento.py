import socket
import threading
import json
from Operacoes import thread_email as correio
from Operacoes import server_operation as op
from Operacoes import thread_email as correio
from Operacoes import operacao
from Estruturas import mensagem

class Cadastramento(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        self.conexaoServidor = socket_servidor

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
        self.fila.enfileira(mensagemServidor, op.respostaAoServidor, self.conexaoCliente, "cadastrar", self.conexaoServidor)

    @classmethod
    def cadastramentoCallback(cls, resposta_banco, socket_cliente, socket_servidor):
        resposta = [ws.strip() for ws in resposta_banco.split('|')]
        dados = resposta[1]
        dadosJson = json.dumps(dados)

        cls.signupHandler(dados, dadosJson, resposta, socket_cliente, socket_servidor)

    @staticmethod
    def _signupHandler(dados, dadosJson, resposta, cliente, servidor):
        if resposta[0] == "ok":
            emailCliente = dadosJson.get("email")
            email = correio.ThreadEmail("confirmacao cadastro", emailCliente).start()
            codigoConfirmacao = str(email.codigo)

            tentativas = 0
            while tentativas < 3:
                tentativas += 1
                codigoCliente = servidor.recv(6).decode("utf-8")

                if codigoCliente[1] == codigoConfirmacao:
                    mensagemAoCliente = op.fazMensagemServidor(f"ok | {dados}")
                    op.enviaMensagem(cliente, mensagemAoCliente)
                    return
                
                else:
                    mensagemAoCliente = op.fazMensagemServidor(f"erro | codigo_invalido")
                    op.enviaMensagem(cliente, mensagemAoCliente)
                    return
                
            mensagemAoCliente = op.fazMensagemServidor(f"erro | limite_excedido")
            op.enviaMensagem(cliente, mensagemAoCliente)

        else:
            mensagemAoCliente = op.fazMensagemServidor(f"erro | {resposta[1]}")
            print("[Servidor] Reportando erro de cadastro...")
            op.enviaMensagem(cliente, mensagemAoCliente)

        

'''
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
'''