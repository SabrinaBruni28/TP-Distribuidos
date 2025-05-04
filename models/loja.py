from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido

class Loja:
    def __init__(self, nome: str, imagem: str):
        self.id = 0
        self.nome = nome
        self.imagem = imagem

        self.produtos = []
            
        self.anuncios = [
            Anuncio(Produto("Produto 1", "Descrição do Produto 1", ["imagens/tablet.png"], self), 10.0, 5, "chave_pix_1"), 
            Anuncio(Produto("Produto 2", "Descrição do Produto 2", ["imagens/notebook.png"], self), 20.0, 3, "chave_pix_2"),
            Anuncio(Produto("Produto 3", "Descrição do Produto 3", ["imagens/fone.png"], self), 30.0, 2, "chave_pix_3"),
            Anuncio(Produto("Produto 4", "Descrição do Produto 4", ["imagens/smartphone.png"], self), 40.0, 1, "chave_pix_4"),
        ]*5
        self.pedidos_confirmados = []
        self.pedidos_em_andamento = []

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
            #"produtos": [produto.nome for produto in self.produtos],
            #"anuncios": [anuncio.produto.nome for anuncio in self.anuncios],
            #"pedidos_confirmados": [pedido.to_dict() for pedido in self.pedidos_confirmados],
            #"pedidos_em_andamento": [pedido.to_dict() for pedido in self.pedidos_em_andamento]
        }  
    
    def from_dict(self, data):
        self.id = data.get("id", 0)
        self.nome = data["nome"]
        self.imagem = data["imagem"]
        self.produtos = [Produto.from_dict(produto) for produto in data["produtos"]] if "produtos" in data else []
        self.anuncios = [Anuncio.from_dict(anuncio) for anuncio in data["anuncios"]] if "anuncios" in data else []
        self.pedidos_confirmados = [Pedido.from_dict(pedido) for pedido in data["pedidos_confirmados"]] if "pedidos_confirmados" in data else []
        self.pedidos_em_andamento = [Pedido.from_dict(pedido) for pedido in data["pedidos_em_andamento"]] if "pedidos_em_andamento" in data else []
    
