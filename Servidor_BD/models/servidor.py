import socket
import threading

class UnixSocketServer:
    def __init__(self, ip='127.0.0.1', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        print(f"Servidor ouvindo em {ip}:{port}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão recebida de {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            while True:
                # Recebe dados de texto
                data = client_socket.recv(1024)
                if not data:
                    break

                if len(data) == 8:
                    # Provavelmente é o cabeçalho da imagem
                    tamanho_total = int.from_bytes(data, 'big')
                    print(f"Recebendo imagem de {tamanho_total} bytes")
                    image_data = b''
                    while len(image_data) < tamanho_total:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            break
                        image_data += chunk
                    with open("imagem_recebida.png", 'wb') as f:
                        f.write(image_data)
                    print("Imagem salva como imagem_recebida.png")
                else:
                    texto = data.decode()
                    print("Mensagem recebida:", texto)
        except Exception as e:
            print("Erro ao lidar com cliente:", e)
        finally:
            client_socket.close()
            print("Conexão encerrada")

# Execução
if __name__ == '__main__':
    server = UnixSocketServer(ip='127.0.0.1', port=5000)
    server.start()
