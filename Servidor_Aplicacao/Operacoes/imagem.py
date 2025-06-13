from Estruturas.requisicao import Requisicao

class Imagem():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def produto(self, nome_imagem):
        print(f"[Servidor][Imagem][Produto] Requisição para receber a imagem de um produto recebida.")
        requisicao = Requisicao.produzRequisicao("imagem_produto", nome_imagem)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagem de um produto: {nome_imagem[:15]}..{nome_imagem[-3:]}.")

        self.fila.registraRequisicao(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def loja(self, nome_imagem):
        print(f"[Servidor][Imagem][Loja] Requisição para receber a imagem de uma loja recebida.")
        requisicao = Requisicao.produzRequisicao("imagem_loja", nome_imagem)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagem de uma loja: {nome_imagem[:15]}..{nome_imagem[-3:]}.")

        self.fila.registraRequisicao(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)