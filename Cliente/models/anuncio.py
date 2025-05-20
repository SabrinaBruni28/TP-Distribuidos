from models.produto import Produto
import json

class Anuncio:
    def __init__(
            self, id: int = 0, preco: float = 0, quantidade_disponivel: int = 0, 
            chave_pix:str = "", pausado: bool = False, produto: Produto = None
        ):
        self.id = id 
        self.preco = preco
        self.quantidade_disponivel = int(quantidade_disponivel)
        self.chave_pix = chave_pix
        self.pausado = pausado
        self.produto = produto
        
        if self.quantidade_disponivel <= 0:
            self.pausar()

    def subtrair_quantidade(self, quantidade):
        if self.pausado:
            return 0
        if quantidade > self.quantidade_disponivel:
            raise ValueError("Quantidade solicitada maior que a disponível.")
        
        self.quantidade_disponivel -= quantidade
        if self.quantidade_disponivel == 0:
            self.pausar()
        return self.quantidade_disponivel

    def pausar(self):
        self.pausado = True

    def ativar(self):
        self.pausado = False

    def to_dict(self):
        return json.dumps({
            "id": self.id,
            "produto": self.produto.to_dict() if self.produto else None,
            "preco": self.preco,
            "quantidade_disponivel": self.quantidade_disponivel,
            "chave_pix": self.chave_pix,
            "pausado": self.pausado
        })
    
    def to_dict_personalizado(self):
        return json.dumps({
            "produto": {"id": f"{self.produto.id if self.produto else None}"},
            "preco": self.preco,
            "quantidade_disponivel": self.quantidade_disponivel,
            "chave_pix": self.chave_pix,
            "pausado": self.pausado
        })
    
    @classmethod
    def from_dict(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        id = data.get("id", 0)
        produto = Produto.from_dict(data["produto"]) if "produto" in data else None
        preco = data.get("preco", 0)
        quantidade_disponivel = data.get("quantidade_disponivel", 0)
        chave_pix = data.get("chave_pix", "")
        pausado = data.get("pausado", False)
        
        return cls(id, preco, quantidade_disponivel, chave_pix, pausado, produto)
    
    def __str__(self):
        return f"Anuncio(id={self.id}, produto={self.produto.__str__()}, preco={self.preco}, quantidade_disponivel={self.quantidade_disponivel}, chave_pix={self.chave_pix}, pausado={self.pausado})"
