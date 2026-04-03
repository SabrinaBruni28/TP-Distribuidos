from models.persistivel import Persistivel
from models.endereco import Endereco
from models.pedido import Pedido
from models.loja import Loja

class Usuario():
    def __init__(self):
        return

class Usuario_Identificado(Persistivel, Usuario):
    def __init__(self, id = 0, nome = '', cpf = '', email = '', senha = '', lojas = [], enderecos = [], pedidos = []):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha

        self.lojas = lojas
        self.enderecos = enderecos
        self.pedidos = pedidos

    def criar_loja(self, loja):
        self.lojas.append(loja)
        return loja
    
    def criar_endereco(self, endereco):
        self.enderecos.append(endereco)
        return endereco
    
    def criar_pedido(self, pedido):
        self.pedidos.append(pedido)
        return pedido
    
    def editar_endereco(self, endereco, novo_endereco):
        if endereco in self.enderecos:
            index = self.enderecos.index(endereco)
            self.enderecos[index] = novo_endereco
            return True
        return False
    
    def editar_loja(self, loja, nova_loja):
        if loja in self.lojas:
            index = self.lojas.index(loja)
            self.lojas[index] = nova_loja
            return True
        return False
    
    def editar_pedido(self, pedido, novo_pedido):
        if pedido in self.pedidos:
            index = self.pedidos.index(pedido)
            self.pedidos[index] = novo_pedido
            return True
        return False
    
    def apagar_endereco(self, endereco):
        if endereco in self.enderecos:
            self.enderecos.remove(endereco)
            return True
        return False
    
    def apagar_loja(self, loja):
        if loja in self.lojas:
            self.lojas.remove(loja)
            return True
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cpf': self.cpf,
            'email': self.email,
            'senha': self.senha,
            'lojas': [loja.to_dict() for loja in self.lojas] if self.lojas else [],
            'enderecos': [endereco.to_dict() for endereco in self.enderecos] if self.enderecos else [],
            'pedidos': [pedido.to_dict() for pedido in self.pedidos] if self.pedidos else []
        } 

    def to_dict_personalisado(self):
        return {
            'nome': self.nome,
            'cpf': self.cpf,
            'email': self.email,
            'senha': self.senha,
        }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ('cpf', 'nome', 'email', 'senha')
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd
    
    def clone_zerado(self):
        return Usuario_Identificado()

    @classmethod
    def from_dict(cls, dados):
        id = dados.get('id', 0)
        nome = dados.get('nome', '')
        cpf = dados.get('cpf', '')
        email = dados.get('email', '')
        senha = dados.get('senha', '')
        lojas = [Loja.from_dict(loja) for loja in dados['lojas']] if 'lojas' in dados else []
        enderecos = [Endereco.from_dict(endereco) for endereco in dados['enderecos']] if 'enderecos' in dados else []
        pedidos = [Pedido.from_dict(pedido) for pedido in dados['pedidos']] if 'pedidos' in dados else []

        return cls(id, nome, cpf, email, senha, lojas, enderecos, pedidos)
    
    def __str__(self):
        return f'Usuario(id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, senha={self.senha})'