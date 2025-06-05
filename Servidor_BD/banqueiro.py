import copy
from models.dao.dao import DAO
from models.persistivel import Persistivel
from models.dao.dao_usuario import DAOUsuario
from models.dao.dao_endereco import DAOEndereco
from models.dao.dao_loja import DAOLoja
from models.dao.dao_produto import DAOProduto
from models.dao.dao_anuncio import DAOAnuncio
from models.dao.dao_pedido import DAOPedido
from models.dao.dao_imagem_produto import DAOImagem_Produto
from models.usuario import Usuario_Identificado
from models.endereco import Endereco
from models.loja import Loja
from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido
from models.imagem_produto import Imagem_Produto

class Banqueiro():
    def __init__(self):
        self.__daoUsuario = DAOUsuario()
        self.__daoEndereco = DAOEndereco()
        self.__daoLoja = DAOLoja()
        self.__daoProduto = DAOProduto()
        self.__daoAnuncio = DAOAnuncio()
        self.__daoPedido = DAOPedido()
        self.__daoImagem_Produto = DAOImagem_Produto()
    
    # Simula um DAO geral. Serve para quase todos os persistíveis.
    def _dao(self, obj: Persistivel) -> DAO:
        if isinstance(obj, Usuario_Identificado):
            return self.__daoUsuario
        elif isinstance(obj, Endereco):
            return self.__daoEndereco
        elif isinstance(obj, Loja):
            return self.__daoLoja
        elif isinstance(obj, Produto):
            return self.__daoProduto
        elif isinstance(obj, Imagem_Produto):
            return self.__daoImagem_Produto
        elif isinstance(obj, Anuncio):
            return self.__daoAnuncio
        elif isinstance(obj, Pedido):
            return self.__daoPedido
        else:
            print('Erro Fatal: Parâmetro de tipo inválido!')
            return DAO([],[])
    
    def conferir(self, obj: Persistivel, attrs = []):
        obj = copy.deepcopy(obj)
        obj.id = 0
        if result := self._dao(obj).select(obj, logic='OR'):
            print(result)
            erros = []
            obj_dict = obj.to_dict_personalisado()
            if not attrs:
                attrs = obj_dict.keys()
            for attr in attrs:
                print('Olhando:', attr)
                for resultado in result:
                    resultado_dict = resultado.to_dict_personalisado()
                    print('Resultado: ', resultado_dict)
                    if obj_dict.get(attr) == resultado_dict.get(attr):
                        print('erro detectado!')
                        erros.append(attr)
                        break
            return ('erro', erros)
        else:
            return ('ok', 'valida')

    def criar(self, obj: Persistivel):
        return self._dao(obj).insert(obj)
    
    def encontrar(self, obj: Persistivel):
        if result := self._dao(obj).select(obj, logic='AND'):
            obj = result[0]
            return obj
        else:
            return False # Persistível não encontrado
    
    def buscar(self, obj: Persistivel):
        return self._dao(obj).select(obj)
    
    def editar(self, obj: Persistivel):
        if obj := self._dao(obj).update(obj):
            return obj
        else:
            return False

    def excluir(self, obj: Persistivel):
        return self._dao(obj).delete(obj.id)
    
    def excluirProduto(self, obj: Produto):
        imagens_a_remover = []
        ans = 'erro'
        pedidos = self.buscar(Pedido(produto = obj))
        if pedidos:
            result = self.encontrar(obj)
            if isinstance(result, Produto):
                obj = result
                self.__daoProduto.zerar(Produto(id = obj.id))
                ans = 'ok'
        else:
            for imagem_produto in self.buscar(Imagem_Produto(id_produto = obj.id)):
                if self.excluir(imagem_produto) == 'ok':
                    imagens_a_remover.append(imagem_produto.caminho())
            ans = self.excluir(obj)
        return imagens_a_remover, ans

    def confirmarPedido(self, obj: Pedido):
        return self.__daoPedido.confirmarPedido(obj)
    
    def retornarLoja(self, obj: Loja, minha=False):
        loja = self.encontrar(obj)
        if isinstance(loja, Loja):
            dummy_produto = Produto(loja = loja)
            produtos_da_loja = self.buscar(dummy_produto)

            anuncios_da_loja = []
            for produto in produtos_da_loja:
                dummy_produto = Produto(id = produto.id)
                dummy_anuncio = Anuncio(produto = dummy_produto)
                anuncios_do_produto = self.buscar(dummy_anuncio)
                for anuncio in anuncios_do_produto:
                    anuncio.produto.nome = produto.nome
                anuncios_da_loja.extend(anuncios_do_produto)

            
            pedidos_confirmados = []
            pedidos_em_andamento = []
            for produto in produtos_da_loja:
                dummy_produto = Produto(id = produto.id)
                dummy_pedido = Pedido(produto = dummy_produto)
                pedidos_do_produto = self.buscar(dummy_pedido)
                for pedido, confirmacao in pedidos_do_produto:
                    if confirmacao:
                        pedidos_confirmados.append(pedido)
                    else:
                        pedidos_em_andamento.append(pedido)
            
            print(loja)
            for produto in produtos_da_loja:
                print(produto)
            for anuncio in anuncios_da_loja:
                print(anuncio)
            for pc in pedidos_confirmados:
                print(pc)
            for pa in pedidos_em_andamento:
                print(pa)
            loja.anuncios = anuncios_da_loja
            if minha:
                loja.produtos = produtos_da_loja
                loja.pedidos_confirmados = pedidos_confirmados
                loja.pedidos_em_andamento = pedidos_em_andamento
            
            return loja
        else:
            return False #loja não encontrada