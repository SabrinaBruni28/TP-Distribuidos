from models.produto import Produto

class Anuncio:
    def __init__(self, produto: Produto, preco, quantidade_disponivel, chave_pix):
        self.id = 0
        self.produto = produto
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.chave_pix = chave_pix
        self.pausado = False

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
            "produto": self.produto.to_dict(),
            "preco": self.preco,
            "quantidade_disponivel": self.quantidade_disponivel,
            "chave_pix": self.chave_pix,
            "pausado": self.pausado
        }
    
    def from_dict(self, data):
        self.id = data.get("id", 0)
        self.produto = Produto.from_dict(data["produto"]) if "produto" in data else []
        self.preco = data["preco"]
        self.quantidade_disponivel = data["quantidade_disponivel"]
        self.chave_pix = data["chave_pix"]
        self.pausado = data.get("pausado", False)
