import socket
import threading
import json

def codifica(mensagem):
    return mensagem.encode("utf-8")[:2048].lower()

def carrega(resposta):
    return resposta.decode("utf-8")[:2048]

def messageHandler(mensagem):
    return None

def decodifica(socket_cliente, tamanho_entrada=2048):
    mensagemCliente = socket_cliente.recv(tamanho_entrada)
    return mensagemCliente.decode("utf-8").lower()

def respostaAoCliente(resposta, socket_cliente):
        try:
            socket_cliente.sendall(carrega(resposta))
        except:
            print("[Servidor] Erro ao enviar resposta ao cliente")
