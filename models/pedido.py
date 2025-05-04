import datetime
from models.produto import Produto
from models.endereco import Endereco

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
    
    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data.isoformat(),
            "produto": self.produto.to_dict(),
            "quantidade": self.quantidade,
            "preco": self.preco,
            "endereco": self.endereco.to_dict()
        }
    
    def from_dict(self, data):
        self.id = data.get("id", 0)
        self.data = datetime.datetime.fromisoformat(data["data"])
        self.produto = Produto.from_dict(data["produto"]) if "produto" in data else []
        self.quantidade = data["quantidade"]
        self.preco = data["preco"]
        self.endereco = Endereco.from_dict(data["endereco"]) if "endereco" in data else []
    