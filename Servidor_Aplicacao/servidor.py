import sys
import time
import Pyro5.api
import Pyro5.server
import Pyro5.errors
from Estruturas.fila_de_requisicoes import FilaDeRequisicoes
from Operacoes.server_services import ServicosServidorAplicacao


# Valores padrão
ip = "127.0.0.1"
porta = 9090
host = "127.0.0.1"

def iniciar_servidorAP(ip, porta, host):
    print(f"Iniciando servidor Pyro5...")
    while True:
        try:
            ns = Pyro5.api.locate_ns(host=ip, port=porta)
            print("Name Server localizado.")
            break

        except Pyro5.errors.NamingError:
            print("Name Server não encontrado. Tentando novamente em 2 segundos...")
            time.sleep(2)

    filaDeMensagem = FilaDeRequisicoes(ip=ip, porta=porta)
    filaDeMensagem.start()

    with Pyro5.server.Daemon(host=host) as daemon:
        servicos = ServicosServidorAplicacao(filaDeMensagem)
        uri = daemon.register(servicos)

        ns.register("Caldeirao:servicos.servidor", uri)
        print(f"Serviço registrado com URI: {uri}")

        print("Servidor aguardando chamadas remotas...")
        daemon.requestLoop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        porta = int(sys.argv[2])
        host = sys.argv[3]
        
    iniciar_servidorAP(ip, porta, host)