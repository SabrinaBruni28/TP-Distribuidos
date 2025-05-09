import socket
import threading
import json
import server_operation as op
from queue import Queue, Empty

class Login():
    pass

class Cadastramento():
    pass

class Visualizar():
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        self.mensagemCliente = mensagem
        self.conexao = socket_cliente
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        print(f"Olha o tamanho do bixo: {self.mensagemCliente.tamanho} cm")
        if self.mensagemCliente.tamanho < 3:
            self.todosAnuncios()

        else:
            self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente[1]

        match operacao:
            case "anuncio":
                self.anuncio()
            
            case "loja":
                self.loja()

            case "minha_loja":
                self.minhaLoja()

            case "minhas_lojas":
                self.minhasListaLojas()

            case "pedidos":
                self.pedidos()

            case "meus_pedidos":
                self.meusPedidos()
    
    def todosAnuncios(self):
        print("0_o quer ver tudo?")
        mensagemServidor = op.codifica("retornar | anuncios")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def anuncio(self):
        print("Só a cbça?")
        idAnuncio = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | anuncio | " + {idAnuncio})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def loja(self):
        idLoja = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | loja | " + {idLoja})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def minhaLoja(self):
        idLoja = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | minha_loja | " + {idLoja})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def minhasListaLojas(self):
        idUsuario = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | minhas_lojas | " + {idUsuario})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def pedidos(self):
        idLoja = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | pedido | " + {idLoja})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))

    def meusPedidos(self):
        idUsuario = self.mensagemCliente[2]
        mensagemServidor = op.codifica("retornar | meus_pedidos | " + {idUsuario})

        self.fila.enfileira(mensagemServidor, op.respostaAoCliente(mensagemServidor, self.conexao))


class Editar():
    pass

class Criar():
    pass

class Apagar():
    pass

class Pedido():
    pass

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

    def enfileira(self, mensagem, callback, conexao):
        self._fila.put((mensagem, callback, conexao))

    def desenfileira(self):
        try:
            return self._fila.get()
        except Empty:
            return None
        
    def enviaAoBanco(self, mensagem):
        try:
            with socket.create_connection(('localhost', 6000)) as servidorBD:
                servidorBD.sendall(op.codifica(mensagem))
                resposta = servidorBD.recv(4096)

                return op.carrega(resposta)
            
        except Exception as e:
            print(f"[Fila de Mensagens] Erro ao enviar para o Banco de Dados: {e}")
            return {"Erro na fila": str(e)}
        
    def vazia(self):
        return self._fila.empty()
    
    def tamanho(self):
        return self._fila.qsize()
    
    def run(self):
        while True:
            mensagem, callback = self.desenfileira()

            if mensagem and callback:
                print("[Fila de Mensagem] Processando uma requisição da fila...")
                resposta = self.enviaAoBanco(mensagem)
                callback(resposta, self.conexao)

            else:
                print("[Fila de mensagens] Erro ao obter callback.")


class ClientHandler(threading.Thread):
    def __init__(self, socket_cliente, endereco, fila):
        super().__init__()
        self.socketCliente = socket_cliente
        self.enderecoCliente = endereco
        self.filaDeMensagem = fila
        self.ativo = True
        self.lock = threading.Lock()

    def run(self):
        print(f"Cliente conectado: {self.enderecoCliente}")

        try:
            while self.ativo:
                stringMensagemCliente = op.decodifica(self.socketCliente)

                mensagemCliente = Mensagem(stringMensagemCliente)
                
                # Se o cliente fecho a conexão
                if not mensagemCliente:
                    break

                print(f"[{self.enderecoCliente}] Comando: {mensagemCliente.stringMensagem}")
                print(mensagemCliente.camposMensagem)

                print(mensagemCliente.camposMensagem[0])

                # Comando de encerramento explícito
                if mensagemCliente.camposMensagem[0] == "fim":
                    self.socketCliente.send("closed".encode("utf-8")[:2048])
                    self.socketCliente.close()
                    return

                # Dispara thread para processar cada comando SEM quebrar o loop
                self.decisor(mensagemCliente)
                self.socketCliente.send("Mensagem recebida.".encode("utf-8")[:2048])

        except Exception as e:
            print(f"Erro com {self.enderecoCliente} - {e}")

        finally:
            return


    def decisor(self, mensagem):
        cabecalhoTipoMensagem = mensagem.camposMensagem[0]

        match cabecalhoTipoMensagem:
            case "login":
                Login()

            case "cadastramento":
                Cadastramento()

            case "visualizar":
                print("Quer ver é?")
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
                print("Comando inválido")
                return

def rodarServidor(endereco_ip, porta, fila):
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
            ClientHandler(socketCliente, endereco, fila).start()

filaDeMensagem = FilaDeMensagens()
filaDeMensagem.start()

rodarServidor('127.0.0.1', 5000, filaDeMensagem)
