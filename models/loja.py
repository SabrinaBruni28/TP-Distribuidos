
class Loja:
    def __init__(self, id: int,  nome: str, imagem: str):
        self.id = id
        self.nome = nome
        self.imagem = imagem

        self.produtos = []
        self.anuncios = []
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
    
    
    
