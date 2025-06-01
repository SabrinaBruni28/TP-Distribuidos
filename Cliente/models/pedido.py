from models.endereco import Endereco
from models.produto import Produto
import datetime, json

class Pedido:
    def __init__(
            self, id: int = 0, quantidade: int = 0, preco: float = 0, data: str = None, 
            produto: Produto = None, endereco: Endereco = None
        ):
        self.id = id
        self.quantidade = quantidade
        self.preco = preco
        self.data = data if data else datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        self.produto = produto
        self.endereco = endereco

    def calcular_total(self):
        total = self.preco * self.quantidade
        return total
    
    def to_dict(self):
        return json.dumps({
            "id": self.id,
            "data": self.data if self.data else "",
            "produto": self.produto.to_dict() if self.produto else None,
            "quantidade": self.quantidade,
            "preco": self.preco,
            "endereco": self.endereco.to_dict() if self.endereco else None,
        })
    
    def to_dict_personalizado(self):
        return json.dumps({
            "data": self.data,
            "produto": {"id": f"{self.produto.id}", "loja": {"id": f"{self.produto.loja.id}"}} if self.produto and self.produto.loja else None,
            "quantidade": self.quantidade,
            "preco": self.preco,
            "endereco": {"id": f"{self.endereco.id}"} if self.endereco else None,
        })
    
    @classmethod
    def from_dict(cls, dados):
        if isinstance(dados, str):
            dados = json.loads(dados)
        id = dados.get("id", 0)
        data = dados.get("data", "")
        produto = Produto.from_dict(dados["produto"]) if "produto" in dados else []
        quantidade = dados.get("quantidade", 0)
        preco = dados.get("preco", 0)
        endereco = Endereco.from_dict(dados["endereco"]) if "endereco" in dados else []

        return cls(id, quantidade, preco, data, produto, endereco)

    def __str__(self):
        return f"Pedido(id={self.id}, data={self.data}, produto={self.produto.nome}, quantidade={self.quantidade}, preco={self.preco}, endereco={self.endereco})"