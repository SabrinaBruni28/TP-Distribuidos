from Estruturas.requisicao import Requisicao

class Editar():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    def anuncio(self, dados):
        """ Operação de editar um anuncio do unuário no marketplace. """
        print("[Servidor][Editar][Anúncio] Operação de editar anúncio recebida.")
        requisicao = Requisicao.produzRequisicao("editar_anuncio", dados)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Editar][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def produto(self, dados):
        """ Operação de editar um produto do usuário no marketplace. """
        print("[Servidor][Editar][Produto] Operação de editar produto recebida.")
        requisicao = Requisicao.produzRequisicao("editar_produto", dados)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Editar][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def loja(self, dados, imagem):
        """
        Operação de editar a loja do usuário no marketplace.
        Na operação de edição da loja, a imagem pode ser editada.
        """
        print("[Servidor][Editar][Loja] Operação de editar loja recebida.")
        requisicao = Requisicao.produzRequisicao("editar_loja", dados, imagens=imagem)
        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Editar][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def endereco(self, dados):
        """ Operação de editar um endereço do usuário no marketplace. """
        print("[Servidor][Editar][Endereço] Operação de editar endereço recebida.")
        requisicao = Requisicao.produzRequisicao("editar_endereco", dados)
        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Editar][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    def usuario(self, dados):
        """
        Operação de editar dados do usuário no marketplace.
        No caso, os dados enviados pelo usuário nos parâmetros da função são os dados editados.
        """
        print("[Servidor][Editar][Usuário] Operação de editar usuário recebida.")
        requisicao = Requisicao.produzRequisicao("editar_usuario", dados)
        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Editar][Usuário][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)