

class Produto:
    def __init__(self, nome, descricao, imagens, loja):
        self.id = 0
        self.nome = nome
        self.descricao = descricao
        self.imagens = imagens
        self.loja = loja

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "imagens": self.imagens,
            "loja": self.loja.to_dict()
        }
    
    def from_dict(self, data):
        from models.loja import Loja
        self.id = data.get("id", 0)
        self.nome = data["nome"]
        self.descricao = data["descricao"]
        self.imagens = data["imagens"]
        self.loja = Loja.from_dict(data["loja"]) if "loja" in data else []