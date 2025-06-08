import socket
import threading
import uuid
from Operacoes import server_operation as op
from Operacoes import operacao
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2

#from Estruturas.fila_de_mensagens import FilaDeMensagens

class Login():
    def __init__(self, mensagem, fila_mensagens: FilaDeMensagensV2):
        self.mensagem = mensagem
        self.fila = fila_mensagens

    def run(self):
        return self.getOperacao()

    def getOperacao(self):
        return self.logar()

    # TODO: Expor essa função pro Pyro
    def logar(self, dados):
        
        print("[Servidor][Login] Operação de Login recebida.")

        # Agora as coisas ficaram bem diferentes.
        # Quando o cliente invocar a operação de logar, ele quer o retorno do banco de dados
        # Assim, a primeira coisa que temos de fazer e enfileirar essa requisição junto a um ID

        reqID = op.gerarID()
        requisicao = f"login"

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Login] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao, dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)