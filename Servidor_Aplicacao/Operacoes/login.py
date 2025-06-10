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
    def __init__(self, fila_mensagens: FilaDeMensagensV2):
        self.fila = fila_mensagens

    def run(self):
        return self.getOperacao()

    def getOperacao(self):
        return self.logar()

    def logar(self, dados):        
        print("[Servidor][Login] Operação de Login recebida.")

        # Gero um ID para a requisição do cliente
        reqID = op.gerarID()
        requisicao = f"login"

        # Registro a requisição -com seu ID- 
        self.fila.registraRequisicao(reqID)

        # Coloco essa requisição do Servidor na Fila de Requisições para ela ser enviada ao banco
        # quando este estiver livre.
        print(f"[Servidor][Login] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao, dados, reqID)

        # Espero a resposta do Banco de Dados para retornar ao cliente
        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)