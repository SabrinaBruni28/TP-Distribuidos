import sys
import Pyro5.api
import Pyro5.server
import Pyro5.errors
import Pyro5.nameserver
from banqueiro import Banqueiro

if len(sys.argv) > 1:
    ip = sys.argv[1]
    porta = int(sys.argv[2])
else:
    ip = "127.0.0.1"
    porta = 9090
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