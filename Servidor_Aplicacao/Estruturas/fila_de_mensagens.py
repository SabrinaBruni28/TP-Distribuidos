import socket
import threading
import logging
from Estruturas.mensagem import Mensagem
from Operacoes import server_operation as op
from Operacoes import *
from Operacoes.login import Login
from queue import Queue, Empty



logging.basicConfig(level=logging.INFO, format='%(message)s')

# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
class FilaDeMensagens(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self.socketBD = None

    # A fila guarda a mensagem (como é o seu propósito),
    # Um callback (uma função que vai direcionar a mensagem do banco de dados para o cliente)
    # O socket do cliente -conexao-, que vai ser usado no callback para o retorno do banco ao cliente
    def enfileira(self, mensagem: Mensagem, callback, conexao, tipo=None, servidor=None):
        self._fila.put((mensagem, callback, conexao, tipo, servidor))


    def desenfileira(self):
        try:
            return self._fila.get()
        except Empty:
            return None
        
        
    def vazia(self):
        return self._fila.empty()
    

    def tamanho(self):
        return self._fila.qsize()
    
    # Função que faz a conexão com o servidor de banco de dados, cria seu socket
    def conectaBanco(self):
        try:
            self.socketBD = socket.create_connection(('localhost', 6001))
            logging.info(f"[Fila de Mensagens] Conectado ao Banco de Dados [localhost:6000].")
        
        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro ao conectar ao Banco de Dados: {e}")
            self.socketBD = None
    
    # Após uma mensagem ser desenfileirada, essa função é responsável por fazer
    # a parte da comunicação servidor de aplicação - servidor de banco de dados
    def enviaAoBanco(self, mensagem: Mensagem):
        print("[Fila de Mensagens] Passou daqui, tá?")
        try:
            # Se não há conexão com o banco de dados, cria seu socket e estabelece comunicação
            if self.socketBD is None:
                self.conectaBanco()

            # Envia a mensagem e retorna a resposta do banco
            if self.socketBD:
                self.socketBD.sendall(mensagem.tamanho.to_bytes(4, "big"))
                self.socketBD.sendall(mensagem.bytesMensagem)
                resposta = self.socketBD.recv(2048)
                return op.carrega(resposta)
            
            else:
                return "[Erro] Conexão com Banco de Dados não estabelecida"

        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro na conexão com Banco de Dados: {e}")
            self.socketBD = None
            return f"[Erro] Falha ao enviar ao banco: {e}"
        

    def run(self):
        # Enquanto o servidor estiver ativo, a fila vai desempilhando e transmitindo as mensagens
        # Se a fila estiver vazia, nada acontece.
        while True:
            try:
                mensagem, callback, connect, tipo, serverSocket = self.desenfileira()
            except ValueError:
                logging.info("[Fila de mensagens] Erro: tupla mal formada na fila.")
                continue

            if mensagem and callback and connect:
                self.decisor(mensagem, callback, connect, tipo, serverSocket)

            else:
                logging.info("[Fila de mensagens] Erro ao obter mensagem, callback ou connect.")


    def decisor(self, mensagem, callback, connect, tipo, serverSocket):
        logging.info("[Fila de Mensagem] Processando uma requisição da fila...")
        resposta = self.enviaAoBanco(mensagem)

        if callback is op.respostaAoCliente:
            callback(resposta, connect)

        elif callback is Login.loginCallback:
            callback(resposta, connect)

        elif callback is op.cadastramentoCallback:
            callback(resposta, connect, serverSocket)