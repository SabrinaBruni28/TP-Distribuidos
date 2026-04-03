import sys, time
import Pyro5.api
import Pyro5.server
import Pyro5.errors
from banqueiro import Banqueiro

ip = "127.0.0.1"
porta = 9090
host = "127.0.0.1"

def iniciar_servidorBD(ip, porta, host):
    while True:
        try:
            nameServer = Pyro5.api.locate_ns(host=ip, port=porta)
            print("Name Server localizado.")
            break

        except Pyro5.errors.NamingError:
            print("Name Server não encontrado. Tentando novamente em 2 segundos...")
            time.sleep(2)

    with Pyro5.server.Daemon(host=host) as daemon:
        banqueiro = Banqueiro()
        uri = daemon.register(banqueiro)

        nameServer.register("Caldeirao:servicos.banqueiro", uri)
        print(f"Serviço registrado com URI: {uri}")

        print("Servidor aguardando chamadas remotas...")
        daemon.requestLoop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        porta = int(sys.argv[2])
        host = sys.argv[3]
        
    iniciar_servidorBD(ip, porta, host)