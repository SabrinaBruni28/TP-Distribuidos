from Estruturas.requisicao import Requisicao

class Criar():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def anuncio(self, dados):
        print("[Servidor][Criar][Anúncio] Operação de criar anúncio recebida.")
        requisicao = Requisicao.produzRequisicao("criar_anuncio", dados)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def produto(self, dados, imagens):
        print("[Servidor][Criar][Produto] Operação de criar produto recebida.")
        requisicao = Requisicao.produzRequisicao("criar_produto", dados, imagens=imagens)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def loja(self, id_usuario, dados, imagem_loja):
        print("[Servidor][Criar][Loja] Operação de criar loja recebida.")
        requisicao = Requisicao.produzRequisicao("criar_loja", dados, imagens=imagem_loja, id_associado=id_usuario)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def pedido(self, dados):
        print("[Servidor][Criar][Pedido] Operação de criar pedido recebida.")
        requisicao = Requisicao.produzRequisicao("criar_pedido", dados)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def endereco(self, id_usuario, dados):
        print("[Servidor][Criar][Endereço] Operação de criar endereço recebida.")
        requisicao = Requisicao.produzRequisicao("criar_endereco", dados, id_associado=id_usuario)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def imagem(self, id_produto, imagem):
        print("[Servidor][Criar][Imagem] Operação de criar imagem recebida.")
        requisicao = Requisicao.produzRequisicao("criar_imagem", id_produto, imagens=imagem)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Criar][Imagem][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)