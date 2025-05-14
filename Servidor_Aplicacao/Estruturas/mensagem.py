import socket
from Operacoes import server_operation as op
# Estrutura de mensagem para organizar melhor uma mensagem do cliente
# Ela carrega a string original, os campos da mensagem e o tamanho
class Mensagem():
    def __init__(self, mensagem, tamanho):
        self.stringMensagem = str(mensagem)
        self.tamanho = tamanho
        self.bytesMensagem = mensagem
        self.camposMensagem = self._divideString()
        self.quantidadeCampos = len(self.camposMensagem)

    # Função para dividir os campos da mensagem
    # o strip limpa os expaços extras das mensagens,
    # mas mantém os espaços que fazem parte da mensagem, se for o caso
    def _divideString(self):
        return [ws.strip() for ws in self.stringMensagem.split('|')]
    
    @classmethod
    def receptorMensagem(cls, socket_cliente: socket.socket):
        tamanho = cls._recebeMensagemTamanho(socket_cliente)
        print("Problema é ali mesmo.")

        stringMensagem = op.decodifica(socket_cliente, tamanho)
        print(f"Problema aqui: {stringMensagem}")
        mensagemCliente = Mensagem(stringMensagem, tamanho)
        print("Ou aqui")
        return mensagemCliente
    
    @classmethod
    def produtorMensagem(cls, string):
        stringMensagemServidor = op.codifica(string)
        tamanhoMensagem = len(stringMensagemServidor)

        mensagemServidor = Mensagem(stringMensagemServidor, tamanhoMensagem)
        return mensagemServidor

    @staticmethod
    def _recebeMensagemTamanho(socket_cliente: socket.socket):
        tamanhoEmBytes = socket_cliente.recv(4)
        tamanho = int.from_bytes(tamanhoEmBytes, "big")
        return tamanho
