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

class DAOPedido_Confirmado(DAO):
    def __init__(self,
            nome_tabelas: list = ['pedido_confirmado', 'anuncio_pedido', 'produto_pedido', 'endereco_pedido'],
            nome_colunas: list = ['id_anuncio', 'id_endereco', 'id_usuario', 'id_produto', 'id_loja', 'quantidade_pedido', 'data_pedido']):
        
        super().__init__(nome_tabelas, nome_colunas)
        self.__daoEndereco_Pedido = DAOEndereco(['endereco_pedido'])
        self.__daoProduto_Pedido = DAOProduto(['produto_pedido'])
        self.__daoImagem_Pedido = DAOImagem_Produto(['imagem_pedido'])
        self.__daoAnuncio_Pedido = DAOAnuncio(['anuncio_pedido', 'produto_pedido'])
    
    def _from_tuple(self, tupla = (0, 0, 0, 0, '')):
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(id = tupla[1]),
            endereco = Endereco(id = tupla[2]),
            quantidade = tupla[3],
            data = tupla[4]
        )
        return pedido
    
    def _from_tuple_completo(self, tupla = (0, 0, 0, 0, '', 0, 0, 0, '', '', 0, '', '', '', '', '', '')):
        pedido = Pedido(
            id = tupla[0],
            anuncio = Anuncio(
                id = tupla[1],
                produto = Produto(
                    id = tupla[5],
                    nome = tupla[8],
                    descricao = tupla[9],
                    loja = Loja(id = tupla[7]) if tupla[7] is not None else None
                ),
                preco = tupla[6],
            ),
            endereco = Endereco(
                id = tupla[2],
                id_usuario= tupla[10],
                rua= tupla[11],
                numero= tupla[12],
                bairro= tupla[13],
                cidade= tupla[14],
                estado= tupla[15],
                complemento= tupla[16]
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
            obj.anuncio.quantidade_disponivel = 0
            obj.anuncio.chave_pix = ''
            obj.anuncio.pausado = None
            if result := self.__daoAnuncio_Pedido.select(obj.anuncio, 'AND'):
                obj.anuncio.id = result[0].id
            else:
                obj.anuncio.id_loja = 0
                obj.anuncio.id = self.__daoAnuncio_Pedido.insert(obj.anuncio)

            # Pedido
            obj.id_endereco = obj.endereco.id
            obj.id_anuncio = obj.anuncio.id
            obj.id_usuario = 0
        return super().insert(obj)

    def select(self, obj: Pedido, logic = 'OR'):
        return [self._from_tuple_completo(pedido_tupla) for pedido_tupla in super().select(obj, logic)]

    def update(self, obj: Pedido):
        pass

    def delete(self, obj: Pedido):
        return super().delete(obj)
    
    def forget(self, obj: Pedido):
        pass

    def __from_tuple_view(self, tupla = (0, 0, 0, 0)):
        return Pedido(
            id = tupla[0],
            anuncio = Anuncio(
                id = tupla[1],
                produto= Produto(id= tupla[2])
            ),
            endereco = Endereco(id = tupla[3])
        )
    
    def cleanForgotten(self):
        pedidos, anuncios, produtos, enderecos = super()._cleaningView()

        # Apagando pedidos...
        for pedido in pedidos:
            self.delete(Pedido(id= pedido[0]))
        
        # Verificando e apagando anúncios...
        for anuncio in anuncios:
            anuncio = Anuncio(id= anuncio[0])
            if not self.select(Pedido(anuncio= anuncio)):
                self.__daoAnuncio_Pedido.delete(anuncio)
        
        # Verificando e apagando produtos...
        for endereco in enderecos:
            if not self.select(Pedido(endereco= Endereco(id= endereco[0]))):
                self.__daoEndereco_Pedido.delete(Endereco(id= endereco[0]))
        
        # Verificando e apagando produtos...
        imagens_a_apagar = []
        for produto in produtos:
            if not self.select(Pedido(id_produto= produto[0])):
                # Recuperando e apagando imagens do produto
                imagens_a_apagar += [imagens.caminho() for imagens in self.__daoImagem_Pedido.select(Imagem_Produto(id_produto= produto[0]))]
                self.__daoImagem_Pedido.delete(Imagem_Produto(id_produto= produto[0]))

                # Apagando produtos...
                self.__daoProduto_Pedido.delete(Produto(id= produto[0]))
        
        return imagens_a_apagar