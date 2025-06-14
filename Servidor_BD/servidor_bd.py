import Pyro5.api
import Pyro5.server
import Pyro5.errors
import Pyro5.nameserver
from banqueiro import Banqueiro

ip = '192.168.1.17'
porta = 5000
try:
    nameServer = Pyro5.api.locate_ns(host=ip, port=porta)
    print("Name Server localizado.")

except Pyro5.errors.NamingError:
    print(f"Name Server não encontrado. Iniciando um novo...")
    Pyro5.nameserver.start_ns_loop()

print("É ali em baixo.")
with Pyro5.server.Daemon(host= '192.168.1.15') as daemon:
    banqueiro = Banqueiro()
    uri = daemon.register(banqueiro)

    nameServer.register("Caldeirao:servicos.banqueiro", uri)
    print(f"Serviço registrado com URI: {uri}")

    print("Servidor aguardando chamadas remotas...")
    daemon.requestLoop()