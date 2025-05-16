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

            case "pedidos":
                self.pedidos()

            case "meus_pedidos":
                self.meusPedidos()
            
            case _:
                print("[Servidor] Mensagem inválida.")

    def todosAnuncios(self):
        mensagemServidor = Mensagem.produtorMensagem("retornar | anuncios")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarTodosAnunciosCallback, "visualizar", self.conexaoCliente)

    def anuncio(self):
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | anuncio | {str(idAnuncio)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarAnuncioCallback, "visualizar",  self.conexaoCliente)

    def produto(self):
        idProduto = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | produto | {str(idProduto)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarProdutoCallback, "visualizar",  self.conexaoCliente)

    def loja(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarLojaCallback, "visualizar",  self.conexaoCliente)

    def minhaLoja(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | minha_loja | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarLojaUsuarioCallback, "visualizar",  self.conexaoCliente)

    def minhasListaLojas(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | minhas_lojas | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarListaLojasUsuarioCallback, "visualizar",  self.conexaoCliente)

    def pedido(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | pedido | " + str(idLoja))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarPedidoCallback, "visualizar",  self.conexaoCliente)

    def meusPedidos(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem("retornar | meus_pedidos | " + str(idUsuario))

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarListaPedidosUsuarioCallback, "visualizar",  self.conexaoCliente)

    def meusEnderecos(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        mensagemServidor = Mensagem.produtorMensagem(f"retornar | meus_enderecos | {str(idUsuario)}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, cb.visualizarEnderecosUsuarioCallback, "visualizar", self.conexaoCliente)