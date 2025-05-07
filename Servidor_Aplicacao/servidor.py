import socket
import threading

class ClientHandler(threading.Thread):
    def __init__(self, socket_cliente, endereco):
        super().__init__()
        self.socketCliente = socket_cliente
        self.enderecoCliente = endereco
        self.ativo = True
        self.lock = threading.Lock()

    def inicio(self):
        print(f"Cliente conectado: {self.enderecoCliente}")

        try:
            while self.ativo:
                msgCliente = self.socketCliente.recv(2048).decode("utf-8")

                # Se o cliente fecho a conexão
                if not msgCliente:
                    break

                print(f"[{self.enderecoCliente}] Comando: {msgCliente}")

                # Comando de encerramento explícito
                if msgCliente.lower() == "fim":
                    self.socketCliente.sendall("Conexão encerrada.".encode("utf-8"))
                    break

                # Dispara thread para processar cada comando SEM quebrar o loop
                self.decisor(msgCliente)

        except Exception as e:
            print(f"Erro com {self.enderecoCliente} - {e}")

        finally:
            self.fim()

    def decisor(self, mensagem):
        match mensagem.lower():
            case "login":
                login()

            case "cadastramento":
                cadastramento()

            case "visualizar":
                visualizar()

            case "editar":
                editar()

            case "criar":
                criar()
            
            case "apagar":
                apagar()

            case "pedido":
                pedido()



def rodarServidor(endereco_ip, porta):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Vinculação do socket servidor ao endereço e porta
        servidor.bind((endereco_ip, porta))

        # Listen para conexões
        servidor.listen()
        print(f"Ouvindo em {endereco_ip}:{porta}")

        while True:
            # Aceita a conexão
            socketCliente, endereco = servidor.accept()

            # Começa uma nova thread para lidar com
            # este cliente
            ClientHandler(socketCliente, endereco).start()
