from models.dao.dao import DAO
from models.anuncio import Anuncio
from models.produto import Produto
from models.loja import Loja

class DAOAnuncio(DAO):
    def __init__(self,
            nome_tabelas: list = ['anuncio', 'produto'],
            nome_colunas: list = ['id_produto', 'id_loja', 'preco_anuncio', 'quantidade_produto', 'chave_pix', 'pausado']):
        
        super().__init__(nome_tabelas, nome_colunas)
    
    def _from_tuple_completo(self, tupla = (0, 0, 0, 0, '', 0, 0, '', '')):
        return Anuncio(
            id = tupla[0],
            produto = Produto(
                id = tupla[1],
                loja= Loja(id= tupla[6]),
                nome= tupla[7],
                descricao= tupla[8]),
            preco = tupla[2],
            quantidade_disponivel = tupla[3],
            chave_pix = tupla[4],
            pausado = bool(tupla[5]))
    
    def _from_tuple(self, tupla = (0, 0, 0, 0, '', 0)):
        return Anuncio(
            id = tupla[0],
            produto = Produto(id = tupla[1]),
            preco = tupla[2],
            quantidade_disponivel = tupla[3],
            chave_pix = tupla[4],
            pausado = bool(tupla[5]))
    
    def _from_tuple_pedido_completo(self, tupla = (0, 0, 0, 0, '', '')):
        return Anuncio(
            id = tupla[0],
            produto = Produto(
                id = tupla[1],
                loja= Loja(id= tupla[3]),
                nome= tupla[4],
                descricao= tupla[5]),
            preco = tupla[2])
    
    def _from_tuple_pedido(self, tupla = (0, 0, 0)):
        return Anuncio(
            id = tupla[0],
            produto= Produto(id = tupla[1]),
            preco= tupla[2])

    def insert(self, obj: Anuncio):
        return super().insert(obj)

    def select(self, obj: Anuncio, logic = 'OR'):
        return [self._from_tuple_completo(tupla) if len(tupla) == 9 else self._from_tuple_pedido_completo(tupla) for tupla in super().select(obj, logic)]

    def update(self, obj: Anuncio):
        return self._from_tuple(super().update(obj))

    def delete(self, obj: Anuncio):
        return super().delete(obj)
    
    def zerar(self, obj: Anuncio):
        pass
