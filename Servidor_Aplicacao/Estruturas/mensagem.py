import socket
import select
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

    @staticmethod
    def limpar_buffer_socket(sock: socket.socket, limite_bytes: int = 8192):
        """
        Descarta qualquer dado residual no buffer de recepção do socket, até um limite.
        Evita bloqueio e restaura o estado original do socket.
        """
        print("[Limpeza] Limpando buffer do socket...")

        try:
            modo_original = sock.getblocking()
            sock.setblocking(0)  # não bloqueante

            total_descartado = 0
            while total_descartado < limite_bytes:
                prontos_para_ler, _, _ = select.select([sock], [], [], 0)
                if not prontos_para_ler:
                    break

                try:
                    dados = sock.recv(4096)
                    if not dados:
                        break
                    total_descartado += len(dados)
                    print(f"[Limpeza] Descartados {len(dados)} bytes.")
                except BlockingIOError:
                    break
                except Exception as e:
                    print(f"[Limpeza] Erro ao limpar buffer: {e}")
                    break

        finally:
            sock.setblocking(modo_original)
            print(f"[Limpeza] Limpeza concluída ({total_descartado} bytes descartados).")

    @classmethod
    def receptorMensagemETamanho(cls, socket_cliente: socket.socket):
        print("[Servidor] Entrou em receptorMensagemETamanho().")
        try:
            tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
            print(f"[Servidor][Receptor Mensagem] Tamanho da mensagem do cliente a receber: {tamanho}")

            if tamanho <= 0:
                print("[Aviso] Tamanho inválido. Limpando buffer.")
                cls.limpar_buffer_socket(socket_cliente)
                return None

            stringMensagem = cls._recebeMensagem(socket_cliente, tamanho)
            return Mensagem(stringMensagem, tamanho)

        except Exception as e:
            print(f"[Erro] Falha ao receber mensagem: {e}")
            cls.limpar_buffer_socket(socket_cliente)
            return None

    @classmethod
    def receptorImagem(cls, socket_cliente: socket.socket):
        print("[Servidor] Esperando imagem.")
        try:
            tamanho = cls._recebeTamanhoDaMensagem(socket_cliente)
            print(f"[Servidor] Tamanho da imagem: {tamanho}")

            if tamanho <= 0 or tamanho > 100_000_000:
                print("[Aviso] Tamanho inválido. Limpando buffer.")
                cls.limpar_buffer_socket(socket_cliente)
                return None

            imagem_bytes = cls._recebeBytes(socket_cliente, tamanho)
            return Mensagem.produtorMensagem(imagem_bytes, bin=True)

        except Exception as e:
            print(f"[Erro] Falha ao receber imagem: {e}")
            cls.limpar_buffer_socket(socket_cliente)
            return None

    @staticmethod
    def _recebeMensagem(socket_cliente: socket.socket, tamanho: int):
        print("[Servidor] Entrou em _recebeMensagem().")
        dados = b''
        try:
            while len(dados) < tamanho:
                parte = socket_cliente.recv(min(4096, tamanho - len(dados)))
                if not parte:
                    raise ConnectionError("Conexão perdida durante a recepção.")
                dados += parte
            return op.decodifica(dados)
        except Exception as e:
            print(f"[Erro] Falha na leitura: {e}")
            Mensagem.limpar_buffer_socket(socket_cliente)
            raise

    @staticmethod
    def _recebeBytes(socket_cliente: socket.socket, tamanho: int):
        print(f"[Servidor] Recebendo {tamanho} bytes de dados brutos.")
        dados = b''
        try:
            while len(dados) < tamanho:
                parte = socket_cliente.recv(min(4096, tamanho - len(dados)))
                if not parte:
                    raise ConnectionError("Conexão encerrada antes do recebimento completo.")
                dados += parte
            return dados
        except Exception as e:
            print(f"[Erro] Falha na leitura de bytes: {e}")
            Mensagem.limpar_buffer_socket(socket_cliente)
            raise

    @staticmethod
    def _recebeTamanhoDaMensagem(socket_cliente: socket.socket):
        print("[Servidor] Entrou em _recebeTamanhoDaMensagem().")
        dados = b''
        while len(dados) < 8:
            parte = socket_cliente.recv(8 - len(dados))
            if not parte:
                raise ConnectionError("Conexão perdida ao ler o tamanho da mensagem.")
            dados += parte
        return int.from_bytes(dados, "big")