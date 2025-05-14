import socket
import threading
from Operacoes import server_operation as op
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

class Login(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.logar()

    def logar(self):
        dados = self.mensagemCliente.camposMensagem[1]
        mensagemServidor = Mensagem.produtorMensagem(f"login | {dados}")

        # A operação de Login enfileira, efetivamente, apenas a mensagem e o socket do cliente além do callback.
        # A operação de login é simples e não há "discussão" entre o servidor e o banco de dados.
        print("[Servidor] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, self.loginCallback, self.conexaoCliente, "login")
    
    @staticmethod
    def loginCallback(respostaBD, socket_cliente):
        resposta = [ws.strip() for ws in respostaBD.split('|')]
        print(resposta)

        if resposta[0] == "ok":
            mensagemAoCliente = Mensagem.produtorMensagem(f"ok | {resposta[1]}")

            print("[Servidor] Confirmando login do cliente...")
            op.enviaMensagem(socket_cliente, mensagemAoCliente)

        else:
            mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta[1]}")
        
            print("[Servidor] Reportando erro de login ao cliente...")
            op.enviaMensagem(socket_cliente, mensagemAoCliente)