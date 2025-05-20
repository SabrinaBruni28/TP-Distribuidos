import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import socket
import errno

class UnixSocketClient:
    def __init__(self, ip, port):
        self.socket = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            self.socket = s  # só define se conectou com sucesso
        except Exception as e:
            print(e)
            pass  # falha silenciosa
        print("Socket:", self.socket)

    def close(self):
        if self.socket:
            self.socket.close()
            print("Fechar socket:", self.socket)
            self.socket = None

    def send(self, data: str):
        if not self.socket:
            return False
        try:
            data_byte = data.encode()
            tamanho = len(data_byte)
            self.send_size(tamanho)
            self.socket.sendall(data_byte)
            print("Mensagem:", data)
            return True
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
            self.close()
            return False

    def receive(self):
        tamanho = self.receive_size()
        print("Tamanho:", tamanho)
        if not tamanho:
            return False
        print("Tentando receber mensagem")
        data = b''
        self.socket.settimeout(15)
        try:
            while len(data) < tamanho:
                chunk = self.socket.recv(min(4096, tamanho - len(data)))
                if not chunk:
                    raise ConnectionError("Socket fechado inesperadamente")
                data += chunk
            resposta = data.decode()
            print("Resposta:", resposta)
            return resposta
        except socket.timeout:
            print("Timeout ao receber tamanho")
            return False
        except Exception as e:
            print("Erro ao receber mensagem:", e)
            self.close()
            return False

    def send_image(self, image_path: str):
        if not self.socket:
            return False
        try:
            with open(image_path, 'rb') as f:
                data = f.read()
                tamanho = len(data)
                self.send_size(tamanho)
                self.socket.sendall(data)
            print("Manda Imagem:", image_path)
            return data
        except Exception as e:
            print("Erro ao enviar imagem:", e)
            self.close()
            return False

    def receive_image(self, buffer_size=4096, path='received_image.png'):
        if not self.socket:
            return False
        tamanho_total = self.receive_size()
        if not tamanho_total:
            return False
        try:
            with open(path, 'wb') as f:
                data = b''
                while len(data) < tamanho_total:
                    chunk = self.socket.recv(min(buffer_size, tamanho_total - len(data)))
                    if not chunk:
                        break
                    data += chunk
                f.write(data)
                print("Recebe Imagem:", path)
            return data, path
        except socket.timeout:
            print("Timeout ao receber tamanho")
            return False
        except Exception as e:
            print("Erro ao receber imagem:", e)
            self.close()
            return False, path

    def send_size(self, tamanho: int):
        if not self.socket:
            return False 
        print("Manda tamanho:", tamanho)
        try:
            self.socket.sendall(tamanho.to_bytes(8, 'big'))
        except Exception as e:
            print("Erro ao enviar tamanho:", e)
            self.close()
            return False

    def receive_size(self):
        if not self.socket:
            return False
        print("Tentar receber tamanho (8 bytes)")
        self.socket.settimeout(15)
        try:
            tamanho_bytes = b''
            while len(tamanho_bytes) < 8:
                print("Recebendo tamanho:", len(tamanho_bytes))
                chunk = self.socket.recv(8 - len(tamanho_bytes))
                print("Chunk:", chunk)
                if not chunk:
                    raise ConnectionError("Socket fechado antes de receber os 8 bytes de tamanho")
                tamanho_bytes += chunk

            tamanho_total = int.from_bytes(tamanho_bytes, 'big')
            print("Recebe tamanho:", tamanho_total)
            return int(tamanho_total)
        except socket.timeout:
            print("Timeout ao receber tamanho")
            return False
        except Exception as e:
            print("Erro ao receber tamanho:", e)
            self.close()
            return False

    def limpar_buffer_socket(self):
        """
        Lê e descarta dados pendentes no socket (modo não bloqueante) sem alterar assinaturas externas.
        """
        if not self.socket:
            return False

        self.socket.setblocking(0)  # modo não bloqueante
        try:
            while True:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        break  # conexão encerrada
                except socket.error as e:
                    if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                        break  # nada mais para ler
                    else:
                        raise
        finally:
            self.socket.setblocking(1)  # volta ao modo bloqueante
