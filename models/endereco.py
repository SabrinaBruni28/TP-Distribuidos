
class Endereco:
    def __init__(self, rua, numero, complemento, bairro, cidade, estado):
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado

    def to_dict(self):
        return {
            "rua": self.rua,
            "numero": self.numero,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado
        }
    
    def from_dict(self, data):
        self.rua = data["rua"]
        self.numero = data["numero"]
        self.complemento = data["complemento"]
        self.bairro = data["bairro"]
        self.cidade = data["cidade"]
        self.estado = data["estado"]


