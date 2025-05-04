
class Anuncio:
    def __init__(self, id, produto, preco, quantidade_disponivel, chave_pix):
        self.id = id
        self.produto = produto
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel
        self.chave_pix = chave_pix
        self.pausado = False

    def subtrair_quantidade(self, quantidade):
        if quantidade > self.quantidade_disponivel:
            raise ValueError("Quantidade solicitada maior que a disponível.")
        self.quantidade_disponivel -= quantidade
        if self.quantidade_disponivel == 0:
            self.pausar()

    def pausar(self):
        self.pausado = True