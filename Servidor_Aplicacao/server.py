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
from Estruturas.fila_de_mensagens import FilaDeMensagens
from Estruturas.mensagem import Mensagem
from queue import Queue, Empty

logging.basicConfig(level=logging.INFO, format='%(message)s')

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class ServicosServidorAplicacao:
    def __init__(self, fila: FilaDeMensagens):
        self.filaDeMensagens = fila

    def logar(self, dados):
        return Login().logar()

print(f"Iniciando servidor Pyro5...")

filaDeMensagem = FilaDeMensagens()
filaDeMensagem.start()

try:
    ns = Pyro5.api.locate_ns()
    print("Name Server localizado.")

except Pyro5.errors.NamingError:
    print(f"Name Server não encontrado. Iniciando um novo...")
    Pyro5.nameserver.start_ns_loop()
    exit

with Pyro5.server.Daemon() as daemon:
    servicos = ServicosServidorAplicacao(filaDeMensagem)
    uri = daemon.register(servicos)

    ns.register("servicos.servidor", uri)
    print(f"Serviço registrado com URI: {uri}")

    print("Servidor aguardando chamadas remotas...")
    daemon.requestLoop()