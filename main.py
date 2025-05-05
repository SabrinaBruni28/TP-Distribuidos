from models.loja import Loja
from models.anuncio import Anuncio
from models.produto import Produto
from models.usuario import Usuario_Identificado
from models.validation_utils import ValidationUtils as vu
from models.cliente import UnixSocketClient

# Cria o socket TCP/IP
cliente_socket = UnixSocketClient('192.168.1.14', 5000)
print("Conectado ao servidor.")

# Envia dados
mensagem = "cadastrar"
print("Enviando dados do produto:", mensagem)

cliente_socket.send(mensagem)

# Recebe resposta
resposta = cliente_socket.receive()
print("Resposta do servidor:", resposta)

mensagem = cliente_socket.send_image("imagens/notebook.png")

resposta = cliente_socket.receive_image()
print("Resposta do servidor:", resposta)

cliente_socket.close()