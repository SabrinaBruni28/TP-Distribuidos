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

class DAOPedido(DAO):
    def __init__(self,
            nome_tabelas: list = ['pedido', 'anuncio_pedido', 'produto_pedido', 'endereco_pedido'],
            nome_colunas: list = ['id_anuncio', 'id_endereco', 'id_usuario', 'quantidade_pedido', 'data_pedido']):
        
        super().__init__(nome_tabelas, nome_colunas)
        self.__daoEndereco_Pedido = DAOEndereco(['endereco_pedido'])
        self.__daoProduto_Pedido = DAOProduto(['produto_pedido'])
        self.__daoImagem_Pedido = DAOImagem_Produto(['imagem_pedido'])
        self.__daoAnuncio_Pedido = DAOAnuncio(['anuncio_pedido'])
    
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
        #IMPORTANTE: Os elementos de Pedido estão inicialmente com o id das tabelas originais, não zerados! Mudar a ordem de inserção pode causar erro irrastreável nas referências!
        if isinstance(obj.endereco, Endereco) and isinstance(obj.anuncio, Anuncio) and isinstance(obj.anuncio.produto, Produto) and isinstance(obj.anuncio.produto.loja, Loja):
            # Endereço
            obj.endereco.id = 0
            if result := self.__daoEndereco_Pedido.select(obj.endereco, logic= 'AND'):
                obj.endereco.id = result[0].id
            else:
                obj.endereco.id = self.__daoEndereco_Pedido.insert(obj.endereco)
            
            # Produto
            obj.anuncio.produto.id = 0
            if result := self.__daoProduto_Pedido.select(obj.anuncio.produto, logic= 'AND'):
                obj.anuncio.produto.id = result[0].id
            else:
                obj.anuncio.produto.id = self.__daoProduto_Pedido.insert(obj.anuncio.produto)
            
            # Imagens
            imagem_pedido = Imagem_Produto()
            imagens_pedido = []
            for imagem_produto in obj.anuncio.produto.imagens:
                imagem_pedido.id = imagem_produto.id
                imagem_pedido.id_produto = 0
                if result := self.__daoImagem_Pedido.select(imagem_pedido, logic= 'AND'):
                    imagem_pedido.id_produto = result[0].id_produto
                    imagens_pedido.append(imagem_pedido.caminho())
                elif imagem := imageu.obterImagem('produto', imagem_produto.caminho()):
                    imagem_pedido.id_produto = obj.anuncio.produto.id
                    self.__daoImagem_Pedido.insert(imagem_pedido)
                    imageu.salvarImagem('pedido', imagem_pedido.caminho(), imagem)
                    imagens_pedido.append(imagem_pedido.caminho())
                else:
                    print('Erro ao salvar imagem do pedido')
            obj.anuncio.produto.imagens = imagens_pedido

            # Anúncio
            obj.anuncio.id_produto = obj.anuncio.produto.id
            obj.anuncio.id = 0
            if result := self.__daoAnuncio_Pedido.select(obj.anuncio):
                obj.anuncio.id = result[0].id
            else:
                obj.anuncio.id = self.__daoAnuncio_Pedido.insert(obj.anuncio)

            # Pedido
            obj.id_endereco = obj.endereco.id
            obj.id_anuncio = obj.anuncio.id
        return super().insert(obj)

    def select(self, obj: Pedido, logic = 'OR'):
        return [(self._from_tuple_completo(pedido_tupla), bool(pedido_tupla[5])) for pedido_tupla in super().select(obj, logic)]

    def update(self, obj: Pedido):
        pass

    def delete(self, id_obj: int):
        return super().delete(id_obj)
    
    def forget(self, obj: Pedido):
        pass

    def confirmarPedido(self, obj: Pedido):
        obj.quantidade = -1
        pedido_tupla = super().update(obj)
        return self._from_tuple(pedido_tupla), bool(pedido_tupla[5])

