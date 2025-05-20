import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas import Mensagem

class Excluir(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)

    def run(self):
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

            case "endereco":
                self.endereco()

            case "imagem":
                self.imagem()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        print("[Servidor][Excluir] Operação de excluir anúncio recebida.")
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"excluir | anuncio | {idAnuncio}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.excluirAnuncioCallback, self.conexaoCliente, "excluir")

    def produto(self):
        print("[Servidor][Excluir] Operação de excluir anúncio recebida.")
        idProduto = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"excluir | produto | {idProduto}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.excluirProdutoCallback, self.conexaoCliente, "excluir")

    def loja(self):
        print("[Servidor][Excluir] Operação de excluir anúncio recebida.")
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"excluir | loja | {idLoja}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.excluirLojaCallback, self.conexaoCliente, "excluir")

    def endereco(self):
        print("[Servidor][Excluir] Operação de excluir anúncio recebida.")
        idEndereco = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"excluir | endereco | {idEndereco}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.excluirEnderecoCallback, self.conexaoCliente, "excluir")

    def imagem(self):
        print("[Servidor][Excluir] Operação de excluir anúncio recebida.")
        nomeImagem = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"excluir | imagem | {nomeImagem}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.excluirImagemCallback, self.conexaoCliente, "excluir")
