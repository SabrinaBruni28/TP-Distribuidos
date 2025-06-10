import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

# Operação de visualizar.
# Excluso o Login, provavelmente a operação mais simples. Não carrega imagens do cliente e nem
# tem duas fases (como o Cadastramento e o Código de confirmação).
class Visualizar(operacao.Operacao):
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    # Operação de visualizar todos os anúncios do marketplace.
    def todosAnuncios(self):
        print("[Servidor][Visualizar] Operação de visualizar todos os anúncios recebida.")
        reqID = op.gerarID()

        self.fila.registrarRequisicao(reqID)

        # Como a requisição de visualizar todos os anúnicos não recebe parãmetros, ao invés de criar uma
        # outra versão de enfileiramento, envio True para que a fila não tenha problemas com essa chamada aqui.
        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_anuncios", True, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar um único anúncio do marketplace.
    def anuncio(self, idAnuncio):
        print("[Servidor][Visualizar] Operação de visualizar anúncio recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_anuncio", idAnuncio, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar um produto específico.
    def produto(self, idProduto):
        print("[Servidor][Visualizar] Operação de visualizar produto recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_produto", idProduto, reqID)

    # Operação de visualizar um loja específica.
    def loja(self, idLoja):
        print("[Servidor][Visualizar] Operação de visualizar loja recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_loja", idLoja, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)
        

    # Operação de visualizar a loja do usuário.
    def minhaLoja(self, idLoja):
        print("[Servidor][Visualizar] Operação de visualizar loja do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_minha_loja", idLoja, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar todas as lojas do usuário.
    def minhaListaLojas(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar lojas do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_minhas_lojas", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar um pedido específico.
    def pedido(self, idPedido):
        print("[Servidor][Visualizar] Operação de visualizar pedido recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_pedido", idPedido, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar todos os pedidos do usuário.
    def meusPedidos(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar pedidos do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_meus_pedidos", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Operação de visualizar a lista de endereços do usuário.
    def meusEnderecos(self, idUsuario):
        print("[Servidor][Visualizar] Operação de visualizar endereços do usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Visualizar] Enviando requisição para a fila...")
        self.fila.enfileira(f"visualizar_meus_enderecos", idUsuario, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)