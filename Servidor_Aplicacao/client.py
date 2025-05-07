import socket
import random

# Cria o socket TCP/IP
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect(('192.168.1.18', 5000))

while True:
    numero = random.randint(1, 2)
    # Envia dados
    if (numero == 1):
        mensagem = "cadastrar"
        cliente_socket.sendall(mensagem.encode())
    else:
        mensagem = "login"
        cliente_socket.sendall(mensagem.encode())

    # Recebe resposta
    resposta = cliente_socket.recv(1024).decode()
    print("Resposta do servidor:", resposta)
