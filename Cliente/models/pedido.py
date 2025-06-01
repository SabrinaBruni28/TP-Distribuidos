from models.endereco import Endereco
from models.anuncio import Anuncio
import datetime, json

class Pedido:
    def __init__(
            self, id: int = 0, quantidade: int = 0, data: str = None, 
            anuncio: Anuncio = None, endereco: Endereco = None
        ):
        self.id = id
        self.quantidade = quantidade
        self.data = data if data else datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        self.anuncio = anuncio
        self.endereco = endereco

    def calcular_total(self):
        total = self.anuncio.preco * self.quantidade
        return total
    
    def to_dict(self):
        return json.dumps({
            "id": self.id,
            "data": self.data if self.data else "",
            "anuncio": self.anuncio.to_dict() if self.anuncio else None,
            "quantidade": self.quantidade,
            "endereco": self.endereco.to_dict() if self.endereco else None,
        })
    
    def to_dict_personalizado(self):
        return json.dumps({
            "data": self.data,
            "anuncio": {"id": f"{self.anuncio.id}"} if self.anuncio else None,
            "quantidade": self.quantidade,
            "endereco": {"id": f"{self.endereco.id}"} if self.endereco else None,
        })
    
    @classmethod
    def from_dict(cls, dados):
        if isinstance(dados, str):
            dados = json.loads(dados)
        id = dados.get("id", 0)
        data = dados.get("data", "")
        anuncio = Anuncio.from_dict(dados["anuncio"]) if "anuncio" in dados else []
        quantidade = dados.get("quantidade", 0)
        endereco = Endereco.from_dict(dados["endereco"]) if "endereco" in dados else []

        return cls(id, quantidade, data, anuncio, endereco)

    def __str__(self):
        return f"Pedido(id={self.id}, data={self.data}, anuncio={self.anuncio}, quantidade={self.quantidade}, endereco={self.endereco})"