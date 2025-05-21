from models.persistivel import Persistivel
from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido

class Loja(Persistivel):
    def __init__(self, id = 0, nome = "", imagem = "", produtos = [], anuncios = [], pedidos_confirmados = [], pedidos_em_andamento = [], id_usuario = 0):
        # Atributos próprios
        self.id = id
        self.nome = nome
        self.imagem = imagem

        # Atributos estrangeiros
        self.id_usuario = id_usuario
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
        print([produto.to_dict() for produto in self.produtos])
        print([anuncio for anuncio in self.anuncios])
        return {
            "id": self.id,
            "nome": self.nome,
            "imagem": self.imagem,
            "produtos": [produto.to_dict() for produto in self.produtos],
            "anuncios": [anuncio.to_dict() for anuncio in self.anuncios],
            "pedidos_confirmados": [pedido.to_dict() for pedido in self.pedidos_confirmados],
            "pedidos_em_andamento": [pedido.to_dict() for pedido in self.pedidos_em_andamento]
        }
    
    def to_dict_personalisado(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "imagem": self.imagem if self.imagem else "",
        }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ("id_usuario", "nome")
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd

    def clone_zerado(self):
        return Loja()
    
    @classmethod
    def from_dict(cls, dados):
        id = dados.get("id", 0)
        nome = dados.get("nome", "")
        imagem = dados.get("imagem", "")
        produtos = [Produto.from_dict(produto) for produto in dados["produtos"]] if "produtos" in dados else []
        anuncios = [Anuncio.from_dict(anuncio) for anuncio in dados["anuncios"]] if "anuncios" in dados else []
        pedidos_confirmados = [Pedido.from_dict(pedido) for pedido in dados["pedidos_confirmados"]] if "pedidos_confirmados" in dados else []
        pedidos_em_andamento = [Pedido.from_dict(pedido) for pedido in dados["pedidos_em_andamento"]] if "pedidos_em_andamento" in dados else []

        return cls(id, nome, imagem, produtos, anuncios, pedidos_confirmados, pedidos_em_andamento)
    
    def __str__(self):
        return f"Loja(id={self.id}, nome={self.nome}, imagem={self.imagem}, id_usuario={self.id_usuario}, produtos={self.produtos}, anuncios={self.anuncios}, pedidos_confirmados={self.pedidos_confirmados}, pedidos_em_andamento={self.pedidos_em_andamento})"