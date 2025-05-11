import socket
import threading
from Operacoes import server_operation as op

class Visualizar():
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexao = socket_cliente
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        if self.mensagemCliente.tamanho < 3:
            self.todosAnuncios()

        else:
            self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.camposMensagem[1]

        match operacao:
            case "anuncio":
                self.anuncio()

            case "loja":
                self.loja()

            case "minha_loja":
                self.minhaLoja()

            case "minhas_lojas":
                self.minhasListaLojas()

            case "pedidos":
                self.pedidos()

            case "meus_pedidos":
                self.meusPedidos()
            
            case _:
                print("[Servidor] Mensagem inválida.")

    def todosAnuncios(self):
        mensagemServidor = op.codifica("retornar | anuncios")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def anuncio(self):
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | anuncio |" + str(idAnuncio))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def loja(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def minhaLoja(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | minha_loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def minhasListaLojas(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | minhas_lojas | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def pedidos(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | pedido | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)

    def meusPedidos(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica("retornar | meus_pedidos | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexao)