from models.endereco import Endereco
from models.pedido import Pedido
from models.loja import Loja
import json

class Usuario:
    def __init__(self):
        pass

class Usuario_Identificado(Usuario):
    def __init__(
            self, id: int = 0, nome: str = "", cpf: str = "", email: str = "", senha: str = "", 
            lojas: Loja = [], enderecos: Endereco = [], pedidos: Pedido = []
        ):
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
        for i, p in enumerate(self.enderecos):
            if p.id == endereco.id:
                self.enderecos[i] = novo_endereco
                return novo_endereco
        return False
    
    def editar_loja(self, loja, nova_loja):
        for i, p in enumerate(self.lojas):
            if p.id == loja.id:
                self.lojas[i] = nova_loja
                return nova_loja
        return False
    
    def editar_pedido(self, pedido, novo_pedido):
        for i, p in enumerate(self.pedidos):
            if p.id == pedido.id:
                self.pedidos[i] = novo_pedido
                return novo_pedido
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
        id = data.get("id", 0)
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