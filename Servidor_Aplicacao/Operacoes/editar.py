import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

class Editar(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens, imagens: list =None):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        self.conexaoServidor = socket_servidor
        self.imagem = imagens

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

            case "usuario":
                self.usuario()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        print("[Servidor][Editar] Operação de editar anúncio recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | anuncio | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.editarAnuncioCallback, self.conexaoCliente, "editar")

    def produto(self):
        print("[Servidor][Editar] Operação de editar produto recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | anuncio | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.editarProdutoCallback, self.conexaoCliente, "editar")

    def loja(self):
        print("[Servidor][Editar] Operação de editar loja recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | loja | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.editarProdutoCallback, self.conexaoCliente, "editar", imagem=self.imagem)

    def endereco(self):
        print("[Servidor][Editar] Operação de editar endereço recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | endereco | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.editarEnderecoCallback, self.conexaoCliente, "editar")

    def usuario(self):
        print("[Servidor][Editar] Operação de editar usuário recebida.")
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | usuario | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.editarUsuarioCallback, self.conexaoCliente, "editar")