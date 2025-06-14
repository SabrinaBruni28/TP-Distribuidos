from Estruturas.requisicao import Requisicao

class Imagem():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def produto(self, nome_imagem):
        print(f"[Servidor][Imagem][Produto] Requisição para receber a imagem de um produto recebida.")
        requisicao = Requisicao.produzRequisicao("imagens_produto", dados= nome_imagem)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagem de um produto: {nome_imagem[-10:]}.")

        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def loja(self, nome_imagem):
        print(f"[Servidor][Imagem][Loja] Requisição para receber a imagem de uma loja recebida.")
        requisicao = Requisicao.produzRequisicao("imagens_loja", dados= nome_imagem)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagem de uma loja: {nome_imagem[-10:]}.")

        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def pedido(self, nome_imagem):
        print(f"[Servidor][Imagem][Pedido] Requisição para receber a imagem de um pedido recebida.")
        requisicao = Requisicao.produzRequisicao("imagens_pedido", dados= nome_imagem)

        self.fila.registraRequisicao(requisicao)
        print(f"[Servidor][Imagem][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Pedindo imagem de um pedido: {nome_imagem[-10:]}.")

        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)