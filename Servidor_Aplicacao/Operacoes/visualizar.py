import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem
from Estruturas.fila_de_mensagens2 import FilaDeMensagensV2

class Visualizar(operacao.Operacao):
    def __init__(self, operacao, fila_mensagens: FilaDeMensagensV2):
        self.tipoOperacao = operacao
        self.fila = fila_mensagens

    def todosAnuncios(self):
        print("[Servidor][Visualizar] Operação de visualizar todos os anúncios recebida.")
        reqID = op.gerarID()

        self.fila.registrarRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_anuncios", True, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def anuncio(self, idAnuncio):
        print("[Servidor][Visualizar] Operação de visualizar anúncio recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_anuncio", idAnuncio, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def produto(self, idProduto):
        print("[Servidor][Visualizar] Operação de visualizar produto recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_produto", idProduto, reqID)

    def loja(self, idLoja):
        print("[Servidor][Visualizar] Operação de visualizar loja recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_loja", idLoja, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)
        

    def minhaLoja(self, idLoja):
        print("[Servidor][Visualizar] Operação de visualizar loja do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_minha_loja", idLoja, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def minhasListaLojas(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar lojas do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_minhas_loja", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def pedido(self, idPedido):
        print("[Servidor][Visualizar] Operação de visualizar pedido recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_pedido", idPedido, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def meusPedidos(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar pedidos do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_meus_pedidos", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def meusEnderecos(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar endereços do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_meus_enderecos", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)