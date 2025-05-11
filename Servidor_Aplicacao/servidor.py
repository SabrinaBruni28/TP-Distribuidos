import socket
import threading
import logging
from Operacoes import server_operation as op
from queue import Queue, Empty
from Operacoes import Login, Cadastramento, Visualizar, Editar, Criar, Apagar, Pedido

logging.basicConfig(level=logging.INFO, format='%(message)s')

class Mensagem():
    def __init__(self, mensagem):
        self.stringMensagem = mensagem
        self.camposMensagem = self.divideString()
        self.tamanho = len(self.camposMensagem)

    def divideString(self):
        return [ws.strip() for ws in self.stringMensagem.split('|')]


class FilaDeMensagens(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self.socketBD = None


    def enfileira(self, mensagem, callback, conexao):
        self._fila.put((mensagem, callback, conexao))


    def desenfileira(self):
        try:
            return self._fila.get()
        except Empty:
            return None
        
        
    def vazia(self):
        return self._fila.empty()
    

    def tamanho(self):
        return self._fila.qsize()
    
    
    def conectaBanco(self):
        try:
            self.socketBD = socket.create_connection(('192.168.1.107', 6000))
            logging.info("[Fila de Mensagens] Conectado ao Banco de Dados.")
        
        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro ao conectar ao Banco de Dados: {e}")
            self.socketBD = None
    

    def enviaAoBanco(self, mensagem):
        try:
            if self.socketBD is None:
                self.conectaBanco()

            if self.socketBD:
                self.socketBD.sendall(mensagem)
                resposta = self.socketBD.recv(2048)
                return op.carrega(resposta)
            
            else:
                return "[Erro] Conexão com Banco de Dados não estabelecida"

        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro na conexão com Banco de Dados: {e}")
            self.socketBD = None
            return f"[Erro] Falha ao enviar ao banco: {e}"
        

    def run(self):
        while True:
            try:
                mensagem, callback, connect = self.desenfileira()
            except ValueError:
                logging.info("[Fila de mensagens] Erro: tupla mal formada na fila.")
                continue

            if mensagem and callback:
                logging.info("[Fila de Mensagem] Processando uma requisição da fila...")
                resposta = self.enviaAoBanco(mensagem)
                callback(resposta, connect)

            else:
                logging.info("[Fila de mensagens] Erro ao obter callback.")


class ClientHandler(threading.Thread):
    def __init__(self, socket_servidor, socket_cliente, endereco, fila):
        super().__init__()
        self.socketCliente = socket_cliente
        self.socketServidor = socket_servidor
        self.enderecoCliente = endereco
        self.filaDeMensagem = fila
        self.ativo = True
        self.lock = threading.Lock()

    def run(self):
        logging.info(f"Cliente conectado: {self.enderecoCliente}")

        try:
            while self.ativo:
                stringMensagemCliente = op.decodifica(self.socketCliente)

                mensagemCliente = Mensagem(stringMensagemCliente)
                
                # Se o cliente fecho a conexão
                if not mensagemCliente or stringMensagemCliente == "":
                    break

                logging.info(f"[{self.enderecoCliente}] Comando: {mensagemCliente.stringMensagem}")

                # Comando de encerramento explícito
                if mensagemCliente.camposMensagem[0] == "fim":
                    self.socketCliente.sendall("closed".encode("utf-8")[:2048])
                    self.socketCliente.close()
                    return

                # Dispara thread para processar cada comando SEM quebrar o loop
                self.decisor(mensagemCliente)

        except Exception as e:
            logging.info(f"Erro com {self.enderecoCliente} - {e}")

        finally:
            self.socketCliente.close()
            return


    def decisor(self, mensagem):
        cabecalhoTipoMensagem = mensagem.camposMensagem[0]

        match cabecalhoTipoMensagem:
            case "login":
                Login()

            case "cadastramento":
                Cadastramento(mensagem, self.socketCliente, self.socketServidor, self.filaDeMensagem).run()

            case "visualizar":
                Visualizar(mensagem, self.socketCliente, self.filaDeMensagem).run()

            case "editar":
                Editar()

            case "criar":
                Criar()
            
            case "apagar":
                Apagar()

            case "pedido":
                Pedido()

            case _:
                logging.info("Comando inválido")
                return


def rodarServidor(endereco_ip, porta, fila):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Vinculação do socket servidor ao endereço e porta
        servidor.bind((endereco_ip, porta))

        # Listen para conexões
        servidor.listen()
        logging.info(f"Ouvindo em {endereco_ip}:{porta}")

        while True:
            # Aceita a conexão
            socketCliente, endereco = servidor.accept()

            # Começa uma nova thread para lidar com
            # este cliente
            ClientHandler(servidor, socketCliente, endereco, fila).start()
            

filaDeMensagem = FilaDeMensagens()
filaDeMensagem.start()

rodarServidor('192.168.1.102', 5000, filaDeMensagem)