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

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class ServicosServidorAplicacao:
    def __init__(self, fila: FilaDeMensagensV2):
        self.filaDeMensagens = fila

    def logar(self, dados):
        try:
            return Login(mensagem=dados, fila_mensagens=self.filaDeMensagens).logar(dados)
        except:
            return False
    
    def cadastrar(self, dados):
        try:
            return Cadastramento(mensagem=dados, fila_mensagens=self.filaDeMensagens).cadastrar(dados)
        except:
            return False
    
    def codigo(self, codigo, id):
        try:
            return Codigo(mensagem=codigo, fila_mensagens=self.filaDeMensagens).codigo(codigo, id)
        except:
            return False
    
    def visualizarAnuncios(self):
        try:
            return Visualizar(operacao="todos_anuncios", fila_mensagens=self.filaDeMensagens).run()
        except:
            return False


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