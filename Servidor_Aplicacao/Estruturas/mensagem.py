import socket
from Operacoes import server_operation as op
# Estrutura de mensagem para organizar melhor uma mensagem do cliente
# Ela carrega a string original, os campos da mensagem e o tamanho
class Mensagem:
    def __init__(self, mensagem, tamanho: int, binario=False):
        self.stringMensagem = mensagem
        self.tamanho = tamanho
        self.bytesTamanho = tamanho.to_bytes(8, "big")
        self.binario = binario

        if binario:
            # Assume que mensagem é um objeto bytes
            self.bytesMensagem = mensagem
            self.camposMensagem = None
        else:
            # Assume que mensagem é string
            self.bytesMensagem = op.codifica(str(mensagem))
            self.camposMensagem = self._divideString()


    # Função para dividir os campos da mensagem
    # o strip limpa os expaços extras das mensagens,
    # mas mantém os espaços que fazem parte da mensagem, se for o caso
    def _divideString(self):
        return [ws.strip() for ws in self.stringMensagem.split('|')]
    
    

    
    # Função para receber apenas a mensagem. Usada em casos onde o tamanho da mensagem é conhecido.
    @classmethod
    def receptorMensagem(cls, socket_cliente: socket.socket, tamanho: int):
        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        
        mensagemServidor = Mensagem(stringMensagem, tamanho)
        return mensagemServidor

    # Função para o Servidor criar suas mensagens. Recebe como parâmetro apenas a string.
    # bin serve para casos em que a mensagem é para uma imagem.
    @classmethod
    def produtorMensagem(cls, string, bin=False):
        stringMensagemServidor = string
        tamanhoMensagem = len(stringMensagemServidor)

        mensagemServidor = Mensagem(stringMensagemServidor, tamanhoMensagem, binario=bin)
        print(f"[Servidor][MENSAGEM] Mensagem peoduzida: {mensagemServidor.stringMensagem}")
        return mensagemServidor
    
    # Receptor mensagem é o equivalente ao receptorMensagemETamanho, mas para uma imagem.
    @classmethod
    def receptorImagem(cls, socket_cliente: socket.socket):
        print("[Servidor] Esperando imagem.")
        tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
        print(f"[Servidor] Tamanho da imagem: {tamanho}")

        if tamanho == 0:
            return None

        imagem_bytes = cls._recebeBytes(socket_cliente, tamanho)
        mensagemImagem = Mensagem.produtorMensagem(imagem_bytes, bin=True)
        return mensagemImagem

    # Recebe bytes é a função resposável por receber um bytestring de uma imagem. Essa função lida com as mensagens vindo em pedaços e tal.
    @staticmethod
    def _recebeBytes(socket_cliente: socket.socket, tamanho: int):
        print(f"[Servidor] Recebendo {tamanho} bytes de dados brutos.")

        dados = b''
        while len(dados) < tamanho:
            parte = socket_cliente.recv(min(4096, tamanho - len(dados)))
            if not parte:
                raise ConnectionError("Conexão encerrada antes do recebimento completo.")
            dados += parte

        return dados

        # Função para receber mensagens que vêm com o tamanho delas antes
    @classmethod
    def receptorMensagemETamanho(cls, socket_cliente: socket.socket):
        print("[Servidor] Entrou em receptorMensagem() e está esperando as mensagens do cliente.")
        tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
        print(f"[Servidor] Tamanho da mensagem do cliente a receber: {tamanho}")
    
        if tamanho == 0:
            return None
    
        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        mensagemCliente = Mensagem(stringMensagem, tamanho)
        return mensagemCliente
    
    @staticmethod
    def _recebeTamanhoDaMensagem(socket_cliente: socket.socket):
        print(f"[Servidor] Entrou em _recebeMensagemTamanho() e vai receber o tamanho da mensagem.")
        dados = b''
        while len(dados) < 8:
            parte = socket_cliente.recv(8 - len(dados))
            if not parte:
                raise ConnectionError("Conexão perdida ao tentar ler o tamanho da mensagem.")
            dados += parte
        tamanho = int.from_bytes(dados, "big")
        return tamanho
    
    @staticmethod
    def _recebeMensagem(socket_cliente: socket.socket, tamanho: int):
        print(f"[Servidor] Entrou em recebeMensagem() e vai receber a string da mensagem recebida.")
        dados = b''
        while len(dados) < tamanho:
            parte = socket_cliente.recv(min(4096, tamanho - len(dados)))
            if not parte:
                raise ConnectionError("Conexão perdida durante a recepção da mensagem.")
            dados += parte
        mensagem = op.decodifica(dados)
        return mensagem
    
