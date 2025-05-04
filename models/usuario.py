
class Usuario:
    def __init__(self):
        return
    
    def visualizar_produto(self):
        pass

    def visualizar_loja(self):
        pass

    def pesquisar_produto(self, texto: str):
        pass

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