from models.produto import Produto

class Anuncio:
    def __init__(self, id = 0, produto: Produto = None, preco = 0, quantidade_disponivel = 0, chave_pix = "", pausado = False):
        self.id = id 
        self.produto = produto
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.chave_pix = chave_pix
        self.pausado = pausado
        
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
        return {
            "id": self.id,
            "produto": self.produto.to_dict() if self.produto else None,
            "preco": self.preco,
            "quantidade_disponivel": self.quantidade_disponivel,
            "chave_pix": self.chave_pix,
            "pausado": self.pausado
        }
    
    def to_dict_personalisado(self):
        return {
            "produto": "{" + f"id: {self.produto.id if self.produto else None}" +"}",
            "preco": self.preco,
            "quantidade_disponivel": self.quantidade_disponivel,
            "chave_pix": self.chave_pix,
            "pausado": self.pausado
        }
    
    @classmethod
    def from_dict(cls, data):
        id = data.get("id", 0)
        produto = Produto.from_dict(data["produto"]) if "produto" in data else None
        preco = data.get("preco", 0)
        quantidade_disponivel = data.get("quantidade_disponivel", 0)
        chave_pix = data.get("chave_pix", "")
        pausado = data.get("pausado", False)
        
        return cls(id, produto, preco, quantidade_disponivel, chave_pix, pausado)
    
    def __str__(self):
        return f"Anuncio(id={self.id}, produto={self.produto.__str__()}, preco={self.preco}, quantidade_disponivel={self.quantidade_disponivel}, chave_pix={self.chave_pix}, pausado={self.pausado})"
