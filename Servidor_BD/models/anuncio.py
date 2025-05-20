from models.persistivel import Persistivel
from models.produto import Produto

class Anuncio(Persistivel):
    def __init__(self, id = 0, produto = None, preco = 0, quantidade_disponivel = 0, chave_pix = "", pausado = False):
        # Atributos próprios
        self.id = id
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.chave_pix = chave_pix
        self.pausado = pausado

        # Atributos estrangeiros
        self.produto = produto
        self.id_produto = produto.id if produto else 0

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
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ("id_produto", "preco", "quantidade_disponivel", "chave_pix", "pausado")
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd
    
    def clone_zerado(self):
        return Anuncio()
    
    @classmethod
    def from_dict(cls, dados):
        id = dados.get("id", 0)
        produto = Produto.from_dict(dados["produto"]) if "produto" in dados else None
        preco = dados.get("preco", 0)
        quantidade_disponivel = dados.get("quantidade_disponivel", 0)
        chave_pix = dados.get("chave_pix", "")
        pausado = dados.get("pausado", False)
        
        return cls(id, produto, preco, quantidade_disponivel, chave_pix, pausado)
    
    def __str__(self):
        return f"Anuncio(id={self.id}, produto={self.produto.__str__()}, preco={self.preco}, quantidade_disponivel={self.quantidade_disponivel}, chave_pix={self.chave_pix}, pausado={self.pausado})"
