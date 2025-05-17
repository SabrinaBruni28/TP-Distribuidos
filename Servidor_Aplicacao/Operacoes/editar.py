import socket
import threading
from Operacoes import server_operation as op
from Operacoes import operacao
from Estruturas.mensagem import Mensagem

class Editar(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens, imagens=None):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        self.conexaoServidor = socket_servidor
        self.imagem = imagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        operacao = self.mensagemCliente.campoosMensagem[1]

        match operacao:
            case "anuncio":
                self.anuncio()

            case "produto":
                self.produto()

            case "loja":
                self.loja()

            case "endereco":
                self.endereco()

            case "usuario":
                self.usuario()

            case _:
                print("[Servidor] Mensagem inválida.")

    def anuncio(self):
        idAnuncio = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = Mensagem.produtorMensagem(f"editar | anuncio | {idAnuncio} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def produto(self):
        idProduto = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | anuncio | {idProduto} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def loja(self):
        idLoja = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | loja | {idLoja} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente, imagem=self.imagem)

    def endereco(self):
        idEndereco = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | endereco | {idEndereco} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoCliente)

    def usuario(self):
        idUsuario = self.mensagemCliente.camposMensagem[2]
        dados = self.mensagemCliente.camposMensagem[3]
        mensagemServidor = op.codifica(f"editar | usuario | {idUsuario} | {dados}")

        print("[Servidor] Enviando requisição para fila...")
        self.fila.enfileira(mensagemServidor, op.respostaAoCliente, self.conexaoServidor)
        resposta = self.conexaoServidor.recv(2048).decode("utf-8")

        if resposta[0] == "ok":
            mensagemAoCliente = op.codifica(f"usuario | {resposta[1]}")

            print("[Servidor] Confirmando ação de edição...")
            self.conexaoCliente.sendall(mensagemAoCliente)

        else:
            mensagemAoCliente = op.codifica("erro | " + str(resposta[1]))

            print("[Servidor] Reportando erro de edição ao cliente...")
            self.conexaoCliente.sendall(mensagemAoCliente)