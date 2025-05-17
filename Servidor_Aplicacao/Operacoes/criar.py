import socket
import threading
from Operacoes import server_operation as op
from Operacoes import operacao
from Estruturas import Mensagem

class Criar(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens, imagens: list = None):
        super().__init__(mensagem, socket_cliente, fila_mensagens, imagens)

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

            case "pedido":
                self.pedido()

            case "endereco":
                self.endereco()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"criar | anuncio | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def produto(self):
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"criar | produto | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente, tipo="produto", imagem=self.imagens)

    def loja(self):
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"criar | loja | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def pedido(self):
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"criar | pedido | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def endereco(self):
        dados = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"criar | endereco | " + str(dados))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)