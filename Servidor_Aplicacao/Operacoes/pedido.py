from Operacoes import server_operation as op
from ..Estruturas.requisicao import Requisicao

class Pedido():
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def confirmar(self, id_pedido):
        print("[Servidor][Pedido][Confirmar] Operação de confirmar pedido recebida.")
        requisicao = Requisicao.produzRequisicao("confirmar_pedido", id_pedido)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Pedido][Confirmar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)


    def cancelar(self, id_pedido):
        print("[Servidor][Pedido][Cancelar] Operação de cancelar pedido recebida.")
        requisicao = Requisicao.produzRequisicao("cancelar_pedido", id_pedido)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Pedido][Cancelar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)