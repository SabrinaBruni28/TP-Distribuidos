import socket
import threading
from Operacoes import server_operation as op

class Pedido():
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexaoCliente = socket_cliente
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.camposMensagem[1]

        match operacao:
            case "confirmar":
                self.confirmar()

            case "cancelar":
                self.cancelar()

            case _:
                print("[Servidor] Mensagem inválida.")

    def confirmar(self):
        idPedido = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"pedido | confirmar | {idPedido}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def cancelar(self):
        idPedido = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = op.codifica(f"excluir | pedido | {idPedido}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)