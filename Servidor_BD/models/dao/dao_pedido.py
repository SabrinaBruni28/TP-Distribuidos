from models.dao.dao import DAO
from models.pedido import Pedido
from models.produto import Produto
from models.endereco import Endereco

class DAOPedido(DAO):
    def __init__(self):
        super().__init__(
            ['pedido'],
            ["id_produto", "id_endereco", "quantidade_pedido", "preco_anuncio", "data_pedido"])
    
    def _from_tuple(self, tupla = (0, 0, 0, 0, "", 0)):
        return Pedido(
            id = tupla[0],
            produto = Produto(id = tupla[1]),
            endereco = Endereco(id = tupla[2]),
            quantidade = tupla[3],
            preco = tupla[4],
            data = tupla[5])

    def insert(self, obj: Pedido):
        return super().insert(obj)

    def select(self, obj: Pedido, logic = 'OR'):
        return [(self._from_tuple(pedido_tupla[:6]), bool(pedido_tupla[6])) for pedido_tupla in super().select(obj, logic)]

    def update(self, obj: Pedido):
        pedido_tupla = super().update(obj)
        return (self._from_tuple(pedido_tupla[:6]), bool(pedido_tupla[6]))

    def delete(self, id_obj: int):
        return super().delete(id_obj)
