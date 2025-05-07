import socket

# Cria o socket TCP/IP
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect(('192.168.1.18', 5000))

# Envia dados
mensagem = "Olá, servidor!"
cliente_socket.sendall(mensagem.encode())

# Recebe resposta
resposta = cliente_socket.recv(1024).decode()
print("Resposta do servidor:", resposta)

cliente_socket.close()
