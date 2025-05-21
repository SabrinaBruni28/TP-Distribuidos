from models.dao.dao import DAO
from models.loja import Loja

class DAOLoja(DAO):
    def __init__(self):
        super().__init__(
            ['loja'],
            ["id_usuario", "nome_loja"])
    
    def _from_tuple(self, tupla = (0, 0, "")):
        return Loja(
            id = tupla[0],
            id_usuario = tupla[1],
            nome = tupla[2])

    def insert(self, obj: Loja):
        obj.id = super().insert(obj)
        if obj.imagem:
            obj.imagem = f'{obj.id}.jpg'
        return obj.id

    def select(self, obj: Loja, logic = 'OR'):
        return [self._from_tuple(tupla) for tupla in super().select(obj, logic)]

    def update(self, obj: Loja):
        loja = self._from_tuple(super().update(obj))
        loja.imagem = obj.imagem
        return loja

    def delete(self, id_obj: int):
        return super().delete(id_obj)
    
    def zerar(self, obj: Loja):
        pass
