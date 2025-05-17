import datetime
from models.produto import Produto
from models.endereco import Endereco

class Pedido:
    def __init__(self, id = 0, produto: Produto = None, quantidade = 0, preco = 0, endereco: Endereco = None, data = None):
        self.id = id
        self.produto = produto
        self.quantidade = quantidade
        self.preco = preco
        self.endereco = endereco
        self.data = data if data else datetime.datetime.now()

    def calcular_total(self):
        total = self.preco * self.quantidade
        return total
    
    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data.isoformat() if self.data else "",
            "produto": self.produto.to_dict() if self.produto else None,
            "quantidade": self.quantidade,
            "preco": self.preco,
            "endereco": self.endereco.to_dict() if self.endereco else None,
        }
    
    def to_dict_personalisado(self):
        return {
            "data": self.data.isoformat() if self.data else datetime.datetime.now().isoformat(),
            "produto": "{" + f"id: {self.produto.id if self.produto else None}" +"}",
            "quantidade": self.quantidade,
            "preco": self.preco,
            "endereco": self.endereco.id if self.endereco else None,
        }
    
    @classmethod
    def from_dict(cls, data):
        id = data.get("id", 0)
        data = datetime.datetime.fromisoformat(data["data"]) if "data" in data else ""
        produto = Produto.from_dict(data["produto"]) if "produto" in data else []
        quantidade = data.get("quantidade", 0)
        preco = data.get("preco", 0)
        endereco = Endereco.from_dict(data["endereco"]) if "endereco" in data else []

        return cls(id, produto, quantidade, preco, endereco, data)
    
    def __str__(self):
        return f"Pedido(id={self.id}, data={self.data}, produto={self.produto.nome}, quantidade={self.quantidade}, preco={self.preco}, endereco={self.endereco})"