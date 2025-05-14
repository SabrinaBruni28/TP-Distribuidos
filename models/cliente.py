import socket

class UnixSocketClient:
    def __init__(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
        except Exception as e:
            print(e)
            self.socket = None
        self.socket = s

    def close(self):
        if self.socket:
            self.socket.close()
            print("Fechar socket:", self.socket)

    def send(self, data: str):
        if not self.socket:
            raise RuntimeError("Socket not connected")
        data_byte = data.encode()
        tamanho = len(data_byte)
        self.receive_size(tamanho)
        self.socket.sendall(data_byte)

    def receive(self):
        if not self.socket:
            raise RuntimeError("Socket not connected")
        tamanho = self.receive_size()
        return self.socket.recv(tamanho).decode()
    
    def send_image(self, image_path: str):
        if not self.socket:
            raise RuntimeError("Socket not connected")
        with open(image_path, 'rb') as f:
            data = f.read()
            tamanho = len(data)
            self.send_size(tamanho)
            self.socket.sendall(data)
        return data

    def receive_image(self, buffer_size=4096, path='received_image.png'):
        if not self.socket:
            raise RuntimeError("Socket not connected")
        tamanho_total = self.receive_size()
        with open(path, 'wb') as f:
            data = b''
            while len(data) < tamanho_total:
                chunk = self.socket.recv(buffer_size)
                if not chunk:
                    break
                data += chunk
            f.write(data)
        return data, path

    def send_size(self, tamanho: int):
        self.socket.sendall(tamanho.to_bytes(8, 'big'))

    def receive_size(self):
        tamanho_bytes = self.socket.recv(8)
        tamanho_total = int.from_bytes(tamanho_bytes, 'big')
        return tamanho_total
