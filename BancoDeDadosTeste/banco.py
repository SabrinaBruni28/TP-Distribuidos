import Pyro5.api
import Pyro5.errors
import Pyro5.nameserver
import Pyro5.server

@Pyro5.api.expose
class ServicosServidorBanco:

    @Pyro5.server.expose
    def login(self, dados):
        print(f"[Banco de Dados] Requisição de [Login] recebida: {dados}")
        arquivo = open("usuarios.txt", "r")
        linha = arquivo.readline()
        while linha != '':
            linha = linha.strip()
            print(f"[Banco de Dados] Comparando:\n[Banco de Dados] Dados recebidos - Dado na linha do arquivo: {dados} - {linha}")
            if linha == dados:
                print(f"[Banco de Dados] Login encontrado.")
                return linha
            
            linha = arquivo.readline()

        print(f"[Banco de Dados] Login não encontrado.")

try:
    ns = Pyro5.api.locate_ns()
    print("Name Server localizado.")

except Pyro5.errors.NamingError:
    print(f"Name Server não encontrado. Iniciando um novo...")
    Pyro5.nameserver.start_ns_loop()

with Pyro5.server.Daemon() as daemon:
    servicos = ServicosServidorBanco
    uri = daemon.register(servicos)

    ns.register("Caldeirao:servicos.banco", uri)
    print(f"Serviço registrado com URI: {uri}")

    print("Servidor aguardando chamadas remotas...")
    daemon.requestLoop()