import socket
import threading
import json
from Operacoes import thread_email as correio
from Operacoes import server_operation as op
from Operacoes import thread_email as correio
from Operacoes import operacao
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
#from Estruturas.fila_de_mensagens import FilaDeMensagens

class Cadastramento(operacao.Operacao):
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def cadastrar(self, dados):
        print("[Servidor][Cadastramento] Operação de Cadastramento recebida.")

        reqID = op.gerarID()
        requisicao = f"cadastramento"

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Cadastramento] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao, dados, reqID)
        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)