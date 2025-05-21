
from models.persistivel import Persistivel


class Endereco(Persistivel):
    def __init__(self, id = 0, rua = '', numero = '', complemento = '', bairro = '', cidade = '', estado = '', id_usuario = 0):
        # Atributos próprios
        self.id = id
        self.rua = rua
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado

        # Atributos estrangeiros
        self.id_usuario = id_usuario

    def to_dict(self):
        return {
            'id': self.id,
            'rua': self.rua,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado
        }
    
    def to_dict_personalisado(self):
        return {
            'rua': self.rua,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado
        }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ('id_usuario', 'rua', 'numero', 'bairro', 'cidade', 'estado', 'complemento')
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd

    def clone_zerado(self):
        return Endereco()
    
    @classmethod
    def from_dict(cls, dados):
        id = dados.get('id', 0)
        rua = dados.get('rua', '')
        numero = dados.get('numero', 0)
        complemento = dados.get('complemento', '')
        bairro = dados.get('bairro', '')
        cidade = dados.get('cidade', '')
        estado = dados.get('estado', '')

        return cls(id, rua, numero, complemento, bairro, cidade, estado)

    def __str__(self):
        return f'Endereco(id={self.id}, rua={self.rua}, numero={self.numero}, complemento={self.complemento}, bairro={self.bairro}, cidade={self.cidade}, estado={self.estado})'


