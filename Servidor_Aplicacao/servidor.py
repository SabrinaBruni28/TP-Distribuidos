import socket
import threading
import logging
from Operacoes import server_operation as op
from Operacoes import Login, Cadastramento, Visualizar, Editar, Criar, Excluir, Pedido
from Estruturas import *
from queue import Queue, Empty


logging.basicConfig(level=logging.INFO, format='%(message)s')
        

# Várias instâncias de ClientHandler vão acontecer conforme clientes vão se conectando ao servidor.
class ClientHandler(threading.Thread):
    def __init__(self, socket_servidor, socket_cliente, endereco, fila: FilaDeMensagens):
        super().__init__()
        self.socketCliente = socket_cliente
        self.socketServidor = socket_servidor
        self.enderecoCliente = endereco
        self.filaDeMensagem = fila
        self.ativo = True
        # self.lock = threading.Lock()  # Os momentos que precisam de trava no servidor já têm ela
                                        # implementada por padrão. No caso, enfileirar mensagens
                                        # já tem sistema de lock implementados em Queue.

    # run vai ser executado logo após a thread ClientHandler ser disparada
    def run(self):
        logging.info(f"Cliente conectado: {self.enderecoCliente}")

        try:
            while self.ativo:
                # Recebe a mensagem do cliente e separa seus campos
                mensagemCliente = Mensagem.receptorMensagem(self.socketCliente)
                
                # Se o cliente fechou a conexão
                if not mensagemCliente or mensagemCliente.camposMensagem[0] == "":
                    self.ativo = False
                    break

                logging.info(f"[{self.enderecoCliente}] Comando: {mensagemCliente.stringMensagem}")

                # Comando de encerramento explícito
                if mensagemCliente.camposMensagem[0] == "fim":
                    self.socketCliente.sendall("closed".encode("utf-8")[:2048])
                    self.socketCliente.close()
                    self.ativo = False
                    break

                # Dispara thread para processar cada comando SEM quebrar o loop
                self.decisor(mensagemCliente)

        except Exception as e:
            logging.info(f"Erro com {self.enderecoCliente} - {e}")

        finally:
            self.socketCliente.close()


    def decisor(self, mensagem: Mensagem):
        cabecalhoTipoMensagem = mensagem.camposMensagem[0]

        match cabecalhoTipoMensagem:
            case "login":
                Login(mensagem, self.socketCliente, self.filaDeMensagem).start()

            case "cadastramento":
                Cadastramento(mensagem, self.socketCliente, self.socketServidor, self.filaDeMensagem).start()

            case "visualizar":
                Visualizar(mensagem, self.socketCliente, self.filaDeMensagem).start()

            case "editar":
                Editar(mensagem, self.socketCliente, self.socketServidor, self.filaDeMensagem).start()

            case "criar":
                Criar(mensagem, self.socketCliente, self.filaDeMensagem).start()
            
            case "excluir":
                Excluir(mensagem, self.socketCliente, self.filaDeMensagem).start()

            case "pedido":
                Pedido(mensagem, self.socketCliente, self.filaDeMensagem).start()

            case _:
                logging.info("Comando inválido")
                self.socketCliente.sendall("[Erro] Comando inválido.")
                return

def terminalServidor(flag_encerramento):
    while not flag_encerramento.is_set():
        comando = input()
        if comando.lower() in ("sair", "exit", "shutdown", "fim", "q"):
            print("[Servidor] Encerrando por comando.")
            flag_encerramento.set()

def conectaNovoCliente(servidor: socket.socket, fila: FilaDeMensagens):
    try:                                                                        #
        # Aceita a conexão (de um cliente)                                      #
        socketCliente, endereco = servidor.accept()                             #    Fluxo se repete
                                                                                #    para cada
        # Começa uma nova thread para lidar com esta conexão (desse cliente)    #    novo
        ClientHandler(servidor, socketCliente, endereco, fila).start()          #    cliente.
                                                                                #
    except socket.timeout:                                                      #
        pass                                                                    #

def rodarServidor(endereco_ip, porta, fila):
    # O terminal do servidor ficará aberto para receber comandos, assim é possível encerrar o
    # servidor pelo terminal do servidor sem necessitar do ctrl+c.
    flagEncerramento = threading.Event()
    threading.Thread(target=terminalServidor, args=(flagEncerramento, ), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Vinculação do socket servidor ao endereço e porta
        servidor.bind((endereco_ip, porta))

        # Listen para conexões
        servidor.listen()
        logging.info(f"Ouvindo em {endereco_ip}:{porta}")

        servidor.settimeout(0.2)

        # Enquanto o servidor não fecha, aceita novas conexões e cria novas thread para elas
        while not flagEncerramento.is_set():
            conectaNovoCliente(servidor, fila)

        
    print("[Servidor] Conexão encerrada.")

# ==== Execução do servidor ====

# Inicialização da Fila de Mensagens
filaDeMensagem = FilaDeMensagens()
filaDeMensagem.start()

# Inicialização do socket servidor
rodarServidor('localhost', 5000, filaDeMensagem)