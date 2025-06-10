import socket
import threading
import logging
import Pyro5.api
import Pyro5.errors
import Pyro5.nameserver
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
from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2
from Estruturas.mensagem import Mensagem
from queue import Queue, Empty

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Esse wraper aqui é equivalente a ficar usando try: 
#                                                   função
#                                               exception:
#                                                   return False
# Fiz para a fachada ali ficar mais limpa
def RetornaCorretamenteOuFalse(funcao):
    def wrapper(*args, **kwargs):
        try:
            return funcao(*args, **kwargs)
        except Exception as e:
            print(f"[Servidor] Erro em {funcao.__name__}: {e}")
            return False
    return wrapper


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class ServicosServidorAplicacao:
    def __init__(self, fila: FilaDeMensagensV2):
        self.filaDeMensagens = fila

    @RetornaCorretamenteOuFalse
    def logar(self, dados):
        return Login(self.filaDeMensagens).logar(dados)
    
    @RetornaCorretamenteOuFalse
    def cadastrar(self, dados):
        return Cadastramento(self.filaDeMensagens).cadastrar(dados)
    
    @RetornaCorretamenteOuFalse
    def codigo(self, codigo, id):
        return Codigo(self.filaDeMensagens).codigo(codigo, id)
    
    @RetornaCorretamenteOuFalse
    def visualizarAnuncios(self):
        return Visualizar(self.filaDeMensagens).todosAnuncios()
    
    @RetornaCorretamenteOuFalse
    def visualizarAnuncio(self, idAnuncio):
        return Visualizar(self.filaDeMensagens).anuncio(idAnuncio)
    
    @RetornaCorretamenteOuFalse
    def visualizarProduto(self, idProduto):
        return Visualizar(self.filaDeMensagens).produto(idProduto)
    
    @RetornaCorretamenteOuFalse
    def visualizarLoja(self, idLoja):
        return Visualizar(self.filaDeMensagens).loja(idLoja)
    
    @RetornaCorretamenteOuFalse
    def visualizarMinhaLoja(self, idLoja):
        return Visualizar(self.filaDeMensagens).minhaLojaS(idLoja)
    
    @RetornaCorretamenteOuFalse
    def visualizarMinhasLojas(self, idUsuario):
        return Visualizar(self.filaDeMensagens).minhaListaLojas(idUsuario)
    
    @RetornaCorretamenteOuFalse
    def visualizarMeusEnderecos(self, idUsuario):
        return Visualizar(self.filaDeMensagens).meusEnderecos(idUsuario)
    
    @RetornaCorretamenteOuFalse
    def visualizarPedido(self, idPedido):
        return Visualizar(self.filaDeMensagens).pedido(idPedido)

    @RetornaCorretamenteOuFalse
    def visualizarMeusPedidos(self, idUsuario):
        return Visualizar(self.filaDeMensagens).meusPedidos(idUsuario)
    
    @RetornaCorretamenteOuFalse
    def editarAnuncio(self, dados):
        return Editar(self.filaDeMensagens).anuncio(dados)
    
    @RetornaCorretamenteOuFalse
    def editarProduto(self, dados):
        return Editar(self.filaDeMensagens).produto(dados)
    
    @RetornaCorretamenteOuFalse
    def editarLoja(self, dados, imagem):
        return Editar(self.filaDeMensagens).loja(dados, imagem)
    
    @RetornaCorretamenteOuFalse
    def editarEndereco(self, dados):
        return Editar(self.filaDeMensagens).endereco(dados)
    
    @RetornaCorretamenteOuFalse
    def editarUsuario(self, dados):
        return Editar(self.filaDeMensagens).usuario(dados)
    
    
    



print(f"Iniciando servidor Pyro5...")

filaDeMensagem = FilaDeMensagensV2()
filaDeMensagem.start()

ip = '192.168.1.4'
porta = 5000
try:
    ns = Pyro5.api.locate_ns(host=ip, port=porta)
    print("Name Server localizado.")

except Pyro5.errors.NamingError:
    print(f"Name Server não encontrado. Iniciando um novo...")
    Pyro5.nameserver.start_ns_loop()

print("É ali em baixo.")
with Pyro5.server.Daemon(host=ip) as daemon:
    servicos = ServicosServidorAplicacao(filaDeMensagem)
    print("É ali mais em baixo.")
    uri = daemon.register(servicos)

    ns.register("Caldeirao:servicos.servidor", uri)
    print(f"Serviço registrado com URI: {uri}")

    print("Servidor aguardando chamadas remotas...")
    daemon.requestLoop()