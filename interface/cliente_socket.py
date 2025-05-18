import socket

class UnixSocketClient:
    def __init__(self, ip, port):
        self.socket = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            self.socket = s  # só define se conectou com sucesso
        except Exception:
            pass  # falha silenciosa
        print("Socket:", self.socket)

    def close(self):
        if self.socket:
            self.socket.close()
            print("Fechar socket:", self.socket)

    def send(self, data: str):
        if not self.socket:
            return False
        data_byte = data.encode()
        tamanho = len(data_byte)
        self.send_size(tamanho)
        self.socket.sendall(data_byte)

    def receive(self):
        if not self.socket:
            return False
        try:
            self.socket.settimeout(10)
            tamanho = self.receive_size()
            return self.socket.recv(tamanho).decode()
        except socket.timeout:
            return False

    def send_image(self, image_path: str):
        if not self.socket:
            return False
        with open(image_path, 'rb') as f:
            data = f.read()
            tamanho = len(data)
            self.send_size(tamanho)
            self.socket.sendall(data)
        return data

    def receive_image(self, buffer_size=4096, path='received_image.png'):
        if not self.socket:
            return False
        tamanho_total = self.receive_size()
        with open(path, 'wb') as f:
            data = b''
            while len(data) < tamanho_total:
                chunk = self.socket.recv(buffer_size)
                if not chunk:
                    break
                data += chunk
                diferenca = tamanho_total - len(data)
                if diferenca < buffer_size:
                    buffer_size = diferenca
            f.write(data)
        return data, path

    def send_size(self, tamanho: int):
        if not self.socket:
            return False 
        self.socket.sendall(tamanho.to_bytes(8, 'big'))

    def receive_size(self):
        if not self.socket:
            return False
        try:
            self.socket.settimeout(10)
            tamanho_bytes = self.socket.recv(8)
            tamanho_total = int.from_bytes(tamanho_bytes, 'big')
            return tamanho_total
        except socket.timeout:
            return False

if __name__ == "__main__":
    socket_c = UnixSocketClient(ip="192.168.1.17", port=5000)
    print("Socket:", socket_c)
    socket_c.receive_image(path="imagem.jpg")
    print("imagem recebida")