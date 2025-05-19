import socket
import threading
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

class Visualizar(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        if self.mensagemCliente.tamanho < 3:
            self.todosAnuncios()

        else:
            self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.camposMensagem[1]

        match operacao:
            case "todos_anuncios":
                self.todosAnuncios()

            case "anuncio":
                self.anuncio()

            case "produto":
                self.produto()

            case "loja":
                self.loja()

            case "minha_loja":
                self.minhaLoja()

            case "minhas_lojas":
                self.minhasListaLojas()

            case "pedido":
                self.pedidos()

            case "meus_pedidos":
                self.meusPedidos()

            case "meus_enderecos":
                self.meusEnderecos()
            
            case _:
                print("[Servidor] Mensagem inválida.")

    def todosAnuncios(self):
        print("[Servidor][Visualizar] Operação de visualizar todos os anúncios recebida.")
        mensagemServidor = Mensagem.produtorMensagem("retornar | anuncios")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarTodosAnunciosCallback, self.conexaoCliente, "visualizar")

    def anuncio(self):
        print("[Servidor][Visualizar] Operação de visualizar anúncio recebida.")
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | anuncio | {str(idAnuncio)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarAnuncioCallback, self.conexaoCliente, "visualizar")

    def produto(self):
        print("[Servidor][Visualizar] Operação de visualizar produto recebida.")
        idProduto = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | produto | {str(idProduto)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarProdutoCallback, self.conexaoCliente, "visualizar")

    def loja(self):
        print("[Servidor][Visualizar] Operação de visualizar loja recebida.")
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarLojaCallback, self.conexaoCliente, "visualizar")

    def minhaLoja(self):
        print("[Servidor][Visualizar] Operação de visualizar loja do usuário recebida.")
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | minha_loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarLojaUsuarioCallback,  self.conexaoCliente, "visualizar")

    def minhasListaLojas(self):
        print("[Servidor][Visualizar] Operação de visualizar lojas do usuário recebida.")
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | minhas_lojas | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarListaLojasUsuarioCallback,  self.conexaoCliente, "visualizar")

    def pedido(self):
        print("[Servidor][Visualizar] Operação de visualizar pedido recebida.")
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | pedido | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarPedidoCallback,  self.conexaoCliente, "visualizar")

    def meusPedidos(self):
        print("[Servidor][Visualizar] Operação de visualizar pedidos do usuário recebida.")
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | meus_pedidos | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarListaPedidosUsuarioCallback,  self.conexaoCliente, "visualizar")

    def meusEnderecos(self):
        print("[Servidor][Visualizar] Operação de visualizar endereços do usuário recebida.")
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | meus_enderecos | {str(idUsuario)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarEnderecosUsuarioCallback, self.conexaoCliente, "visualizar")