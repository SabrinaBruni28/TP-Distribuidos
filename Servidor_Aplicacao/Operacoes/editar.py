import socket
import threading
from Operacoes import server_operation as op

class Editar():
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens)
        self.mensagemCliente = mensagem
        self.conexaoCliente = socket_cliente
        self.conexaoServidor = socket_servidor
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.campoosMensagem[1]

        match operacao:
            case "anuncio":
                self.anuncio()

            case "produto":
                self.produto()

            case "loja":
                self.loja()

            case "endereco":
                self.endereco()

            case "usuario":
                self.usuario()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | anuncio | {idAnuncio} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def produto(self):
        idProduto = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | anuncio | {idProduto} | {dados}")