import socket
import threading

class CommandThread(threading.Thread):
    def __init__(self, comando):
        super().__init__()
        self.comando = comando

    def run(self):
        print("Thread iniciada.")
        self.comando()
        print("Thread finalizada.")

# Cria o socket TCP/IP
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Liga o socket a um endereço e porta
servidor_socket.bind(('', 5000))
servidor_socket.listen(1)

print("Servidor esperando conexão...")

# Aceita a conexão do cliente
conexao, endereco = servidor_socket.accept()
print("Conectado")

# Recebe e envia dados
while True:
    dados = conexao.recv(64000).decode()
    if not dados:
        break
    print("Recebido: ", dados)
    conexao.sendall(f"Echo: {dados}".encode())

conexao.close()