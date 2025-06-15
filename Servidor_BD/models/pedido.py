import datetime
from models.persistivel import Persistivel
from models.anuncio import Anuncio
from models.endereco import Endereco

class Pedido(Persistivel):
    def __init__(self, id = 0, anuncio = None, quantidade = 0, endereco = None, data = None):
        # Atributos próprios
        self.id = id
        self.data = data
        self.quantidade = quantidade

        # Atributos estrangeiros
        self.anuncio = anuncio
        self.id_anuncio = anuncio.id if anuncio else 0
        self.endereco = endereco
        if endereco:
            self.id_endereco = endereco.id
            self.id_usuario = endereco.id_usuario
        else:
            self.id_endereco = 0
            self.id_usuario = 0

    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data if self.data else '',
            'anuncio': self.anuncio.to_dict() if self.anuncio else None,
            'quantidade': self.quantidade,
            'endereco': self.endereco.to_dict() if self.endereco else None,
        }
    
    def to_dict_personalisado(self):
        return {
            'anuncio': {'id': self.anuncio.id, 'nome': self.anuncio.nome} if self.anuncio else None,
            'quantidade': self.quantidade,
            'data': self.data if self.data else '',
            'endereco': {'id': self.endereco.id} if self.endereco else None
            }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        if self.quantidade == -1:
            #modo especial de confirmação == True
            obj_bd['confirmacao_pedido'] = True
            self.quantidade = 0
        elif self.quantidade == -2:
            #modo especial de confirmação == False
            obj_bd['confirmacao_pedido'] = False
            self.quantidade = 0
        
        atributos_bd = ('id_anuncio', 'id_endereco', 'id_usuario', 'quantidade', 'data')
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd
    
    def clone_zerado(self):
        return Pedido()

    @classmethod
    def from_dict(cls, dados):
        id = dados.get('id', 0)
        data = dados.get('data', None)
        anuncio = Anuncio.from_dict(dados['anuncio']) if 'anuncio' in dados else None
        quantidade = dados.get('quantidade', 0)
        endereco = Endereco.from_dict(dados['endereco']) if 'endereco' in dados else None

        return cls(id, anuncio, quantidade, endereco, data)
    
    def __str__(self):
        return f'Pedido(id={self.id}, data={self.data}, anuncio={self.anuncio}, quantidade={self.quantidade}, endereco={self.endereco})'