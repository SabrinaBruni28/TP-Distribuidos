from Estruturas.requisicao import Requisicao

class Cadastramento():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def cadastrar(self, dados):
        print("[Servidor][Cadastramento] Operação de Cadastramento recebida.")

        requisicao = Requisicao.produzRequisicao("cadastramento", dados)

        self.fila.registraRequisicao(requisicao.idRequisicao)

        print(f"[Servidor][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)