from Operacoes import thread_email as correio
from Operacoes import server_operation as op
from Estruturas.requisicao import Requisicao


class Cadastramento():
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def cadastrar(self, dados):
        print("[Servidor][Cadastramento] Operação de Cadastramento recebida.")

        requisicao = Requisicao.produzRequisicao("cadastramento", dados)

        self.fila.registraRequisicao(requisicao.idRequisicao)

        print(f"[Servidor][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)
        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)