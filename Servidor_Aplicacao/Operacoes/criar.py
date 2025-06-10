import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem
from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2

class Criar(operacao.Operacao):
    def __init__(self, fila_mensagens: FilaDeMensagensV2):
        self.fila = fila_mensagens

    def anuncio(self, dados):
        print("[Servidor][Criar][Anúncio] Operação de criar anúncio recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Anúncio] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_anuncio", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def produto(self, dados, imagens):
        print("[Servidor][Criar][Produto] Operação de criar produto recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Produto] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_produto", dados, reqID, imagens)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def loja(self, dados, imagens=[]):
        print("[Servidor][Criar][Loja] Operação de criar loja recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Produto] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_loja", dados, reqID, imagens)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def pedido(self, dados):
        print("[Servidor][Criar][Pedido] Operação de criar pedido recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Pedido] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_pedido", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def endereco(self, dados):
        print("[Servidor][Criar][Endereço] Operação de criar endereço recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Endereço] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_endereco", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def imagem(self, dados):
        print("[Servidor][Criar][Imagem] Operação de criar imagem recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Criar][Imagem] Enviando requisição para a fila...")
        self.fila.enfileira(f"criar_imagem", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)