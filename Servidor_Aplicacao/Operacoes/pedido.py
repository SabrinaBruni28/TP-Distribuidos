from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas import Mensagem

class Pedido(operacao.Operacao):
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def confirmar(self, id_pedido):
        print("[Servidor][Pedido][Confirmar] Operação de confirmar pedido recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Pedido][Confirmar] Enviando requisição para a fila...")
        self.fila.enfileira(f"confirmar_pedido", id_pedido, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)


    def cancelar(self, id_pedido):
        print("[Servidor][Pedido][Cancelar] Operação de cancelar pedido recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Pedido][Cancelar] Enviando requisição para a fila...")
        self.fila.enfileira(f"cancelar_pedido", id_pedido, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)