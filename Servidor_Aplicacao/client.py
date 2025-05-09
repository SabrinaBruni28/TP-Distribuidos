import socket
import random

# Cria o socket TCP/IP
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect(('127.0.0.1', 5000))
cliente_socket.send("visualizar | todos_anuncios".encode("utf-8")[:2048])

resposta = cliente_socket.recv(2048)
resposta = resposta.decode("utf-8")

print(f"Recebido: {resposta}")
try:
    while True:
        # Pega a mensagem de entrada do usuário e envia ao servidor
        msg = input("Mensagem: ")
        cliente_socket.send(msg.encode("utf-8")[:2048])

        # Recebe a mensagem do servidor
        resposta = cliente_socket.recv(2048)
        resposta = resposta.decode("utf-8")

        # Se o servidor envia "closed" na carga, sai do loop
        # e fecha o socket client
        if resposta == "closed":
            break

        print(f"Recebido: {resposta}")
except Exception as e:
    print(f"Erro: {e}")

finally:
    # Fecha o socket client (a conexão com o servidor)
    cliente_socket.close()
    print("Conexão com o servidor fechada.")
