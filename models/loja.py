from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido

class Loja:
    def __init__(self, id = 0, nome = "", imagem = "", produtos: Produto = [], anuncios = [], pedidos_confirmados = [], pedidos_em_andamento = []):
        self.id = id
        self.nome = nome
        self.imagem = imagem

        self.produtos = produtos
            
        self.anuncios = anuncios
        self.pedidos_confirmados = pedidos_confirmados
        self.pedidos_em_andamento = pedidos_em_andamento

    def criar_produto(self, produto):
        self.produtos.append(produto)
        return produto
    
    def criar_anuncio(self, anuncio):
        self.anuncios.append(anuncio)
        return anuncio
    
    def criar_pedido(self, pedido):
        self.pedidos_confirmados.append(pedido)
        return pedido
    
    def apagar_produto(self, produto):
        if produto in self.produtos:
            self.produtos.remove(produto)
            return True
        return False
    
    def apagar_anuncio(self, anuncio):
        if anuncio in self.anuncios:
            self.anuncios.remove(anuncio)
            return True
        return False
    
    def editar_produto(self, produto, novo_produto):
        if produto in self.produtos:
            index = self.produtos.index(produto)
            self.produtos[index] = novo_produto
            return True
        return False
    
    def editar_anuncio(self, anuncio, novo_anuncio):
        if anuncio in self.anuncios:
            index = self.anuncios.index(anuncio)
            self.anuncios[index] = novo_anuncio
            return True
        return False
    
    def confirmar_pedido(self, id_pedido):
        for pedido in self.pedidos_em_andamento:
            if pedido.id == id_pedido:
                self.pedidos_confirmados.append(pedido)
                self.pedidos_em_andamento.remove(pedido)
                return True
        return False
    
    def cancelar_pedido(self, id_pedido):
        for pedido in self.pedidos_em_andamento:
            if pedido.id == id_pedido:
                self.pedidos_em_andamento.remove(pedido)
                return True
        return False
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "imagem": self.imagem,
            "produtos": [produto.nome for produto in self.produtos] if self.produtos else [],
            "anuncios": [anuncio.produto.nome for anuncio in self.anuncios] if self.anuncios else [],
            "pedidos_confirmados": [pedido.to_dict() for pedido in self.pedidos_confirmados] if self.pedidos_confirmados else [],
            "pedidos_em_andamento": [pedido.to_dict() for pedido in self.pedidos_em_andamento] if self.pedidos_em_andamento else [],
        }  
    
    def to_dict_personalisado(self):
        return {
            "nome": self.nome,
            "imagem": self.imagem if self.imagem else "",
        } 
    
    @classmethod
    def from_dict(cls, data):
        id = data.get("id", 0)
        nome = data.get("nome", "")
        imagem = data.get("imagem", "")
        produtos = [Produto.from_dict(produto) for produto in data["produtos"]] if "produtos" in data else []
        anuncios = [Anuncio.from_dict(anuncio) for anuncio in data["anuncios"]] if "anuncios" in data else []
        pedidos_confirmados = [Pedido.from_dict(pedido) for pedido in data["pedidos_confirmados"]] if "pedidos_confirmados" in data else []
        pedidos_em_andamento = [Pedido.from_dict(pedido) for pedido in data["pedidos_em_andamento"]] if "pedidos_em_andamento" in data else []

        return cls(id, nome, imagem, produtos, anuncios, pedidos_confirmados, pedidos_em_andamento)
    
    def __str__(self):
        return f"Loja(id={self.id}, nome={self.nome}, imagem={self.imagem})"