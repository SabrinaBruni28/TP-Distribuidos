
class Endereco:
    def __init__(self, id = 0, rua = "", numero = "", complemento = "", bairro = "", cidade = "", estado = ""):
        self.id = id
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado

    def to_dict(self):
        return {
            "id": self.id,
            "rua": self.rua,
            "numero": self.numero,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado
        }
    
    def to_dict_personalisado(self):
        return {
            "rua": self.rua,
            "numero": self.numero,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado
        }
    
    @classmethod
    def from_dict(cls, data):
        rua = data.get("rua", "")
        numero = data.get("numero", 0)
        complemento = data.get("complemento", "")
        bairro = data.get("bairro", "")
        cidade = data.get("cidade", "")
        estado = data.get("estado", "")

        return cls(rua, numero, complemento, bairro, cidade, estado)

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.bairro}, {self.cidade} - {self.estado}, {self.complemento}"


