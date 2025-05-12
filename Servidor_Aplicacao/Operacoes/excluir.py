import socket
import threading
from Operacoes import server_operation as op

class Excluir():
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexaoCliente = socket_cliente
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

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        idAnuncio = self.mensagemCliente.campoosMensagem[2]
        mensagemServidor = op.codificar(f"excluir | anuncio | {idAnuncio}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def produto(self):
        idProduto = self.mensagemCliente.campoosMensagem[2]
        mensagemServidor = op.codificar(f"excluir | produto | {idProduto}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def loja(self):
        idLoja = self.mensagemCliente.campoosMensagem[2]
        mensagemServidor = op.codificar(f"excluir | loja | {idLoja}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def endereco(self):
        idEndereco = self.mensagemCliente.campoosMensagem[2]
        mensagemServidor = op.codificar(f"excluir | endereco | {idEndereco}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)