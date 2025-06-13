from Operacoes import server_operation as op
from Estruturas.requisicao import Requisicao
from Estruturas.fila_de_requisicoes import FilaDeRequisicoes

class Imagem():
    def __init__(self, fila_requisicoes: FilaDeRequisicoes):
        self.fila = fila_requisicoes

    def anuncio(self, id_anuncio):
        print(f"[Servidor][Imagem][Anúncio] Requisição para receber imagens de um anúncio recebida.")
        requisicao = Requisicao.produzRequisicao("imagens_anuncio", id_anuncio)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Anuncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagens de um anúncio.")

        self.fila.registraRequisicao(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)