import socket
from Operacoes import server_operation as op

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

    def _divideString(self):
        # Divide a string da mensagem em campos, removendo espaços extras em cada campo
        return [ws.strip() for ws in self.stringMensagem.split('|')]

    @classmethod
    def receptorMensagem(cls, socket_cliente: socket.socket, tamanho: int):
        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        mensagemServidor = Mensagem(stringMensagem, tamanho)
        return mensagemServidor

    @classmethod
    def produtorMensagem(cls, string, bin=False):
        # Ajusta o cálculo do tamanho dependendo se é string ou bytes
        if bin:
            tamanhoMensagem = len(string)  # string aqui é bytes
        else:
            tamanhoMensagem = len(op.codifica(string))  # tamanho em bytes da string codificada

        mensagemServidor = Mensagem(string, tamanhoMensagem, binario=bin)
        if len(mensagemServidor.stringMensagem):
            print(f"[Servidor][MENSAGEM] Mensagem produzida: {mensagemServidor.stringMensagem[-100:]}")
        else:
            print(f"[Servidor][MENSAGEM] Mensagem produzida: {mensagemServidor.stringMensagem}")
        return mensagemServidor

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
        print("[Servidor] Entrou em receptorMensagemETamanho().")
        tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
        print(f"[Servidor][Receptor Mensagem] Tamanho da mensagem do cliente a receber: {tamanho}")

        if tamanho == 0:
            return None

        stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
        mensagemCliente = Mensagem(stringMensagem, tamanho)
        print(f"[Servidor][Receptor Mensagem] Mensagem: {mensagemCliente.stringMensagem}")
        return mensagemCliente

    @staticmethod
    def _recebeTamanhoDaMensagem(socket_cliente: socket.socket):
        print(f"[Servidor] Entrou em _recebeMensagemTamanho().")
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
        print(f"[Servidor] Entrou em _recebeMensagem().")
        dados = b''
        while len(dados) < tamanho:
            parte = socket_cliente.recv(min(4096, tamanho - len(dados)))
            if not parte:
                raise ConnectionError("Conexão perdida durante a recepção da mensagem.")
            dados += parte
        mensagem = op.decodifica(dados)
        return mensagem

    @staticmethod
    def limpar_buffer_socket(sock):
        """
        Lê e descarta dados pendentes no socket (modo não bloqueante) sem alterar assinaturas externas.
        """
        import errno
        import socket

        sock.setblocking(0)  # modo não bloqueante
        try:
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break  # conexão encerrada
                except socket.error as e:
                    if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        break  # nada mais para ler
                    else:
                        raise
        finally:
            sock.setblocking(1)  # volta ao modo bloqueante
