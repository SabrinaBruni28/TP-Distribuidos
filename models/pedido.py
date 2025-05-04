import datetime

class Pedido:
    def __init__(self, id, produto, quantidade, preco, endereco, data = None):
        self.id = id
        self.data = data if data else datetime.datetime.now()
        self.produto = produto
        self.quantidade = quantidade
        self.preco = preco
        self.endereco = endereco

    def calcular_total(self):
        total = self.preco * self.quantidade
        return total
    