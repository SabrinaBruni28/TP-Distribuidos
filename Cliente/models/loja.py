from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido
import json

class Loja:
    def __init__(
            self, id: int = 0, nome: str = "", imagem: str = "", 
            produtos: Produto = [], anuncios: Anuncio = [], 
            pedidos_confirmados: Pedido = [], pedidos_em_andamento: Pedido = []
        ):
        self.id = id
        self.nome = nome
        self.imagem = imagem

        self.produtos = produtos
            
        self.anuncios = anuncios
        self.pedidos_confirmados = pedidos_confirmados
        self.pedidos_em_andamento = pedidos_em_andamento

    def anuncio_produto(self, produto):
        for anuncio in self.anuncios:
            if anuncio.produto.id == produto.id:
                return anuncio
        return None

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
        for i, p in enumerate(self.produtos):
            if p.id == produto.id:
                del self.produtos[i]
                return True
        return False

    def apagar_anuncio(self, anuncio: Anuncio):
        for i, a in enumerate(self.anuncios):
            if a.id == anuncio.id:
                del self.anuncios[i]
                return True
        return False
    
    def editar_produto(self, produto, novo_produto):
        for i, p in enumerate(self.produtos):
            if p.id == produto.id:
                self.produtos[i] = novo_produto
                return novo_produto
        return False
    
    def editar_anuncio(self, anuncio, novo_anuncio):
        for i, a in enumerate(self.anuncios):
            if a.id == anuncio.id:
                self.anuncios[i] = novo_anuncio
                return novo_anuncio
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
        return json.dumps({
            "id": self.id,
            "nome": self.nome,
            "imagem": self.imagem,
            "produtos": [produto.nome for produto in self.produtos] if self.produtos else [],
            "anuncios": [anuncio.produto.nome for anuncio in self.anuncios] if self.anuncios else [],
            "pedidos_confirmados": [pedido.to_dict() for pedido in self.pedidos_confirmados] if self.pedidos_confirmados else [],
            "pedidos_em_andamento": [pedido.to_dict() for pedido in self.pedidos_em_andamento] if self.pedidos_em_andamento else [],
        }) 
    
    def to_dict_personalizado(self):
        return json.dumps({
            "nome": self.nome,
            "imagem": self.imagem if self.imagem else "",
        })
    
    @classmethod
    def from_dict(cls, data):
        if isinstance(data, str):
            data = json.loads(data)
        id = data.get("id", 0)
        nome = data.get("nome", "")
        imagem = data.get("imagem", "")
        produtos = [Produto.from_dict(produto) for produto in data.get("produtos", [])]
        anuncios = [Anuncio.from_dict(anuncio) for anuncio in data.get("anuncios", [])]
        pedidos_confirmados = [Pedido.from_dict(pedido) for pedido in data.get("pedidos_confirmados", [])]
        pedidos_em_andamento = [Pedido.from_dict(pedido) for pedido in data.get("pedidos_em_andamento", [])]

        return cls(id, nome, imagem, produtos, anuncios, pedidos_confirmados, pedidos_em_andamento)
    
    def __str__(self):
        return f"Loja(id={self.id}, nome={self.nome}, imagem={self.imagem}, produtos={[produto for produto in self.produtos]}, anuncios={[anuncio for anuncio in self.anuncios]}, pedidos_confirmados={[pedido for pedido in self.pedidos_confirmados]}, pedidos_em_andamento={[pedido for pedido in self.pedidos_em_andamento]})"