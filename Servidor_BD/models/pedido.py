import datetime
from models.persistivel import Persistivel
from models.produto import Produto
from models.endereco import Endereco

class Pedido(Persistivel):
    def __init__(self, id = 0, produto = None, quantidade = 0, preco = 0, endereco = None, data = None):
        # Atributos próprios
        self.id = id
        self.data = data
        self.quantidade = quantidade
        self.preco = preco

        # Atributos estrangeiros
        self.produto = produto
        self.id_produto = produto.id if produto else 0
        self.endereco = endereco
        self.id_endereco = endereco.id if endereco else 0

    def calcular_total(self):
        total = self.preco * self.quantidade
        return total
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else '',
            'produto': self.produto.to_dict() if self.produto else None,
            'quantidade': self.quantidade,
            'preco': self.preco,
            'endereco': self.endereco.to_dict() if self.endereco else None,
        }
    
    def to_dict_personalisado(self):
        return {
            'produto': {'id': self.produto.id, 'nome': self.produto.nome} if self.produto else None,
            'preco': self.preco,
            'quantidade': self.quantidade,
            'data': self.data.isoformat() if self.data else ''
            }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ('id_produto', 'id_endereco', 'quantidade', 'preco', 'data_pedido')
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
        data = datetime.datetime.fromisoformat(dados['data']) if 'data' in dados else None
        produto = Produto.from_dict(dados['produto']) if 'produto' in dados else None
        quantidade = dados.get('quantidade', 0)
        preco = dados.get('preco', 0)
        endereco = Endereco.from_dict(dados['endereco']) if 'endereco' in dados else None

        return cls(id, produto, quantidade, preco, endereco, data)
    
    def __str__(self):
        return f'Pedido(id={self.id}, data={self.data}, produto={self.produto}, quantidade={self.quantidade}, preco={self.preco}, endereco={self.endereco})'