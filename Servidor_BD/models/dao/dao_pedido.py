from models.dao.dao import DAO
from models.pedido import Pedido
from models.endereco import Endereco
from models.anuncio import Anuncio
from models.produto import Produto
from models.loja import Loja

class DAOPedido(DAO):
    def __init__(self):
        super().__init__(
            ['pedido', 'anuncio', 'produto', 'endereco'],
            ['id_anuncio', 'id_endereco', 'id_usuario', 'quantidade_pedido', 'data_pedido'])
    
    def _from_tuple(self, tupla = (0, 0, 0, 0, '', False)):
        #confirmacao_pedido = tupla[5],
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(id = tupla[1]),
            endereco = Endereco(id = tupla[2]),
            quantidade = tupla[3],
            data = tupla[4]
        )
        return pedido
    
    def _from_tuple_completo(self, tupla = (0, 0, 0, 0, '', False, 0, 0, 0, '', False, 0, '', '', 0, '', '', '', '', '', '')):
        #confirmacao_pedido = tupla[5],
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(
                id = tupla[1],
                produto = Produto(
                    id = tupla[6],
                    nome = tupla[12],
                    descricao = tupla[13],
                    loja = Loja(id = tupla[11])
                ),
                preco = tupla[7],
                quantidade_disponivel = tupla[8],
                chave_pix = tupla[9],
                pausado = tupla[10]
            ),
            endereco = Endereco(
                id = tupla[2],
                id_usuario= tupla[14],
                rua= tupla[15],
                numero= tupla[16],
                bairro= tupla[17],
                cidade= tupla[18],
                estado= tupla[19],
                complemento= tupla[20]
            ),
            quantidade = tupla[3],
            data = tupla[4]
        )
        return pedido

    def insert(self, obj: Pedido):
        return super().insert(obj)

    def select(self, obj: Pedido, logic = 'OR'):
        return [(self._from_tuple_completo(pedido_tupla), bool(pedido_tupla[5])) for pedido_tupla in super().select(obj, logic)]

    def update(self, obj: Pedido):
        pass

    def delete(self, id_obj: int):
        return super().delete(id_obj)
    
    def zerar(self, obj: Pedido):
        pass

    def confirmarPedido(self, obj: Pedido):
        obj.quantidade = -1
        pedido_tupla = super().update(obj)
        return self._from_tuple(pedido_tupla), bool(pedido_tupla[5])

