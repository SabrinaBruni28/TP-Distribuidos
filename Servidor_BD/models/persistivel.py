
class Persistivel:
    def __init__(self, id = 0):
        self.id = id

    def to_dict(self):
        pass

    def to_dict_personalisado(self):
        return self.__dict__

    def to_dict_bd(self, nome_colunas):
        return {}

    def clone_zerado(self):
        return Persistivel()
    
    @classmethod
    def from_dict(cls, dados):
        pass
    