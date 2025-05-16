import socket
import threading
from Operacoes import server_operation as op
from Operacoes import operacao
from Operacoes import callback
from Estruturas.mensagem import Mensagem
#from Estruturas.fila_de_mensagens import FilaDeMensagens

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
        print("[Servidor][Login] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, callback.loginCallback, self.conexaoCliente, "login")