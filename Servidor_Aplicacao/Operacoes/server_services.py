import logging
import Pyro5.api
import Pyro5.server
from Operacoes import server_operation as op
from Operacoes.login import Login
from Operacoes.cadastramento import Cadastramento
from Operacoes.visualizar import Visualizar
from Operacoes.editar import Editar
from Operacoes.criar import Criar
from Operacoes.excluir import Excluir
from Operacoes.pedido import Pedido
from Operacoes.codigo import Codigo
from Operacoes.imagem import Imagem
from Estruturas.fila_de_requisicoes import FilaDeRequisicoes

logging.basicConfig(level=logging.INFO, format='%(message)s')

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class ServicosServidorAplicacao:
    """ Essa é a fachada do Servidor para os métodos expostos para o Cliente via Pyro5 """
    def __init__(self, fila: FilaDeRequisicoes):
        self.filaDeMensagens = fila

    # ========== Função relacionada à operação de Login =========
    @op.RetornaCorretamenteOuFalse
    def logar(self, dados):
        """ Função exposta via Pyro para o cliente realizar o login. Recebe os dados de login. """
        return Login(self.filaDeMensagens).logar(dados)
    # ==========================================================


    # ========== Funções relacionadas à operação de Cadastramento ==========
    @op.RetornaCorretamenteOuFalse
    def cadastrar(self, dados):
        """ Função exposta via Pyro para o cliente se cadastrar. Recebe os dados do cadastro. """
        return Cadastramento(self.filaDeMensagens).cadastrar(dados)

    @op.RetornaCorretamenteOuFalse
    def codigo(self, id_requisicao_cadastramento, codigo):
        """ Função exposta via Pyro para o cliente validar o código de confirmação.
            Recebe o código e o ID da requisição de cadastramento. """
        return Codigo(self.filaDeMensagens).codigo(codigo, id_requisicao_cadastramento)
    # ======================================================================

    # ========== Funções relacionadas à operação de Visualizar ==========
    @op.RetornaCorretamenteOuFalse
    def visualizarAnuncios(self):
        """ Função exposta via Pyro para o cliente visualizar todos os anúncios disponíveis. """
        return Visualizar(self.filaDeMensagens).todosAnuncios()

    @op.RetornaCorretamenteOuFalse
    def visualizarAnuncio(self, idAnuncio):
        """ Função exposta via Pyro para o cliente visualizar um anúncio específico. Recebe o ID do anúncio. """
        return Visualizar(self.filaDeMensagens).anuncio(idAnuncio)

    @op.RetornaCorretamenteOuFalse
    def visualizarProduto(self, idProduto):
        """ Função exposta via Pyro para o cliente visualizar os dados de um produto. Recebe o ID do produto. """
        return Visualizar(self.filaDeMensagens).produto(idProduto)

    @op.RetornaCorretamenteOuFalse
    def visualizarLoja(self, idLoja):
        """ Função exposta via Pyro para o cliente visualizar uma loja. Recebe o ID da loja. """
        return Visualizar(self.filaDeMensagens).loja(idLoja)

    @op.RetornaCorretamenteOuFalse
    def visualizarMinhaLoja(self, idLoja):
        """ Função exposta via Pyro para o cliente visualizar os dados da sua própria loja. Recebe o ID da loja. """
        return Visualizar(self.filaDeMensagens).minhaLoja(idLoja)

    @op.RetornaCorretamenteOuFalse
    def visualizarMinhasLojas(self, idUsuario):
        """ Função exposta via Pyro para o cliente visualizar a lista de suas lojas. Recebe o ID do usuário. """
        return Visualizar(self.filaDeMensagens).minhaListaLojas(idUsuario)

    @op.RetornaCorretamenteOuFalse
    def visualizarMeusEnderecos(self, idUsuario):
        """ Função exposta via Pyro para o cliente visualizar todos os seus endereços. Recebe o ID do usuário. """
        return Visualizar(self.filaDeMensagens).meusEnderecos(idUsuario)

    @op.RetornaCorretamenteOuFalse
    def visualizarPedido(self, idPedido):
        """ Função exposta via Pyro para o cliente visualizar os detalhes de um pedido. Recebe o ID do pedido. """
        return Visualizar(self.filaDeMensagens).pedido(idPedido)

    @op.RetornaCorretamenteOuFalse
    def visualizarMeusPedidos(self, idUsuario):
        """ Função exposta via Pyro para o cliente visualizar todos os seus pedidos. Recebe o ID do usuário. """
        return Visualizar(self.filaDeMensagens).meusPedidos(idUsuario)
    # ===================================================================

    # ========== Funções relacionadas à operação de Editar ==========
    @op.RetornaCorretamenteOuFalse
    def editarAnuncio(self, dados):
        """ Função exposta via Pyro para o cliente editar um anúncio. Recebe os dados do anúncio. """
        return Editar(self.filaDeMensagens).anuncio(dados)

    @op.RetornaCorretamenteOuFalse
    def editarProduto(self, dados):
        """ Função exposta via Pyro para o cliente editar um produto. Recebe os dados atualizados do produto. """
        return Editar(self.filaDeMensagens).produto(dados)

    @op.RetornaCorretamenteOuFalse
    def editarLoja(self, dados, imagem):
        """ Função exposta via Pyro para o cliente editar uma loja. Recebe os dados da loja e uma nova imagem (opcional). """
        return Editar(self.filaDeMensagens).loja(dados, imagem)

    @op.RetornaCorretamenteOuFalse
    def editarEndereco(self, dados):
        """ Função exposta via Pyro para o cliente editar um endereço. Recebe os dados do endereço. """
        return Editar(self.filaDeMensagens).endereco(dados)

    @op.RetornaCorretamenteOuFalse
    def editarUsuario(self, dados):
        """ Função exposta via Pyro para o cliente editar os dados do seu usuário. """
        return Editar(self.filaDeMensagens).usuario(dados)
    # ==============================================================


    # ========== Funções relacionadas à operação de Criar ==========
    @op.RetornaCorretamenteOuFalse
    def criarAnuncio(self, dados):
        """ Função exposta via Pyro para o cliente criar um anúncio. Recebe os dados do anúncio. """
        return Criar(self.filaDeMensagens).anuncio(dados)

    @op.RetornaCorretamenteOuFalse
    def criarProduto(self, dados, imagens):
        """ Função exposta via Pyro para o cliente criar um produto. Recebe os dados do produto e a(s) imagem(ens) dele. """
        return Criar(self.filaDeMensagens).produto(dados, imagens)

    @op.RetornaCorretamenteOuFalse
    def criarLoja(self, id_usuario, dados, imagem_loja= None):
        """ Função exposta via Pyro para o cliente criar uma loja. Recebe o id do usuário e os dados da loja.
            Uma loja pode possuir uma imagem, por isso a função recebe uma imagem (esse parâmetro pode estar vazio). """
        return Criar(self.filaDeMensagens).loja(id_usuario, dados, imagem_loja)

    @op.RetornaCorretamenteOuFalse
    def criarPedido(self, dados_pedido):
        """ Função exposta via Pyro para o cliente criar um endereço. Recebe o id do usuário e os dados do endereço. """
        return Criar(self.filaDeMensagens).pedido(dados_pedido)

    @op.RetornaCorretamenteOuFalse
    def criarEndereco(self, id_usuario, dados_endereco):
        """ Função exposta via Pyro para o cliente criar um endereço. Recebe o id do usuário e os dados do endereço. """
        return Criar(self.filaDeMensagens).endereco(id_usuario, dados_endereco)

    @op.RetornaCorretamenteOuFalse
    def criarImagem(self, id_produto, imagem):
        """ Função exposta via Pyro para o cliente criar a imagem de um produto. Recebe o id do produto e a imagem. """
        return Criar(self.filaDeMensagens).imagem(id_produto, imagem)
    # ================================================================


    # ========== Funções relacionadas à operação de Excluir ==========
    @op.RetornaCorretamenteOuFalse
    def excluirAnuncio(self, id_anuncio):
        """ Função exposta via Pyro para o cliente excluir um anúncio. Recebe apenas o id do anúncio. """
        return Excluir(self.filaDeMensagens).anuncio(id_anuncio)

    @op.RetornaCorretamenteOuFalse
    def excluirProduto(self, id_produto):
        """ Função exposta via Pyro para o cliente excluir um produto. Recebe apenas o id do produto. """
        return Excluir(self.filaDeMensagens).produto(id_produto)

    @op.RetornaCorretamenteOuFalse
    def excluirLoja(self, id_loja):
        """ Função exposta via Pyro para o cliente excluir uma loja. Recebe apenas o id da loja. """
        return Excluir(self.filaDeMensagens).loja(id_loja)

    @op.RetornaCorretamenteOuFalse
    def excluirEndereco(self, id_endereco):
        """ Função exposta via Pyro para o cliente excluir um endereço. Recebe apenas o id do endereço. """
        return Excluir(self.filaDeMensagens).endereco(id_endereco)

    @op.RetornaCorretamenteOuFalse
    def excluirImagem(self, nome_imagem):
        """ Função exposta via Pyro para o cliente excluir uma imagem. Recebe apenas o nome da imagem. """
        return Excluir(self.filaDeMensagens).imagem(nome_imagem)
    # ============================================================


    # ========== Funções de confirmar e cancelar Pedido ==========
    @op.RetornaCorretamenteOuFalse
    def confirmarPedido(self, id_pedido):
        """ Função exposta via Pyro para o cliente confirmar um pedido. Recebe apenas o id do pedido. """
        return Pedido(self.filaDeMensagens).confirmar(id_pedido)

    @op.RetornaCorretamenteOuFalse
    def cancelarPedido(self, id_pedido):
        """ Função exposta via Pyro para o cliente cancelar um pedido. Recebe apenas o id do pedido. """
        return Pedido(self.filaDeMensagens).cancelar(id_pedido)
    # ============================================================

    # ========== Funções que enviam imagens para o cliente ==========
    @op.RetornaCorretamenteOuFalse
    def imagemProduto(self, nome_imagem):
        """ Função exposta via Pyro para o cliente pedir a imagem de um produto. Recebe apenas o nome da imagem. """
        return Imagem(self.filaDeMensagens).produto(nome_imagem)

    @op.RetornaCorretamenteOuFalse
    def imagemLoja(self, nome_imagem):
        """ Função exposta via Pyro para o cliente pedir a imagem de uma loja. Recebe apenas o nome da imagem. """
        return Imagem(self.filaDeMensagens).loja(nome_imagem)

    @op.RetornaCorretamenteOuFalse
    def imagemPedido(self, nome_imagem):
        """ Função exposta via Pyro para o cliente pedir a imagem de um pedido. Recebe apenas o nome da imagem. """
        return Imagem(self.filaDeMensagens).pedido(nome_imagem)
    # ===============================================================