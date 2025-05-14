import socket
import threading
import json
from Operacoes import thread_email as correio
from Operacoes import cadastramento
from Estruturas import Mensagem
'''
Algumas operações que o servidor usa. Estão aqui separadas para maior universalismo
e para melhor organização.
'''
def codifica(mensagem):
    return mensagem.encode("utf-8").lower()

def carrega(resposta):
    return resposta.decode("utf-8")

def fazMensagemServidor(string):
    stringMensagemServidor = codifica(string)
    tamanhoMensagem = len(stringMensagemServidor)

    mensagemServidor = Mensagem(stringMensagemServidor, tamanhoMensagem)
    return mensagemServidor

def enviaMensagem(socket: socket.socket, mensagem: Mensagem):
    try:
        socket.sendall(codifica(str(mensagem.tamanho)))
        print("enviando: " + mensagem.stringMensagem)
        socket.sendall(codifica(mensagem.stringMensagem))
        return True
    
    except Exception as e:
        print(f"[Erro] {e}\nFalha no envio da mensagem: {mensagem.stringMensagem}")
        return False

def messageHandler(socket_cliente):
    return None

def recebeMensagemTamanho(socket_cliente):
    tamanhoEmBytes = socket_cliente.recv(4)
    tamanho = int.from_bytes(tamanhoEmBytes, "big")
    return tamanho

def decodifica(socket_cliente, tamanho_entrada=2048):
    mensagemCliente = socket_cliente.recv(tamanho_entrada)
    return mensagemCliente.decode("utf-8").lower()

def respostaAoCliente(resposta, socket_cliente):
    try:
        print("[Servidor] Resposta ao cliente: " + resposta)
        socket_cliente.sendall(codifica(resposta))
        print("[Servidor] Mensagem enviada ao cliente.")
    except Exception as e:
        print(f"[Servidor] Erro ao enviar resposta ao cliente: {e}")

            

# [Login] O calback do login é simples. É a comunicação do Banco com o Cliente.


def cadastramentoCallback(resposta_banco, socket_cliente, socket_servidor):
    respostaBD = [ws.strip() for ws in resposta_banco.split('|')]
    dados = respostaBD[1]
    dadosJson = json.dumps(dados)
    
    signupHandler(dados, dadosJson, respostaBD, socket_cliente, socket_servidor)

def signupHandler(dados, dados_json, resposta_banco, cliente, servidor):
    if resposta_banco[0] == "ok":
        emailCliente = dados_json.get("email")
        email = correio.ThreadEmail("confirmacao cadastro", emailCliente).start()
        codigoConfirmacao = email.codigo

        tentativas = 0
        while tentativas < 3:
            tentativas += 1
            codigoCliente = servidor.recv(2048).decode("utf-8")

            if codigoCliente[1] == codigoConfirmacao:
                mensagemAoCliente = codifica("ok | " +str(dados))
                cliente.sendall(mensagemAoCliente)
                return
            
            else:
                mensagemAoCliente = codifica("erro | codigo_invalido")
                cliente.sendall(mensagemAoCliente)
                return
            
        mensagemAoCliente = codifica("erro | limite_excedido")
        cliente.sendall(mensagemAoCliente)

    else:
        mensagemAoCliente = codifica("erro | " + str(resposta_banco[1]))
        print("[Servidor] Reportando erro de cadastro...")
        cliente.sendall(mensagemAoCliente)