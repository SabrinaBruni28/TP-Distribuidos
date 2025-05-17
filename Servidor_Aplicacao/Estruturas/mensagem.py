import socket
from Operacoes import server_operation as op
# Estrutura de mensagem para organizar melhor uma mensagem do cliente
# Ela carrega a string original, os campos da mensagem e o tamanho
class Mensagem():
    def __init__(self, mensagem, tamanho: int, tipoDivisao=None):
        self.stringMensagem = mensagem
        self.tamanho = tamanho
        self.bytesTamanho = tamanho.to_bytes(8, "big")
        self.bytesMensagem = op.codifica(str(mensagem))
        self.camposMensagem = self._divideString if tipoDivisao == None else self._divideStringImg
        self.quantidadeCampos = len(self.camposMensagem)

    # Função para dividir os campos da mensagem
    # o strip limpa os expaços extras das mensagens,
    # mas mantém os espaços que fazem parte da mensagem, se for o caso
    def _divideString(self):
        return [ws.strip() for ws in self.stringMensagem.split('|')]
    
    def _divideStringImg(self):
        return []
    
    # Função para receber mensagens que vêm com o tamanho delas antes
    @classmethod
    def receptorMensagemETamanho(cls, socket_cliente: socket.socket):
        print("[Servidor] Entrou em receptorMensagem() e está esperando as mensagens do cliente.")
        tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
        print(f"[Servidor] Tamanho da mensagem do cliente a receber: {tamanho}")

        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        mensagemCliente = Mensagem(stringMensagem, tamanho)
        return mensagemCliente
    
    # Função para receber apenas a mensagem. Usada em casos onde o tamanho da mensagem é conhecido.
    @classmethod
    def receptorMensagem(cls, socket_cliente: socket.socket, tamanho: int):
        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        
        mensagemServidor = Mensagem(stringMensagem, tamanho)
        return mensagemServidor

    # Função para o Servidor criar suas mensagens
    @classmethod
    def produtorMensagem(cls, string):
        stringMensagemServidor = string
        tamanhoMensagem = len(stringMensagemServidor)

        mensagemServidor = Mensagem(stringMensagemServidor, tamanhoMensagem)
        return mensagemServidor

    @staticmethod
    def _recebeTamanhoDaMensagem(socket_cliente: socket.socket):
        print(f"[Servidor] Entrou em _recebeMensagemTamanho() e vai receber o tamanho da mensagem.")
        tamanhoEmBytes = socket_cliente.recv(4)
        tamanho = int.from_bytes(tamanhoEmBytes, "big")
        return tamanho
    
    @staticmethod
    def _recebeMensagem(socket_cliente: socket.socket, tamanho: int):
        print(f"[Servidor] Entrou em recebeMensagem() e vai receber a string da mensagem recebida.")
        mensagemEmBytes = socket_cliente.recv(tamanho)
        mensagem = op.decodifica(mensagemEmBytes)
        return mensagem

