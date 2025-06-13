from Operacoes import server_operation as op
from Estruturas.requisicao import Requisicao

# Operação de visualizar.
# Excluso o Login, provavelmente a operação mais simples. Não carrega imagens do cliente e nem
# tem duas fases (como o Cadastramento e o Código de confirmação).
class Visualizar():
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    # Operação de visualizar todos os anúncios do marketplace.
    def todosAnuncios(self):
        print("[Servidor][Visualizar] Operação de visualizar todos os anúncios recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_anuncios", None)
        self.fila.registraRequisicao(requisicao)

        # Como a requisição de visualizar todos os anúnicos não recebe parãmetros, ao invés de criar uma
        # outra versão de enfileiramento, envio True para que a fila não tenha problemas com essa chamada aqui.
        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

    # Operação de visualizar um único anúncio do marketplace.
    def anuncio(self, id_anuncio):
        print("[Servidor][Visualizar] Operação de visualizar anúncio recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_anuncio", id_anuncio)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    # Operação de visualizar um produto específico.
    def produto(self, id_produto):
        print("[Servidor][Visualizar] Operação de visualizar produto recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_produto", id_produto)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

    # Operação de visualizar um loja específica.
    def loja(self, id_loja):
        print("[Servidor][Visualizar] Operação de visualizar loja recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_loja", id_loja)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)
        

    # Operação de visualizar a loja do usuário.
    def minhaLoja(self, id_loja):
        print("[Servidor][Visualizar] Operação de visualizar loja do usuário recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_minha_loja", id_loja)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    # Operação de visualizar todas as lojas do usuário.
    def minhaListaLojas(self, id_usuario):
        print("[Servidor][Visualizar] Operação de visualizar lojas do usuário recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_minhas_lojas", id_usuario)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    # Operação de visualizar um pedido específico.
    def pedido(self, id_pedido):
        print("[Servidor][Visualizar] Operação de visualizar pedido recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_pedido", id_pedido)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    # Operação de visualizar todos os pedidos do usuário.
    def meusPedidos(self, id_usuario):
        print("[Servidor][Visualizar] Operação de visualizar pedidos do usuário recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_meus_pedidos", id_usuario)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)

    # Operação de visualizar a lista de endereços do usuário.
    def meusEnderecos(self, id_usuario):
        print("[Servidor][Visualizar] Operação de visualizar endereços do usuário recebida.")
        requisicao = Requisicao.produzRequisicao("visualizar_meus_enderecos", id_usuario)

        self.fila.registraRequisicao(requisicao)

        print(f"[Servidor][Visualizar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)