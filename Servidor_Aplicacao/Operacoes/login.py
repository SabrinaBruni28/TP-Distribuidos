import socket
import threading
import uuid
from Operacoes import server_operation as op
from Operacoes import operacao
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
#from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2
#from Estruturas.fila_de_mensagens import FilaDeMensagens

class Login(operacao.Operacao):
    def __init__(self, mensagem, fila_mensagens):
        super().__init__(mensagem, fila_mensagens)

    def run(self):
        return self.getOperacao()

    def getOperacao(self):
        return self.logar()

    def logar(self):
        print("[Servidor][Login] Operação de Login recebida.")

        # Agora as coisas ficaram bem diferentes.
        # Quando o cliente invocar a operação de logar, ele quer o retorno do banco de dados
        # Assim, a primeira coisa que temos de fazer e enfileirar essa requisição junto a um ID
        





        dados = self.mensagemCliente.camposMensagem[1]
        mensagemServidor = Mensagem.produtorMensagem(f"login | {dados}")

        # A operação de Login enfileira, efetivamente, apenas a mensagem e o socket do cliente além do callback.
        # A operação de login é simples e não há "discussão" entre o servidor e o banco de dados.
        # Tamnbém não há envio de imagens.
        print("[Servidor][Login] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, cb.loginCallback, self.conexaoCliente, tipo="login")