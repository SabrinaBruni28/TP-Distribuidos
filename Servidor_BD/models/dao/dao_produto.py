from models.dao.dao import DAO
from models.produto import Produto
from models.loja import Loja

class DAOProduto(DAO):
    def __init__(self):
        super().__init__(
            ['produto'],
            ['id_loja', 'nome_produto', 'descricao_produto'])
    
    def _from_tuple(self, tupla = (0, 0, '', '')):
        return Produto(
            id = tupla[0],
            loja = Loja(id = tupla[1]),
            nome = tupla[2],
            descricao = tupla[3])
    
    def insert(self, obj: Produto):
        return super().insert(obj)

    def select(self, obj: Produto, logic = 'OR'):
        return [self._from_tuple(tupla) for tupla in super().select(obj, logic)]

    def update(self, obj: Produto):
        produto = self._from_tuple(super().update(obj))
        produto.imagens = obj.imagens
        return produto

    def delete(self, id_obj: int):
        return super().delete(id_obj)
    
    def zerar(self, obj: Produto):
        return self._from_tuple(super().zerar(obj, ['id_loja']))
