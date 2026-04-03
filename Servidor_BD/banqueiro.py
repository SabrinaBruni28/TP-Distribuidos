import traceback
from Pyro5.api import expose
from Pyro5.api import behavior
import image_utils as imageu
from models.persistivel import Persistivel
from models.dao.dao_usuario import DAOUsuario
from models.dao.dao_endereco import DAOEndereco
from models.dao.dao_loja import DAOLoja
from models.dao.dao_produto import DAOProduto
from models.dao.dao_anuncio import DAOAnuncio
from models.dao.dao_pedido_andamento import DAOPedido_Andamento
from models.dao.dao_pedido_confirmado import DAOPedido_Confirmado
from models.dao.dao_imagem_produto import DAOImagem_Produto
from models.usuario import Usuario_Identificado
from models.endereco import Endereco
from models.loja import Loja
from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido
from models.imagem_produto import Imagem_Produto

@expose
@behavior(instance_mode='single')
class Banqueiro():

    def __init__(self):
        self.__daoUsuario = DAOUsuario()
        self.__daoEndereco = DAOEndereco()
        self.__daoLoja = DAOLoja()
        self.__daoProduto = DAOProduto()
        self.__daoAnuncio = DAOAnuncio()
        self.__daoPedido_Andamento = DAOPedido_Andamento()
        self.__daoPedido_Confirmado = DAOPedido_Confirmado()
        self.__daoImagem_Produto = DAOImagem_Produto()
        self.__daoImagem_Pedido = DAOImagem_Produto(['imagem_pedido'])
    
    ################################## Login ##################################

    def loginUsuario(self, usuario: dict):
        try:
            print('[Banqueiro][Login] - Iniciando tentativa de login...')
            usuarioLogando = Usuario_Identificado.from_dict(usuario)
            print('[Banqueiro][Login] - Usuário a logar:', usuarioLogando)
            if result := self.__daoUsuario.select(usuarioLogando, logic= 'AND'):
                print('[Banqueiro][Login] - Usuário encontrado:', result[0])
                return result[0].to_dict()
            else:
                print('[Banqueiro][Login] - Usuário não encontrado!')
                return 'dados_incorretos'
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Login][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    ################################## Confere Usuário ##################################
    
    def confereUsuario(self, usuario: dict):
        try:
            print('[Banqueiro][Confere][Usuário] - Iniciando conferimento do usuário...')
            usuarioConferindo = Usuario_Identificado.from_dict(usuario)
            print('[Banqueiro][Confere][Usuário] - Usuário a conferir:', usuarioConferindo)
            usuarioConferindo.id = 0
            print('[Banqueiro][Confere][Usuário] - Conferindo usuário...')
            erros = []
            if result := self.__daoUsuario.select(usuarioConferindo):
                for resultado in result:
                    if usuarioConferindo.cpf == resultado.cpf:
                        print('[Banqueiro][Confere][Usuário] - Incompatibilidade detectada: cpf repete.')
                        erros.append('cpf')
                        break
                for resultado in result:
                    if usuarioConferindo.email == resultado.email:
                        print('[Banqueiro][Confere][Usuário] - Incompatibilidade detectada: email repete.')
                        erros.append('email')
                        break
                if erros:
                    print('[Banqueiro][Confere][Usuário] - Retornando motivos de incompatibilidade...')
                    return erros
            print('[Banqueiro][Confere] - Usuário conferido: Integridade do banco livre de ameaças.')
            return True
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Confere][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    ################################## Criar ##################################

    def criarUsuario(self, usuario: dict):
        try:
            print(f'[Banqueiro][Criar][Usuário] - Iniciando tentativa de criar usuário...')
            obj = Usuario_Identificado.from_dict(usuario)
            print('[Banqueiro][Criar][Usuário] - Usuário a criar:', obj)
            print('[Banqueiro][Criar][Usuário] - Inserindo usuário no banco...')
            obj.id = self.__daoUsuario.insert(obj)
            print('[Banqueiro][Criar][Usuário] - Retornando usuário inserido...')
            return obj.to_dict()
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Usuário][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarEndereco(self, id_usuario: int, endereco: dict):
        try:
            print(f'[Banqueiro][Criar][Endereço] - Iniciando tentativa de criar endereço...')
            obj = Endereco.from_dict(endereco)
            obj.id_usuario = id_usuario
            print('[Banqueiro][Criar][Endereço] - Endereço a criar:', obj)
            print('[Banqueiro][Criar][Endereço] - Inserindo endereço no banco...')
            obj.id = self.__daoEndereco.insert(obj)
            print('[Banqueiro][Criar][Endereço] - Retornando endereço inserido...')
            return obj.to_dict()
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Endereço][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarLoja(self, id_usuario: int, loja: dict, imagem= None):
        try:
            print(f'[Banqueiro][Criar][Loja] - Iniciando tentativa de criar loja...')
            obj = Loja.from_dict(loja)
            obj.id_usuario = id_usuario
            print('[Banqueiro][Criar][Loja] - Loja a criar:', obj)
            print('[Banqueiro][Criar][Loja] - Inserindo loja no banco...')
            obj.id = self.__daoLoja.insert(obj)
            if imagem is not None:
                obj.imagem = f'{obj.id}.jpg'
                imageu.salvarImagem('loja', obj.imagem, imagem)
            print('[Banqueiro][Criar][Loja] - Retornando loja inserido...')
            return obj.to_dict(), imagem
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Loja][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarImagemProduto(self, id_produto: int, imagem: bytes):
        try:
            print(f'[Banqueiro][Criar][Imagem] - Iniciando tentativa de criar imagem de produto...')
            imagem_produto = Imagem_Produto(id_produto= id_produto)
            print('[Banqueiro][Criar][Imagem] - Imagem a criar:', imagem_produto)
            print('[Banqueiro][Criar][Imagem] - Inserindo imagem no banco...')
            imagem_produto.id = self.__daoImagem_Produto.insert(imagem_produto)
            imageu.salvarImagem('produto', imagem_produto.caminho(), imagem)
            print('[Banqueiro][Criar][Imagem] - Retornando nome e imagem salvos...')
            return imagem_produto.caminho(), imagem
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Imagem][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarProduto(self, produto: dict, imagens: list[bytes]):
        try:
            print(f'[Banqueiro][Criar][Produto] - Iniciando tentativa de criar produto...')
            obj = Produto.from_dict(produto)
            print('[Banqueiro][Criar][Produto] - Produto a criar:', obj)
            print('[Banqueiro][Criar][Produto] - Inserindo produto no banco...')
            obj.id = self.__daoProduto.insert(obj)
            obj.imagens = []
            for imagem in imagens:
                if img_t := self.criarImagemProduto(obj.id, imagem):
                    nomeImagem, _ = img_t
                    obj.imagens.append(nomeImagem)
                else:
                    print('[Banqueiro][Criar][Produto][Imagem] - Não foi possível inserir a imagem no banco de dados.')
            print('[Banqueiro][Criar][Produto] - Retornando produto inserido...')
            return obj.to_dict(), imagens
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Produto][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarAnuncio(self, anuncio: dict):
        try:
            print(f'[Banqueiro][Criar][Anúncio] - Iniciando tentativa de criar anuncio...')
            obj = Anuncio.from_dict(anuncio)
            print('[Banqueiro][Criar][Anúncio] - Anuncio a criar:', obj)
            print('[Banqueiro][Criar][Anúncio] - Inserindo anuncio no banco...')
            obj.id = self.__daoAnuncio.insert(obj)
            if isinstance(obj.produto, Produto):
                print('[Banqueiro][Criar][Anúncio] - Recuperando produto do anuncio inserido...')
                if result := self.__daoProduto.select(Produto(id= obj.produto.id)):
                    obj.produto = result[0]
                    print('[Banqueiro][Criar][Anúncio] - Produto recuperado:', obj.produto)

                    print(f'[Banqueiro][Retornar][Produto] - Recuperando imagens do produto...')
                    obj.produto.imagens = [imagem_produto.caminho() for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = obj.produto.id))]
                    print(f'[Banqueiro][Retornar][Produto] - Produto recuperado + imagens:', obj.produto)
                else:
                    print('[Banqueiro][Criar][Anúncio] - Produto não encontrado!')
                    return False
            else:
                print('[Banqueiro][Criar][Anúncio] - Falha fatal: Anúncio sem produto!')
                return False
            print('[Banqueiro][Criar][Anúncio] - Retornando anuncio inserido...')
            return obj.to_dict()
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Anúncio][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarPedido(self, pedido: dict):
        try:
            print(f'[Banqueiro][Criar][Pedido] - Iniciando tentativa de criar pedido...')
            obj = Pedido.from_dict(pedido)
            print('[Banqueiro][Criar][Pedido] - Pedido a criar:', obj)
            print('[Banqueiro][Criar][Pedido] - Inserindo pedido no banco...')
            obj.id = self.__daoPedido_Andamento.insert(obj)
            print('[Banqueiro][Criar][Pedido] - Retornando pedido inserido...')
            return obj.to_dict()
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Pedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def criarPeido(self, pedido: dict):
        try:
            print(f'[Banqueiro][Criar][Pedido] - Iniciando tentativa de criar pedido...')
            obj = Pedido.from_dict(pedido)
            print('[Banqueiro][Criar][Pedido] - Pedido a criar:', obj)

            print('[Banqueiro][Criar][Pedido] - Recuperando endereço do pedido...')
            if isinstance(obj.endereco, Endereco):
                if result := self.__daoEndereco.select(Endereco(id = obj.endereco.id), logic= 'AND'):
                    obj.endereco = result[0]
                else:
                    print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Endereço não encontrado!')
                    return False
            else:
                print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Pedido não possui endereço!')
                return False
            
            print('[Banqueiro][Criar][Pedido] - Recuperando anúncio do pedido...')
            if isinstance(obj.anuncio, Anuncio):
                if result := self.__daoAnuncio.select(Anuncio(id = obj.anuncio.id), logic= 'AND'):
                    obj.anuncio = result[0]

                    print('[Banqueiro][Criar][Pedido] - Recuperando produto do anúncio do pedido...')
                    if isinstance(obj.anuncio.produto, Produto):
                        if result := self.__daoProduto.select(Produto(id = obj.anuncio.produto.id), logic= 'AND'):
                            obj.anuncio.produto = result[0]

                            print('[Banqueiro][Criar][Pedido] - Recuperando imagens do produto do pedido...')
                            #Está adicionando os objetos e não os caminhos pois isso será necessário no conferimento de redundância.
                            obj.anuncio.produto.imagens = self.__daoImagem_Produto.select(Imagem_Produto(id_produto = obj.anuncio.produto.id))
                        else:
                            print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Pedido não encontrado!')
                            return False
                    else:
                        print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Anúncio do pedido não possui produto!')
                        return False
                    
                else:
                    print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Anúncio não encontrado!')
                    return False
            else:
                print(f'[Banqueiro][Criar][Pedido] - Falha fatal: Pedido não possui anúncio!')
                return False
            
            print('[Banqueiro][Criar][Pedido] - Pedido a criar + endereço + anuncio + produto + imagens:', obj)
            print('[Banqueiro][Criar][Pedido] - Inserindo pedido no banco...')
            obj.id = self.__daoPedido_Andamento.insert(obj)
            print('[Banqueiro][Criar][Pedido] - Retornando pedido inserido...')
            return obj.to_dict()
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Criar][Pedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    ################################### Retornar ###################################
    
    def retornarUsuario(self, id_usuario: int):
        try:
            print(f'[Banqueiro][Retornar][Usuário] - Iniciando tentativa de retornar usuário...')
            if result := self.__daoUsuario.select(Usuario_Identificado(id= id_usuario), logic= 'AND'):
                usuario = result[0]
                print(f'[Banqueiro][Retornar][Usuário] - Usuário recuperado:', usuario)
                return usuario.to_dict()
            else:
                print(f'[Banqueiro][Retornar][Usuário] - Usuário não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Usuário][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def retornarImagem(self, tipoObj: str, nomeImagem: str):
        try:
            print(f'[Banqueiro][Retornar][Imagem] - Iniciando tentativa de retornar imagem...')
            imagem = imageu.obterImagem(tipoObj, nomeImagem)
            if imagem:
                print(f'[Banqueiro][Retornar][Imagem] - Imagem obtida! Retornando imagem...')
                return imagem
            else:
                print(f'[Banqueiro][Retornar][Imagem] - Imagem não encontrada!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Imagem][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def retornarAnuncios(self):
        try:
            print(f'[Banqueiro][Retornar][Anuncios] - Iniciando tentativa de retornar anuncios...')
            anuncios = self.__daoAnuncio.select(Anuncio(pausado= False))
            print(f'[Banqueiro][Retornar][Anuncios] - Anuncios recuperados:', anuncios)
            print(f'[Banqueiro][Retornar][Anuncios] - Recuperando imagens do anuncios...')
            for anuncio in anuncios:
                if anuncio.produto is not None:
                    anuncio.produto.imagens = []
                    for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = anuncio.produto.id)):
                        anuncio.produto.imagens.append(imagem_produto.caminho())
                    print(f'[Banqueiro][Retornar][Anuncios] - Anuncio recuperado + imagens:', anuncio)
                else:
                    print(f'[Banqueiro][Retornar][Anúncio] - Falha fatal: Anuncio não possui Produto!')
                    return False
            print(f'[Banqueiro][Retornar][Anuncios] - Retornando anuncios...')
            return [anuncio.to_dict() for anuncio in anuncios]
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Anuncios][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def retornarAnuncio(self, id):
        try:
            print(f'[Banqueiro][Retornar][Anúncio] - Iniciando tentativa de retornar anuncio...')
            if result := self.__daoAnuncio.select(Anuncio(id= id), logic= 'AND'):
                anuncio = result[0]
                print(f'[Banqueiro][Retornar][Anúncio] - Anuncio recuperado:', anuncio)
                if anuncio.produto is not None:
                    anuncio.produto.imagens = []
                    print(f'[Banqueiro][Retornar][Anuncios] - Recuperando imagens do anuncio...')
                    for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = anuncio.produto.id)):
                        anuncio.produto.imagens.append(imagem_produto.caminho())
                    print(f'[Banqueiro][Retornar][Anúncio] - Anuncio recuperado + imagens:', anuncio)
                else:
                    print(f'[Banqueiro][Retornar][Anúncio] - Falha fatal: Anúncio não possui Produto!')
                    return False
                print(f'[Banqueiro][Retornar][Anúncio] - Retornando anuncio...')
                return anuncio.to_dict()
            else:
                print(f'[Banqueiro][Retornar][Anúncio] - Anúncio não encontrado!')
                return 'Anúncio não encontrado!'
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Anúncio][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarProduto(self, id):
        try:
            print(f'[Banqueiro][Retornar][Produto] - Iniciando tentativa de retornar produto...')
            if result := self.__daoProduto.select(Produto(id= id), logic= 'AND'):
                produto = result[0]
                print(f'[Banqueiro][Retornar][Produto] - Produto recuperado:', produto)
                produto.imagens = []
                print(f'[Banqueiro][Retornar][Produto] - Recuperando imagens do produto...')
                for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = produto.id)):
                    produto.imagens.append(imagem_produto.caminho())
                print(f'[Banqueiro][Retornar][Produto] - Produto recuperado + imagens:', produto)
                print(f'[Banqueiro][Retornar][Produto] - Retornando produto...')
                return produto.to_dict()
            else:
                print(f'[Banqueiro][Retornar][Produto] - Produto não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Produto][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarPedidoAndamento(self, id: int):
        try:
            print(f'[Banqueiro][Retornar][Pedido][Andamento] - Iniciando tentativa de retornar pedido...')
            if result := self.__daoPedido_Andamento.select(Pedido(id= id), logic= 'AND'):
                pedido = result[0]
                print(f'[Banqueiro][Retornar][Pedido][Andamento] - Pedido recuperado:', pedido)
                if pedido.anuncio is not None:
                    pedido.anuncio.produto.imagens = []
                    print(f'[Banqueiro][Retornar][Pedido][Andamento] - Recuperando imagens do pedido...')
                    for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = pedido.anuncio.produto.id)):
                        pedido.anuncio.produto.imagens.append(imagem_produto.caminho())
                    print(f'[Banqueiro][Retornar][Pedido][Andamento] - Pedido recuperado + imagens:', pedido)
                    print(f'[Banqueiro][Retornar][Pedido][Andamento] - Retornando pedido...')
                    return pedido.to_dict()
                else:
                    print(f'[Banqueiro][Retornar][Pedido][Andamento] - Falha fatal: Pedido não possui Anúncio!')
                    return False
            else:
                print(f'[Banqueiro][Retornar][Pedido][Andamento] - Pedido não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Pedido][Andamento][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarPedidoConfirmado(self, id: int):
        try:
            print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Iniciando tentativa de retornar pedido...')
            if result := self.__daoPedido_Confirmado.select(Pedido(id= id), logic= 'AND'):
                pedido = result[0]
                print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Pedido recuperado:', pedido)
                if pedido.anuncio is not None:
                    pedido.anuncio.produto.imagens = []
                    print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Recuperando imagens do pedido...')
                    for imagem_produto in self.__daoImagem_Pedido.select(Imagem_Produto(id_produto = pedido.anuncio.produto.id)):
                        pedido.anuncio.produto.imagens.append(imagem_produto.caminho())
                    print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Pedido recuperado + imagens:', pedido)
                    print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Retornando pedido...')
                    return pedido.to_dict()
                else:
                    print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Falha fatal: Pedido não possui Anúncio!')
                    return False
            else:
                print(f'[Banqueiro][Retornar][Pedido][Confirmado] - Pedido não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Pedido][Confirmado][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarLoja(self, id):
        try:
            print(f'[Banqueiro][Retornar][Loja] - Iniciando tentativa de retornar loja...')
            if result := self.__daoLoja.select(Loja(id= id), logic= 'AND'):
                loja = result[0]
                if imageu.seExisteImagem('loja', f'{loja.id}.jpg'):
                    loja.imagem = f'{loja.id}.jpg'
                print(f'[Banqueiro][Retornar][Loja] - Loja recuperada:', loja)

                anuncios_da_loja = []
                loja.anuncios = []
                print(f'[Banqueiro][Retornar][Loja] - Recuperando anúncios não pausados da loja...')
                anuncios_da_loja += self.__daoAnuncio.select(Anuncio(produto= Produto(loja= loja))) 
                for anuncio in anuncios_da_loja:
                    if not anuncio.pausado:
                        anuncio.produto.imagens = [imagem_produto.caminho() for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = anuncio.produto.id))]
                        print()
                        print(anuncio.produto.imagens)
                        print()
                        loja.anuncios.append(anuncio)
                
                loja.produtos = []
                loja.pedidos_confirmados = []
                loja.pedidos_em_andamento = []
                print(f'[Banqueiro][Retornar][Loja] - Loja recuperada + anúncios:', loja)

                print(f'[Banqueiro][Retornar][Loja] - Retornando loja...')
                return loja.to_dict()
            else:
                print(f'[Banqueiro][Retornar][Loja] - Loja não encontrada!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][Loja][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarMinhaLoja(self, id):
        try:
            print(f'[Banqueiro][Retornar][MinhaLoja] - Iniciando tentativa de retornar loja...')
            if result := self.__daoLoja.select(Loja(id= id), logic= 'AND'):
                loja = result[0]
                if imageu.seExisteImagem('loja', f'{loja.id}.jpg'):
                    loja.imagem = f'{loja.id}.jpg'
                print(f'[Banqueiro][Retornar][MinhaLoja] - Loja recuperada:', loja)
                
                produtos_da_loja = []
                print(f'[Banqueiro][Retornar][MinhaLoja] - Recuperando produtos da loja...')
                produtos_da_loja += self.__daoProduto.select(Produto(loja = loja))
                for produto in produtos_da_loja:
                    produto.imagens = [imagem_produto.caminho() for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = produto.id))]


                anuncios_da_loja = []
                print(f'[Banqueiro][Retornar][MinhaLoja] - Recuperando anúncios da loja...')
                anuncios_da_loja += self.__daoAnuncio.select(Anuncio(produto= Produto(loja= loja)))
                for anuncio in anuncios_da_loja:
                    anuncio.produto.imagens = [imagem_produto.caminho() for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto = anuncio.produto.id))] 
                
                pedidos_em_andamento = []
                print(f'[Banqueiro][Retornar][MinhaLoja] - Recuperando pedidos em andamento...')
                pedidos_em_andamento = self.__daoPedido_Andamento.select( Pedido(id_loja= loja.id))
                pedidos_confirmados = []
                print(f'[Banqueiro][Retornar][MinhaLoja] - Recuperando pedidos confirmados...')
                pedidos_confirmados = self.__daoPedido_Confirmado.select( Pedido(id_loja= loja.id))
                
                loja.anuncios = anuncios_da_loja
                loja.produtos = produtos_da_loja
                loja.pedidos_em_andamento = pedidos_em_andamento
                loja.pedidos_confirmados = pedidos_confirmados
                print(f'[Banqueiro][Retornar][MinhaLoja] - Loja recuperada + produtos + anúncios + pedidos:', loja)
                
                print(f'[Banqueiro][Retornar][MinhaLoja] - Retornando loja...')
                return loja.to_dict()
            else:
                print(f'[Banqueiro][Retornar][MinhaLoja] - Loja não encontrada!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][MinhaLoja][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarMinhasLojas(self, id):
        try:
            print(f'[Banqueiro][Retornar][MinhasLojas] - Iniciando tentativa de retornar lojas...')
            minhasLojas = self.__daoLoja.select(Loja(id_usuario= id))
            for loja in minhasLojas:
                if imageu.seExisteImagem('loja', f'{loja.id}.jpg'):
                    loja.imagem = f'{loja.id}.jpg'
            print(f'[Banqueiro][Retornar][MinhasLojas] - Lojas recuperadas:', minhasLojas)
            print(f'[Banqueiro][Retornar][MinhasLojas] - Retornando lojas...')
            return [loja.to_dict() for loja in minhasLojas]
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][MinhasLojas][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
        
    def retornarMeusEnderecos(self, id):
        try:
            print(f'[Banqueiro][Retornar][MeusEnderecos] - Iniciando tentativa de retornar endereços...')
            meusEnderecos = self.__daoEndereco.select(Endereco(id_usuario= id))
            print(f'[Banqueiro][Retornar][MeusEnderecos] - Endereços recuperados:', meusEnderecos)
            print(f'[Banqueiro][Retornar][MeusEnderecos] - Retornando endereços...')
            return [endereco.to_dict() for endereco in meusEnderecos]
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][MeusEnderecos][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarMeusPedidos(self, id):
        try:
            print(f'[Banqueiro][Retornar][MeusPedidos] - Iniciando tentativa de retornar pedidos...')

            print(f'[Banqueiro][Retornar][MeusPedidos] - Recuperando pedidos em andamento...')
            meusPedidos_Andamento = self.__daoPedido_Andamento.select(Pedido(endereco= Endereco(id_usuario= id)))
            print(f'[Banqueiro][Retornar][MeusPedidos] - Pedidos recuperados:', meusPedidos_Andamento)
            
            print(f'[Banqueiro][Retornar][MeusPedidos] - Recuperando pedidos confirmados...')
            meusPedidos_Confirmado = self.__daoPedido_Confirmado.select(Pedido(endereco= Endereco(id_usuario= id)))
            print(f'[Banqueiro][Retornar][MeusPedidos] - Pedidos recuperados:', meusPedidos_Confirmado)

            print(f'[Banqueiro][Retornar][MeusPedidos] - Retornando pedidos...')
            return [pedido.to_dict() for pedido in meusPedidos_Andamento], [pedido.to_dict() for pedido in meusPedidos_Confirmado]
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][MeusPedidos][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarCompradorPedido(self, id_pedido: int):
        try:
            print(f'[Banqueiro][Retornar][CompradorPedido] - Iniciando tentativa de retornar comprador do pedido {id_pedido}...')
            if result := self.__daoPedido_Andamento.select(Pedido(id= id_pedido), logic= 'AND'):
                pedido = result[0]
                print(f'[Banqueiro][Retornar][CompradorPedido] - Pedido recuperado:', pedido)
                if isinstance(pedido.endereco, Endereco):
                    print(f'[Banqueiro][Retornar][CompradorPedido] - Recuperando comprador do pedido recuperado...')
                    if result := self.__daoUsuario.select(Usuario_Identificado(id= pedido.endereco.id_usuario), logic= 'AND'):
                        comprador = result[0]
                        print(f'[Banqueiro][Retornar][CompradorPedido] - Comprador recuperado:', comprador)
                        return comprador.to_dict()
                    else:
                        print(f'[Banqueiro][Retornar][CompradorPedido] - Usuário não encontrado!')
                        return False
                else:
                    print(f'[Banqueiro][Retornar][CompradorPedido] - Falha fatal: Pedido não possui Endereço!')
                    return False
            else:
                print(f'[Banqueiro][Retornar][CompradorPedido] - Pedido não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][CompradorPedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def retornarVendedorPedido(self, id_pedido: int):
        try:
            print(f'[Banqueiro][Retornar][VendedorPedido] - Iniciando tentativa de retornar vendedor do pedido {id_pedido}...')
            if result := self.__daoPedido_Andamento.select(Pedido(id= id_pedido), logic= 'AND'):
                pedido = result[0]
                print(f'[Banqueiro][Retornar][VendedorPedido] - Pedido recuperado:', pedido)
                if isinstance(pedido.anuncio, Anuncio):
                    if isinstance(pedido.anuncio.produto, Produto):
                        if isinstance(pedido.anuncio.produto.loja, Loja):
                            print(f'[Banqueiro][Retornar][VendedorPedido] - Recuperando loja do produto do pedido recuperado...')
                            if result := self.__daoLoja.select(Loja(id= pedido.anuncio.produto.loja.id), logic= 'AND'):
                                loja = result[0]
                                pedido.anuncio.produto.loja = loja
                                print(f'[Banqueiro][Retornar][VendedorPedido] - Loja recuperada:', pedido.anuncio.produto.loja)
                                
                                print(f'[Banqueiro][Retornar][VendedorPedido] - Recuperando vendedor da loja recuperado...')
                                if result := self.__daoUsuario.select(Usuario_Identificado(id= pedido.anuncio.produto.loja.id_usuario), logic= 'AND'):
                                    vendedor = result[0]
                                    print(f'[Banqueiro][Retornar][VendedorPedido] - Vendedor recuperado:', vendedor)
                                    return vendedor.to_dict()
                                else:
                                    print(f'[Banqueiro][Retornar][VendedorPedido] - Usuário não encontrado!')
                                    return False
                            else:
                                print(f'[Banqueiro][Retornar][VendedorPedido] - Usuário não encontrado!')
                                return False
                        else:
                            print(f'[Banqueiro][Retornar][VendedorPedido] - Falha fatal: Produto do Anúncio do Pedido não possui Loja!')
                            return False
                    else:
                        print(f'[Banqueiro][Retornar][VendedorPedido] - Falha fatal: Anúncio do Pedido não possui Produto!')
                        return False
                else:
                    print(f'[Banqueiro][Retornar][VendedorPedido] - Falha fatal: Pedido não possui Anúncio!')
                    return False
            else:
                print(f'[Banqueiro][Retornar][VendedorPedido] - Pedido não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Retornar][VendedorPedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    ################################### Editar ###################################

    def editarUsuario(self, usuario: dict):
        try:
            print(f'[Banqueiro][Editar][Usuário] - Iniciando tentativa de editar usuário...')
            obj = Usuario_Identificado.from_dict(usuario)
            print('[Banqueiro][Editar][Usuário] - Usuário a editar:', obj)
            result = self.confereUsuario(usuario)
            if result == True:
                print('[Banqueiro][Editar][Usuário] - Usuário não ameaça integridade do banco de dados.')
                print('[Banqueiro][Editar][Usuário] - Editando usuário...')
                if obj := self.__daoUsuario.update(obj):
                    print('[Banqueiro][Editar][Usuário] - Retornando usuário modificado...')
                    return obj.to_dict()
                else:
                    print('[Banqueiro][Editar][Usuário] - Algo saiu mal.')
            elif isinstance(result, list):
                print('[Banqueiro][Editar][Usuário] - Retornando motivos de incompatibilidade...')
                return result
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Editar][Usuário][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def editarEndereco(self, endereco: dict):
        try:
            print(f'[Banqueiro][Editar][Endereço] - Iniciando tentativa de editar endereço...')
            obj = Endereco.from_dict(endereco)
            print('[Banqueiro][Editar][Endereço] - Endereço a editar:', obj)
            if obj := self.__daoEndereco.update(obj):
                print('[Banqueiro][Editar][Endereço] - Retornando endereço modificado...')
                return obj.to_dict()
            else:
                print('[Banqueiro][Editar][Endereço] - Algo saiu mal.')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Editar][Endereço][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def editarLoja(self, loja: dict, imagem= None):
        try:
            print('[Banqueiro][Editar][Loja] - Iniciando tentativa de editar loja...')
            print('[Banqueiro][Editar][Loja] - Loja a editar:', loja)
            if 'id' in loja:
                if 'imagem' in loja:
                    if loja['imagem']:
                        if imagem is not None:
                            print('[Banqueiro][Editar][Loja] - Editando imagem...')
                            loja['imagem'] = f"{loja['id']}.jpg"
                            imageu.salvarImagem('loja', loja['imagem'], imagem)
                        else:
                            print('[Banqueiro][Retornar][Anúncio] - Falha fatal: Imagem nula!')
                            return False
                    else:
                        print('[Banqueiro][Editar][Loja] - Excluindo imagem...')
                        if not imageu.apagarImagem('loja', f"{loja['id']}.jpg"):
                            print('[Banqueiro][Editar][Loja] - Falha fatal: Tentativa de excluir imagem de loja sem imagem!')
                            return False
            else:
                print('[Banqueiro][Editar][Loja] - Falha fatal: Loja sem id!')
                return False
            if 'nome' in loja:
                print('[Banqueiro][Editar][Loja] - Editando loja...')
                obj = self.__daoLoja.update(Loja.from_dict(loja))
                if not obj:
                    print('[Banqueiro][Editar][Loja] - Algo saiu mal.')
                    return False
            print('[Banqueiro][Editar][Loja] - Retornando loja modificada...')
            return loja, imagem
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Editar][Loja][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
        
    def editarProduto(self, produto: dict):
        try:
            print(f'[Banqueiro][Editar][Produto] - Iniciando tentativa de editar produto...')
            obj = Produto.from_dict(produto)
            print('[Banqueiro][Editar][Produto] - Produto a editar:', obj)

            print('[Banqueiro][Editar][Produto] - Verificando se há anúncios sobre o produto com pedidos ainda em andamento...')
            if pedidos := self.__daoPedido_Andamento.select(Pedido(id_produto= obj.id)):
                print(f'[Banqueiro][Editar][Produto] - Produto não pode ser editado: {len(pedidos)} pedidos em andamneto!')
                return 'pedidos_pendentes'
            else:
                if obj := self.__daoProduto.update(obj):
                    print('[Banqueiro][Editar][Produto] - Retornando produto modificado...')
                    return obj.to_dict()
                else:
                    print('[Banqueiro][Editar][Produto] - Algo saiu mal.')
                    return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Editar][Produto][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
        
    def editarAnuncio(self, anuncio: dict):
        try:
            print(f'[Banqueiro][Editar][Anúncio] - Iniciando tentativa de editar anúncio...')
            obj = Anuncio.from_dict(anuncio)
            print('[Banqueiro][Editar][Anúncio] - Anúncio a editar:', obj)

            if 'preco' in anuncio:
                print('[Banqueiro][Editar][Anúncio] - Edição de preço detectada.')
                print('[Banqueiro][Editar][Anúncio] - Verificando se o anúncio ainda possui pedidos em andamento...')
                if pedidos := self.__daoPedido_Andamento.select(Pedido(anuncio= Anuncio(id= obj.id))):
                    print(f'[Banqueiro][Editar][Anúncio] - Preço do anúncio não pode ser editado: {len(pedidos)} pedidos em andamneto!')
                    return 'pedidos_pendentes'
                
            if obj := self.__daoAnuncio.update(obj):
                print('[Banqueiro][Editar][Anúncio] - Retornando anúncio modificado...')
                return obj.to_dict()
            else:
                print('[Banqueiro][Editar][Anúncio] - Algo saiu mal.')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Editar][Anúncio][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    ################################### Confirmar ###################################

    def confirmarPedido(self, id: int):
        try:
            print('[Banqueiro][Confirmar][Pedido] - Iniciando tentativa de confirmar pedido...')
            print('[Banqueiro][Confirmar][Pedido] - Recuperando todos os dados do pedido em andamento...')
            if result := self.__daoPedido_Andamento.select(Pedido(id= id)):
                pedido = result[0]
                print('[Banqueiro][Confirmar][Pedido] - Pedido recuperando!')
                print('[Banqueiro][Confirmar][Pedido] - Recuperando imagens do pedido...')
                if isinstance(pedido.anuncio, Anuncio):
                    if isinstance(pedido.anuncio.produto, Produto):
                        pedido.anuncio.produto.imagens = self.__daoImagem_Produto.select(Imagem_Produto(id_produto = pedido.anuncio.produto.id))
                    else:
                        print(f'[Banqueiro][Confirmar][Pedido] - Falha fatal: Anúncio do pedido não possui produto!')
                        return False
                else:
                    print(f'[Banqueiro][Confirmar][Pedido] - Falha fatal: Pedido não possui anúncio!')
                    return False
                print('[Banqueiro][Confirmar][Pedido] - Pedido a confirmar:', pedido)
            else:
                print(f'[Banqueiro][Confirmar][Pedido] - Falha fatal: Pedido não encontrado!')
                return False
            print('[Banqueiro][Confirmar][Pedido] - Confirmando pedido...')
            pedido.id = self.__daoPedido_Confirmado.insert(pedido)
            if self.__daoPedido_Andamento.delete(Pedido(id= pedido.id)):
                print('[Banqueiro][Confirmar][Pedido] - Pedido confirmado!')
                return True
            else:
                print('[Banqueiro][Confirmar][Pedido] - Algo saiu mal: Pedido não cancelado.')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Confirmar][Pedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    ################################### Cancelar ###################################

    def cancelarPedido(self, id: int):
        try:
            print('[Banqueiro][Cancelar][Pedido] - Iniciando tentativa de cancelar pedido...')
            if result := self.__daoPedido_Andamento.select(Pedido(id= id)):
                pedido = result[0]
                print('[Banqueiro][Cancelar][Pedido] - Pedido a cancelar:', pedido)

                print('[Banqueiro][Cancelar][Pedido] - Retornando quantidade do pedido ao anúncio...')
                if isinstance(pedido.anuncio, Anuncio):
                    self.__daoAnuncio.update(Anuncio(id= pedido.anuncio.id, quantidade_disponivel= pedido.anuncio.quantidade_disponivel+pedido.quantidade))
                    print('[Banqueiro][Cancelar][Pedido] - Anúncio do pedido atualizado!')

                    if self.__daoPedido_Andamento.delete(Pedido(id= id)):
                        print('[Banqueiro][Cancelar][Pedido] - Pedido cancelado!')
                        return True
                    else:
                        print('[Banqueiro][Cancelar][Pedido] - Algo saiu mal: Pedido não cancelado.')
                        return False
                    
                else:
                    print(f'[Banqueiro][Cancelar][Pedido] - Falha fatal: Pedido não possui anúncio!')
                    return False
                
            else:
                print(f'[Banqueiro][Cancelar][Pedido] - Falha fatal: Pedido não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Cancelar][Pedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    ################################### Excluir ###################################

    def excluirImagemProduto(self, nome_imagem: str):
        try:
            print(f'[Banqueiro][Excluir][Imagem] - Iniciando tentativa de excluir imagem de produto...')
            obj = Imagem_Produto.from_name(nome_imagem)
            print('[Banqueiro][Excluir][Imagem] - Imagem a excluir:', obj)
            if self.__daoImagem_Produto.delete(Imagem_Produto(id= obj.id)):
                print('[Banqueiro][Excluir][Imagem] - Registro da imagem excluído!')
                print('[Banqueiro][Excluir][Imagem] - Excluindo imagem...')
                if imageu.apagarImagem('produto', nome_imagem):
                    print('[Banqueiro][Excluir][Imagem] - Imagem excluída!')
                    return True
                else:
                    print('[Banqueiro][Excluir][Imagem] - Falha fatal: Imagem não pôde ser excluída!')
                    return False
            else:
                print('[Banqueiro][Excluir][Imagem] - Falha fatal: Registro da imagem não pôde ser excluído!')
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Imagem][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def excluirAnuncio(self, id: int):
        try:
            print('[Banqueiro][Excluir][Anúncio] - Iniciando tentativa de excluir anúncio...')
            if result := self.__daoAnuncio.select(Anuncio(id= id)):
                obj = result[0]
                print('[Banqueiro][Excluir][Anúncio] - Anúncio a excluir:', obj)

                print('[Banqueiro][Excluir][Anúncio] - Verificando se o anúncio ainda possui pedidos em andamento...')
                if pedidos := self.__daoPedido_Andamento.select(Pedido(anuncio= Anuncio(id= obj.id))):
                    print(f'[Banqueiro][Excluir][Anúncio] - Anúncio não pode ser excluído: {len(pedidos)} pedidos em andamneto!')
                    return 'pedidos_pendentes'
                else:
                    print('[Banqueiro][Excluir][Anúncio] - Excluindo anúncio...')
                    if self.__daoAnuncio.delete(Anuncio(id= obj.id)):
                        print('[Banqueiro][Excluir][Anúncio] - Anúncio excluído!')
                        return True
                    else:
                        print('[Banqueiro][Excluir][Anúncio] - Falha fatal: Anúncio não pôde ser excluído!')
                        return False
            else:
                print('[Banqueiro][Excluir][Anúncio] - Falha fatal: Anúncio não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Anúncio][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def excluirProduto(self, id: int):
        try:
            print('[Banqueiro][Excluir][Produto] - Iniciando tentativa de excluir produto...')
            if result := self.__daoProduto.select(Produto(id= id)):
                obj = result[0]
                print('[Banqueiro][Excluir][Produto] - Produto a excluir:', obj)

                print('[Banqueiro][Excluir][Produto] - Verificando se há anúncios sobre o produto com pedidos ainda em andamento...')
                if pedidos := self.__daoPedido_Andamento.select(Pedido(id_produto= obj.id)):
                    print(f'[Banqueiro][Excluir][Produto] - Produto não pode ser excluído: {len(pedidos)} pedidos em andamneto!')
                    return 'pedidos_pendentes'
                else:
                    print('[Banqueiro][Excluir][Produto] - Excluindo anúncios do produto...')
                    if self.__daoAnuncio.delete(Anuncio(produto= Produto(id= obj.id))):
                        print('[Banqueiro][Excluir][Produto] - Anúncios excluídos!')
                    else:
                        print('[Banqueiro][Excluir][Produto] - Falha fatal: Anúncios do produto não puderam ser excluídos!')
                        return False
                    
                    print('[Banqueiro][Excluir][Produto] - Excluindo imagens do produto...')
                    for imagem_produto in self.__daoImagem_Produto.select(Imagem_Produto(id_produto= obj.id)):
                        if not self.excluirImagemProduto(imagem_produto.caminho()):
                            print('[Banqueiro][Excluir][Produto] - Falha fatal: Imagem do produto não pôde ser excluído!')
                            return False
                    print('[Banqueiro][Excluir][Produto] - Imagens excluídas!')

                    if self.__daoProduto.delete(Produto(id= obj.id)):
                        print('[Banqueiro][Excluir][Produto] - Produto excluído!')
                        return True
                    else:
                        print('[Banqueiro][Excluir][Produto] - Falha fatal: Produto não pôde ser excluído!')
                        return False
            else:
                print('[Banqueiro][Excluir][Produto] - Falha fatal: Produto não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Produto][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False
    
    def excluirEndereco(self, id: int):
        try:
            print('[Banqueiro][Excluir][Endereço] - Iniciando tentativa de excluir endereço...')
            if result := self.__daoEndereco.select(Endereco(id= id)):
                obj = result[0]
                print('[Banqueiro][Excluir][Endereço] - Endereço a excluir:', obj)

                print('[Banqueiro][Excluir][Endereço] - Verificando se há pedidos em andamento para este endereço...')
                if pedidos := self.__daoPedido_Andamento.select(Pedido(endereco= Endereco(id= obj.id))):
                    print(f'[Banqueiro][Excluir][Endereço] - Endereço não pode ser excluído: {len(pedidos)} pedidos em andamneto!')
                    return 'pedidos_pendentes'
                else:
                    if self.__daoEndereco.delete(Endereco(id= obj.id)):
                        print('[Banqueiro][Excluir][Endereço] - Endereço excluído!')
                        return True
                    else:
                        print('[Banqueiro][Excluir][Endereço] - Falha fatal: Endereço não pôde ser excluído!')
                        return False
            else:
                print('[Banqueiro][Excluir][Endereço] - Falha fatal: Endereço não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Endereço][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def excluirLoja(self, id: int):
        try:
            print('[Banqueiro][Excluir][Loja] - Iniciando tentativa de excluir loja...')
            if result := self.__daoLoja.select(Loja(id= id)):
                obj = result[0]
                print('[Banqueiro][Excluir][Loja] - Loja a excluir:', obj)

                print('[Banqueiro][Excluir][Loja] - Verificando se a loja possui pedidos em andamento...')
                if pedidos := self.__daoPedido_Andamento.select(Pedido(id_loja= obj.id)):
                    print(f'[Banqueiro][Excluir][Loja] - Loja não pode ser excluída: {len(pedidos)} pedidos em andamneto!')
                    return 'pedidos_pendentes'
                else:
                    print('[Banqueiro][Excluir][Loja] - Excluindo produtos da loja...')
                    for produto in self.__daoProduto.select(Produto(loja= Loja(id= obj.id))):
                        result = self.excluirProduto(produto.id)
                        if result == 'pedidos_pendentes':
                            print(f'[Banqueiro][Excluir][Loja] - Falha fatal: Produto {produto.id} possui pedidos em andamento!')
                            return 'pedidos_pendentes'
                        elif result is False:
                            print(f'[Banqueiro][Excluir][Loja] - Falha fatal: Produto {produto.id} não pôde ser excluído!')
                            return False
                    
                    print('[Banqueiro][Excluir][Loja] - Excluindo loja...')
                    if self.__daoLoja.delete(Loja(id= obj.id)):
                        print('[Banqueiro][Excluir][Loja] - Loja excluída!')
                        self._excluirPedidosEsquecidos()
                        return True
                    else:
                        print('[Banqueiro][Excluir][Loja] - Falha fatal: Loja não pôde ser excluída!')
                        return False
            else:
                print('[Banqueiro][Excluir][Loja] - Falha fatal: Loja não encontrada!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Loja][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def excluirUsuario(self, id: int):
        try:
            print('[Banqueiro][Excluir][Usuário] - Iniciando tentativa de excluir usuário...')
            if result := self.__daoUsuario.select(Usuario_Identificado(id= id)):
                obj = result[0]
                print('[Banqueiro][Excluir][Usuário] - Usuário a excluir:', obj)

                print('[Banqueiro][Excluir][Usuário] - Tentando excluir lojas do usuário...')
                for loja in self.__daoLoja.select(Loja(id_usuario= obj.id)):
                    print(f'[Banqueiro][Excluir][Usuário] - Excluindo loja {loja.id}...')
                    result = self.excluirLoja(loja.id)
                    if result == 'pedidos_pendentes':
                        print(f'[Banqueiro][Excluir][Usuário] - Falha fatal: Loja {loja.id} possui pedidos em andamento!')
                        return 'pedidos_pendentes'
                    elif result is False:
                        print(f'[Banqueiro][Excluir][Usuário] - Falha fatal: Loja {loja.id} não pôde ser excluída!')
                        return False

                print('[Banqueiro][Excluir][Usuário] - Tentando excluir endereços do usuário...')
                for endereco in self.__daoEndereco.select(Endereco(id_usuario= obj.id)):
                    print(f'[Banqueiro][Excluir][Usuário] - Excluindo endereço {endereco.id}...')
                    result = self.excluirEndereco(endereco.id)
                    if result == 'pedidos_pendentes':
                        print(f'[Banqueiro][Excluir][Usuário] - Falha fatal: Endereço {endereco.id} possui pedidos em andamento!')
                        return 'pedidos_pendentes'
                    elif result is False:
                        print(f'[Banqueiro][Excluir][Usuário] - Falha fatal: Endereço {endereco.id} não pôde ser excluído!')
                        return False
                
                print('[Banqueiro][Excluir][Usuário] - Excluindo usuário...')
                if self.__daoUsuario.delete(Usuario_Identificado(id= obj.id)):
                    print('[Banqueiro][Excluir][Usuário] - Usuário excluído!')
                    self._excluirPedidosEsquecidos()
                    return True
                else:
                    print('[Banqueiro][Excluir][Usuário] - Falha fatal: Usuário não pôde ser excluído!')
                    return False
            else:
                print('[Banqueiro][Excluir][Usuário] - Falha fatal: Usuário não encontrado!')
                return False
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Excluir][Usuário][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False

    def _excluirPedidosEsquecidos(self):
        try:
            print('[Banqueiro][Esquecer][Pedido] - Iniciando limpeza de pedidos esquecidos...')
            for imagem_a_apagar in self.__daoPedido_Confirmado.cleanForgotten():
                if not imageu.apagarImagem('pedido', imagem_a_apagar):
                    print('[Banqueiro][Esquecer][Pedido] - Falha fatal: Não foi possível excluir', imagem_a_apagar)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            linha = tb[-1].lineno if tb else '[linha desconhecida]'
            tipo = type(e).__name__
            mensagem = str(e)
            print(f'[Banqueiro][Esquecer][Pedido][ERRO] - Exceção na linha {linha}: {tipo} - {mensagem}')
            return False