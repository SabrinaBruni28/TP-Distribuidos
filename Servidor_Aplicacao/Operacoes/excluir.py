from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas import Mensagem

class Excluir(operacao.Operacao):
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def anuncio(self, id_anuncio):
        print("[Servidor][Excluir][Anúncio] Operação de excluir anúncio recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Excluir][Anúncio] Enviando requisição para a fila...")
        self.fila.enfileira(f"excluir_anuncio", id_anuncio, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def produto(self, id_produto):
        print("[Servidor][Excluir][Produto] Operação de excluir produto recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Excluir][Produto] Enviando requisição para a fila...")
        self.fila.enfileira(f"excluir_produto", id_produto, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def loja(self, id_loja):
        print("[Servidor][Excluir][Loja] Operação de excluir loja recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Excluir][Loja] Enviando requisição para a fila...")
        self.fila.enfileira(f"excluir_loja", id_loja, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def endereco(self, id_endereco):
        print("[Servidor][Excluir][Endereço] Operação de excluir endereço recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Excluir][Endereço] Enviando requisição para a fila...")
        self.fila.enfileira(f"excluir_endereco", id_endereco, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

    def imagem(self, nome_imagem):
        print("[Servidor][Excluir][Imagem] Operação de excluir imagem recebida.")
        reqID = op.gerarID()

        self.fila.registraRequisicao(reqID)

        print(f"[Servidor][Excluir][Imagem] Enviando requisição para a fila...")
        self.fila.enfileira(f"excluir_imagem", nome_imagem, reqID)

        return self.fila.esperarRespostaDoBancoDeRespostas(reqID)