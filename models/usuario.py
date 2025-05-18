from models.endereco import Endereco
from models.pedido import Pedido
from models.loja import Loja
from typing import Optional
import json

class Usuario:
    def __init__(self):
        pass

class Usuario_Identificado(Usuario):
    def __init__(
            self, id = 0, nome = "", cpf = "", email = "", senha = "", 
            lojas: Optional[list[Loja]] = None, 
            enderecos: Optional[list[Endereco]] = None, 
            pedidos: Optional[list[Pedido]] = None
        ):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha

        self.lojas = lojas if lojas is not None else []
        self.enderecos = enderecos if enderecos is not None else []
        self.pedidos = pedidos if pedidos is not None else []

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
    
    def get_endereco(self, endereco: str) -> Endereco:
        for end in self.enderecos:
            string = end.__str__() 
            if string == endereco:
                return end
        return None
    
    def to_dict(self):
        return json.dumps({
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "senha": self.senha,
            "lojas": [loja.to_dict() for loja in self.lojas] if self.lojas else [],
            "enderecos": [endereco.to_dict() for endereco in self.enderecos] if self.enderecos else [],
            "pedidos": [pedido.to_dict() for pedido in self.pedidos] if self.pedidos else []
        })

    def to_dict_cadastramento(self):
        return json.dumps({
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "senha": self.senha,
        })
    
    def to_dict_login(self):
        return json.dumps({
            "email": self.email,
            "senha": self.senha,
        })
    
    @classmethod
    def from_dict(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        id = data.get("id_usuario", 0)
        nome = data.get("nome", "")
        cpf = data.get("cpf", "")
        email = data.get("email", "")
        senha = data.get("senha", "")
        lojas = [Loja.from_dict(loja) for loja in data["lojas"]] if "lojas" in data else []
        enderecos = [Endereco.from_dict(endereco) for endereco in data["enderecos"]] if "enderecos" in data else []
        pedidos = [Pedido.from_dict(pedido) for pedido in data["pedidos"]] if "pedidos" in data else []

        return cls(id, nome, cpf, email, senha, lojas, enderecos, pedidos)
    
    def __str__(self):
        return f"Usuario(id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, senha={self.senha})"