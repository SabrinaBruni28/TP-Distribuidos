from models.dao.dao import DAO
from models.imagem_produto import Imagem_Produto

class DAOImagem_Produto(DAO):
    def __init__(self):
        super().__init__(
            ['imagem_produto'],
            ['id_produto'])
    
    def _from_tuple(self, tupla = (0, 0)):
        return Imagem_Produto(
            id = tupla[0],
            id_produto = tupla[1])

    def insert(self, obj: Imagem_Produto):
        return super().insert(obj)

    def select(self, obj: Imagem_Produto, logic = 'OR'):
        return [self._from_tuple(tupla) for tupla in super().select(obj, logic)]

    def update(self, obj: Imagem_Produto):
        return self._from_tuple(super().update(obj))

    def delete(self, id_obj: int):
        return super().delete(id_obj)
