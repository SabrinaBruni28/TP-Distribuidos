import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem
from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2

class Criar(operacao.Operacao):
    def __init__(self, fila_mensagens: FilaDeMensagensV2):
        self.fila = fila_mensagens

    def anuncio(self):
        print("[Servidor][Criar] Operação de criar anúncio recebida.")
        reqID

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
        idUsuario = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | pedido | {idUsuario} | {dados}")

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