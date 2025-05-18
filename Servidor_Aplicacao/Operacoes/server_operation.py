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
def recebeQuantidade(stringDados: str, campo: str):
    dadosJson = json.loads(stringDados)

    quantidade = len(dadosJson.get(campo))
    return quantidade

def codifica(mensagemEmString: str):
    return mensagemEmString.encode("utf-8")

def carrega(resposta):
    return resposta.decode("utf-8")

def fazMensagemServidor(string):
    stringMensagemServidor = codifica(string)
    tamanhoMensagem = len(stringMensagemServidor)

    mensagemServidor = Mensagem(stringMensagemServidor, tamanhoMensagem)
    return mensagemServidor

def enviaMensagem(socket: socket.socket, mensagem: Mensagem):
    try:
        socket.sendall(mensagem.bytesTamanho)
        socket.sendall(mensagem.bytesMensagem)
        return True
    
    except Exception as e:
        print(f"[Erro] {e}\nFalha no envio da mensagem: {mensagem.stringMensagem}")
        return False
    
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


def enviaImagem(socket: socket.socket, mensagem: Mensagem):
    try:
        # Assume que mensagem.stringMensagem contém os dados binários da imagem
        if isinstance(mensagem.stringMensagem, bytes):
            dados = mensagem.stringMensagem
        elif isinstance(mensagem.stringMensagem, str):
            # Caso tenha sido acidentalmente convertido em string, tenta reverter
            dados = mensagem.stringMensagem.encode("latin1")  # cuidado: pode corromper se não for essa a origem
        else:
            raise ValueError("stringMensagem não contém dados binários válidos.")

        tamanho = len(dados)
        print(f"[Envio] Enviando imagem com {tamanho} bytes.")

        socket.sendall(tamanho.to_bytes(8, "big"))
        socket.sendall(dados)
        return True

    except Exception as e:
        print(f"[Erro] {e}\nFalha no envio da imagem.")
        return False


def messageHandler(socket_cliente):
    return None

def recebeMensagemTamanho(socket_cliente):
    tamanhoEmBytes = socket_cliente.recv(4)
    tamanho = int.from_bytes(tamanhoEmBytes, "big")
    return tamanho


def decodifica(mensagem_em_bytes):
    return mensagem_em_bytes.decode("utf-8").lower()

def respostaAoCliente(resposta, socket_cliente):
    try:
        print("[Servidor] Resposta ao cliente: " + resposta)
        socket_cliente.sendall(codifica(resposta))
        print("[Servidor] Mensagem enviada ao cliente.")
    except Exception as e:
        print(f"[Servidor] Erro ao enviar resposta ao cliente: {e}")


def cadastramentoCallback(resposta_banco, socket_cliente, socket_servidor):
        resposta = [ws.strip() for ws in resposta_banco.split('|')]
        dados = json.loads(resposta[1])
        dadosJson = (dados)

        cadastramento.Cadastramento.signupHandler(dados, dadosJson, resposta, socket_cliente, socket_servidor)


# [Login] O calback do login é simples. É a comunicação do Banco com o Cliente.

'''
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

'''