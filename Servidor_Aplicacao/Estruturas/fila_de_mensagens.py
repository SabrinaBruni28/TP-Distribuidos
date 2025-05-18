import socket
import threading
import logging
from Estruturas.mensagem import Mensagem
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Operacoes import server_operation as op
from queue import Queue, Empty
#from Operacoes.login import Login
from Operacoes import callback as cb



logging.basicConfig(level=logging.INFO, format='%(message)s')

# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
class FilaDeMensagens(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self.dadosTemp = DadosTemporariosConfirmacao()
        self.socketBD = None

    # A fila guarda a mensagem (como é o seu propósito),
    # Um callback (uma função que vai direcionar a mensagem do banco de dados para o cliente)
    # O socket do cliente -conexao-, que vai ser usado no callback para o retorno do banco ao cliente
    def enfileira(self, mensagem: Mensagem, callback, conexao, tipo=None, servidor=None, fila=None, imagem=None):
        self._fila.put((mensagem, callback, conexao, tipo, servidor, fila, imagem))


    def desenfileira(self):
        try:
            return self._fila.get()
        except Empty:
            return None
        
    # DecisorFilaDeMensages() é o método onde as mensagens do servidor são envidas ao banco de dados e o retorno ao cliente é processado.
    def decisorFilaDeMensagens(self, mensagem, callback, connect, tipo, serverSocket, fila, imagens):
        from Operacoes.cadastramento import Cadastramento

        logging.info("[Fila de Mensagem] Processando uma requisição da fila...")

        respostao = self.enviaAoBanco(mensagem)
        resposta = [ws.strip() for ws in respostao.split('|')]
        '''
        if imagens == None:
            respostao = self.enviaAoBanco(mensagem)
            resposta = [ws.strip() for ws in respostao.split('|')]
        else:
            resposta = self.mensagemProBancoCriar(mensagem, imagens)
            resposta = [ws.strip() for ws in respostao.split('|')]
        '''

        match tipo:
            case "visualizar":
                self.decisorVisualizar(resposta, connect, callback, self.socketBD)

            case "login":
                callback(resposta, connect)

            case "pedido":
                self.decisorPedido(resposta, connect, callback, mensagem)

            case "editar":
                print("[Retorno][Edição]")
                self.decisorEditar(resposta, connect, self.socketBD, callback, imagens=imagens)

            case "criar":
                self.decisorCriar(resposta, connect, callback, imagens)

            case "excluir":
                self.decisorExcluir(resposta, connect, callback)

            case "cadastramento":
                callback(resposta, connect, serverSocket, fila)
                
            case _:
                print("[Fila de Mensagens] Resposta do Banco de Dados não tratada.")
                return

    def run(self):
        # Enquanto o servidor estiver ativo, a fila vai desempilhando e transmitindo as mensagens ao banco de dados.
        # Se a fila estiver vazia, nada acontece.
        while True:
            try:
                mensagem, callback, connect, tipo, serverSocket, fila, imagens = self.desenfileira()
            except ValueError:
                logging.info("[Fila de mensagens] Erro: tupla mal formada na fila.")
                continue

            if mensagem and callback and connect:
                self.decisorFilaDeMensagens(mensagem, callback, connect, tipo, serverSocket, fila, imagens)

            else:
                logging.info("[Fila de mensagens] Erro ao obter mensagem, callback ou connect.")
    
    # Função que faz a conexão com o servidor de banco de dados, cria seu socket
    def conectaBanco(self):
        try:
            #self.socketBD = socket.create_connection(('localhost', 6001))
            self.socketBD = socket.create_connection(('192.168.1.15', 6000))
            logging.info(f"[Fila de Mensagens] Conectado ao Banco de Dados [192.168.1.15:6000].")
        
        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro ao conectar ao Banco de Dados: {e}")
            self.socketBD = None
    
    # Após uma mensagem ser desenfileirada, essa função é responsável por fazer
    # a parte da comunicação entre o servidor de aplicação e o servidor de banco de dados.
    def enviaAoBanco(self, mensagem: Mensagem):
        print("[Fila de Mensagens] Entrou em enviaAoBanco().")
        try:
            # Se não há conexão com o banco de dados, cria seu socket e estabelece comunicação
            if self.socketBD is None:
                self.conectaBanco()

            # Envia a mensagem e retorna a resposta do banco
            if self.socketBD:
                # Envia o tamanho da mensagem para o Banco
                print(f"[Fila de Mensagens] Enviando o tamanho da mensagem para o BD: {mensagem.tamanho}")
                self.socketBD.sendall(mensagem.bytesTamanho)

                # Envia a mensagem para o Banco
                print(f"[Fila de Mensagens] Enviando mensagem para o BD: {mensagem.stringMensagem}")
                self.socketBD.sendall(mensagem.bytesMensagem)
                
                '''
                # POSSO TRAZER OS MÉTODOS DE ENVIO E RECEPÇÃO DE MENSAGEM PARA CÁ.
                '''

                # Recebe o tamanho da resposta do Banco
                tamRespostaBytes = self.socketBD.recv(8)
                tamResposta = int.from_bytes(tamRespostaBytes, "big")
                print(f"[Fila de Mensagens] Tamanho da mensagem a receber do BD: {tamResposta}")

                # Recebe a mensagem de resposta do Banco
                resposta = self.socketBD.recv(tamResposta)
                print(f"[Fila de Mensagens] Resposta recebida do BD: {resposta}")
                
                return op.decodifica(resposta)
            
            else:
                return "[Fila de Mensagens][Erro] Conexão com Banco de Dados não estabelecida."

        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro na conexão com Banco de Dados: {e}")
            self.socketBD = None
            return f"[Fila de Mensagens][Erro] Falha ao enviar ao banco: {e}"
        

    @staticmethod
    def decisorVisualizar(resposta, connect, callback, socket_banco):
        #resposta = [ws.strip() for ws in respostaO.split('|')]
        match resposta[0]:
            case "anuncios":
                callback(resposta, connect, socket_banco)

            case "anuncio":
                callback(resposta, connect, socket_banco)

            case "produto":
                callback(resposta, connect, socket_banco)

            case "pedido":
                callback(resposta, connect, socket_banco)

            case "loja":
                callback(resposta, connect, socket_banco)

            case "minha_loja":
                callback(resposta, connect, socket_banco)

            case "meus_enderecos":
                callback(resposta, connect, socket_banco)

            case "meus_pedidos":
                callback(resposta, connect, socket_banco)

    @staticmethod
    def decisorEditar(resposta, connect, socket_banco, callback, imagens: list):
        print(f"[Decisor Editar] Resposta: $ {resposta[0]} $")
        match resposta[0]:
            case "loja":
                print("[Decisor Editar][Editar Loja]")
                mensagemImagemProBanco = Mensagem.produtorMensagem(imagens[0])
                op.enviaMensagem(socket_banco, mensagemImagemProBanco)
                callback(resposta, connect, imagens)

            case "anuncio":
                print("[Decisor Editar][Editar Anúncio]")
                callback(resposta, connect)

            case "produto":
                print("[Decisor Editar][Editar Produto]")
                callback(resposta, connect)

            case "endereco":
                print("[Decisor Editar][Editar Endereco]")
                callback(resposta, connect)

            case _:
                print("[Decisor Editar][Editar Usuário]")
                callback(resposta, connect)

    def decisorCriar(self, resposta: list, connect: socket.socket, callback, imagens: list):
        match resposta[0]:
            case "produto":
                callback(resposta, connect, imagens)

            case "loja":
                callback(resposta, connect, imagens)

            case "pedido":
                callback(resposta, connect)

            case "endereco":
                callback(resposta, connect)

            case "imagem":
                callback(resposta, connect, imagens)

            case "anuncio":
                callback(resposta, connect, imagens)

    def decisorExcluir(self, resposta: list, connect: socket.socket, callback):
        match resposta[0]:
            case "anuncio":
                callback(resposta, connect)

            case "produto":
                callback(resposta, connect)

            case "loja":
                callback(resposta, connect)

            case "endereco":
                callback(resposta, connect)

            case "imagem":
                callback(resposta, connect)

    def decisorPedido(self, resposta: list, connect: socket.socket, callback, mensagemServidor: Mensagem):
        if mensagemServidor.camposMensagem[0] == "pedido":
            callback(resposta, connect)

        elif mensagemServidor.camposMensagem[0] == "excluir":
            callback(resposta, connect)

    def mensagemProBancoCriar(self, mensagem: Mensagem, imagens: list):
        try:
            # Se não há conexão com o banco de dados, cria seu socket e estabelece comunicação
            if self.socketBD is None:
                self.conectaBanco()

            # Envia o tamanho da mensagem para o Banco
                print(f"[Servidor] Enviando o tamanho da mensagem para o BD: {mensagem.tamanho}")
                self.socketBD.sendall(mensagem.bytesTamanho)
                # Envia a mensagem para o Banco
                print(f"[Servidor] Enviando mensagem para o BD: {mensagem.stringMensagem}")
                self.socketBD.sendall(mensagem.bytesMensagem)
                
            if self.socketBD:
                for imagem in imagens:
                    mensagemImagem = Mensagem.produtorMensagem(imagem)
                    # Envia o tamanho da mensagem para o Banco
                    print(f"[Servidor] Enviando o tamanho da mensagem para o BD: {mensagemImagem.tamanho}")
                    self.socketBD.sendall(mensagemImagem.bytesTamanho)

                    # Envia a mensagem para o Banco
                    print(f"[Servidor] Enviando mensagem para o BD: {mensagemImagem.stringMensagem}")
                    self.socketBD.sendall(mensagemImagem.bytesMensagem)
                

                # Recebe o tamanho da resposta do Banco
                tamRespostaBytes = self.socketBD.recv(8)
                tamResposta = int.from_bytes(tamRespostaBytes, "big")
                print(f"[Servidor] Tamanho da mensagem a receber do BD: {tamResposta}")

                # Recebe a mensagem de resposta do Banco
                resposta = self.socketBD.recv(tamResposta)
                print(f"[Servidor] Resposta recebida do BD: {resposta}")
                
                return op.decodifica(resposta)
            
            else:
                return "[Fila de Mensagens][Erro] Conexão com Banco de Dados não estabelecida"

        except Exception as e:
            logging.info(f"[Fila de Mensagens] Erro na conexão com Banco de Dados: {e}")
            self.socketBD = None
            return f"[Fila de Mensagens][Erro] Falha ao enviar ao banco: {e}"
        