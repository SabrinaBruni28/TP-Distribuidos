from Estruturas.requisicao import Requisicao

class Excluir():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def anuncio(self, id_anuncio):
        print("[Servidor][Excluir][Anúncio] Operação de excluir anúncio recebida.")
        requisicao = Requisicao.produzRequisicao("excluir_anuncio", id_anuncio)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Excluir][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def produto(self, id_produto):
        print("[Servidor][Excluir][Produto] Operação de excluir produto recebida.")
        requisicao = Requisicao.produzRequisicao("excluir_produto", id_produto)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Excluir][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def loja(self, id_loja):
        print("[Servidor][Excluir][Loja] Operação de excluir loja recebida.")
        requisicao = Requisicao.produzRequisicao("excluir_loja", id_loja)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Excluir][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def endereco(self, id_endereco):
        print("[Servidor][Excluir][Endereço] Operação de excluir endereço recebida.")
        requisicao = Requisicao.produzRequisicao("excluir_endereco", id_endereco)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Excluir][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    def imagem(self, nome_imagem):
        print("[Servidor][Excluir][Imagem] Operação de excluir imagem recebida.")
        requisicao = Requisicao.produzRequisicao("excluir_imagem", nome_imagem)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Excluir][Imagem][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)