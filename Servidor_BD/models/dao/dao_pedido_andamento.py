import image_utils as imageu
from models.dao.dao import DAO
from models.dao.dao_endereco import DAOEndereco
from models.dao.dao_produto import DAOProduto
from models.dao.dao_imagem_produto import DAOImagem_Produto
from models.dao.dao_anuncio import DAOAnuncio
from models.pedido import Pedido
from models.endereco import Endereco
from models.anuncio import Anuncio
from models.produto import Produto
from models.imagem_produto import Imagem_Produto
from models.loja import Loja

class DAOPedido_Andamento(DAO):
    def __init__(self,
            nome_tabelas: list = ['pedido_andamento', 'anuncio', 'produto', 'endereco'],
            nome_colunas: list = ['id_anuncio', 'id_endereco', 'id_usuario', 'id_loja', 'quantidade_pedido', 'data_pedido']):
        
        super().__init__(nome_tabelas, nome_colunas)
    
    def _from_tuple(self, tupla = (0, 0, 0, 0, '')):
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(id = tupla[1]),
            endereco = Endereco(id = tupla[2]),
            quantidade = tupla[3],
            data = tupla[4]
        )
        return pedido
    
    def _from_tuple_completo(self, tupla = (0, 0, 0, 0, '', 0, 0, 0, '', False, 0, '', '', 0, '', '', '', '', '', '')):
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(
                id = tupla[1],
                produto = Produto(
                    id = tupla[5],
                    nome = tupla[11],
                    descricao = tupla[12],
                    loja = Loja(id = tupla[10])
                ),
                preco = tupla[6],
                quantidade_disponivel = tupla[7],
                chave_pix = tupla[8],
                pausado = tupla[9]
            ),
            endereco = Endereco(
                id = tupla[2],
                id_usuario= tupla[13],
                rua= tupla[14],
                numero= tupla[15],
                bairro= tupla[16],
                cidade= tupla[17],
                estado= tupla[18],
                complemento= tupla[19]
            ),
            quantidade = tupla[3],
            data = tupla[4]
        )
        return pedido

    def insert(self, obj: Pedido):
        return super().insert(obj)

    def select(self, obj: Pedido, logic = 'OR'):
        return [self._from_tuple_completo(pedido_tupla) for pedido_tupla in super().select(obj, logic)]

    def update(self, obj: Pedido):
        pass

    def delete(self, obj: Pedido):
        return super().delete(obj)
    
    def forget(self, obj: Pedido):
        pass

