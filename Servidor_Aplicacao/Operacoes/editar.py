import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

class Editar(operacao.Operacao):
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens


    def anuncio(self, dados):
        print("[Servidor][Editar][Anúncio] Operação de editar anúncio recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Editar][Anúncio] Enviando requisição para a fila...")
        self.fila.enfileira(f"editar_anuncio", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def produto(self, dados):
        print("[Servidor][Editar][Produto] Operação de editar produto recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Editar][Produto] Enviando requisição para a fila...")
        self.fila.enfileira(f"editar_produto", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    # Na operação de edição da loja, a imagem pode ser editada.
    def loja(self, dados, imagem):
        print("[Servidor][Editar][Loja] Operação de editar loja recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Editar][Loja] Enviando requisição para a fila...")
        self.fila.enfileira(f"editar_loja", dados, reqID, imagem)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def endereco(self, dados):
        print("[Servidor][Editar][Endereço] Operação de editar endereço recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Editar][Endereço] Enviando requisição para a fila...")
        self.fila.enfileira(f"editar_endereco", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def usuario(self, dados):
        print("[Servidor][Editar][Usuário] Operação de editar usuário recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Editar][Usuário] Enviando requisição para a fila...")
        self.fila.enfileira(f"editar_usuario", dados, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)