from models.endereco import Endereco
from models.pedido import Pedido
from models.loja import Loja

class Usuario:
    def __init__(self):
        return

class Usuario_Identificado(Usuario):
    def __init__(self, nome, cpf, email, senha):
        self.id_usuario = 0
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha

        self.lojas = []
        self.enderecos = []
        self.pedidos = []

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
            "id_usuario": self.id_usuario,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "senha": self.senha,
            "lojas": [loja.to_dict() for loja in self.lojas],
            "enderecos": [endereco.to_dict() for endereco in self.enderecos],
            "pedidos": [pedido.to_dict() for pedido in self.pedidos]
        }  
    
    def from_dict(self, data):
        self.id_usuario = data.get("id_usuario", 0)
        self.nome = data["nome"]
        self.cpf = data["cpf"]
        self.email = data["email"]
        self.senha = data["senha"]
        self.lojas = [Loja.from_dict(loja) for loja in data["lojas"]] if "lojas" in data else []
        self.enderecos = [Endereco.from_dict(endereco) for endereco in data["enderecos"]] if "enderecos" in data else []
        self.pedidos = [Pedido.from_dict(pedido) for pedido in data["pedidos"]] if "pedidos" in data else []
    
