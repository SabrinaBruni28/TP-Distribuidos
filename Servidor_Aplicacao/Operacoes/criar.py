import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas import Mensagem

class Criar(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens, imagens: list = None):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        self.imagens = imagens

    def run(self):
        print("[Servidor][Criar] Operação de criar recebida.")
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.camposMensagem[1]

        match operacao:
            case "anuncio":
                self.anuncio()

            case "produto":
                self.produto()

            case "loja":
                self.loja()

            case "pedido":
                self.pedido()

            case "endereco":
                self.endereco()

            case "imagem":
                self.imagem()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | anuncio | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarAnuncioCallback, self.conexaoCliente, "criar")

    def produto(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | produto | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarProdutoCallback, self.conexaoCliente,"criar", imagem=self.imagens)

    def loja(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        idLoja = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | loja | {idLoja} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarLojaCallback, self.conexaoCliente, "criar", imagem=self.imagens)

    def pedido(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | pedido | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarPedidoCallback, self.conexaoCliente, "criar")

    def endereco(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[3]
        idUsusario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | endereco | {idUsusario} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarEnderecoCallback, self.conexaoCliente, "criar")

    def imagem(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | imagem | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.criarImagemCallback, self.conexaoCliente, "criar", imagem=self.imagens)