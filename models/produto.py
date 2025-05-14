

class Produto:
    def __init__(self, id = 0, nome = "", descricao = "", imagens = [], loja = None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.imagens = imagens
        self.loja = loja

    def criar_imagem(self, imagem):
        self.imagens.append(imagem)
        return imagem

    def apagar_imagem(self, imagem):
        if imagem in self.imagens:
            self.imagens.remove(imagem)
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "imagens": self.imagens,
            "loja": self.loja.to_dict() if self.loja else None,
        }
    
    def to_dict_personalisado(self):
        return {
            "nome": self.nome,
            "descricao": self.descricao,
            "imagens": self.imagens,
            "loja": "{" + f"id: {self.loja.id if self.loja else None}" +"}",
        }
    
    @classmethod
    def from_dict(cls, data):
        from models.loja import Loja
        id = data.get("id", 0)
        nome = data.get("nome", "")
        descricao = data.get("descricao", "")
        imagens = data.get("imagens", [])
        loja = Loja.from_dict(data["loja"]) if "loja" in data else None

        return cls(id, nome, descricao, imagens, loja)

    def __str__(self):
        return f"Produto(id={self.id}, nome={self.nome}, descricao={self.descricao}, imagens={self.imagens}, loja={self.loja.__str__()})"