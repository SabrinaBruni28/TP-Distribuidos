import socket
import threading
import json
from Operacoes import thread_email as correio
from Operacoes import server_operation as op
from Operacoes import thread_email as correio
from Operacoes import operacao
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
#from Estruturas.fila_de_mensagens import FilaDeMensagens

class Cadastramento(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, socket_servidor, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        self.conexaoServidor = socket_servidor

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.decisor()

    def decisor(self):
        self.cadastrar()

    def cadastrar(self):
        print("[Servidor][Cadastramento] Operação de Cadastramento recebida.")
        dados = self.mensagemCliente.camposMensagem[1]
        dadosJson = json.loads(dados)
        mensagemServidor = Mensagem.produtorMensagem(f"confere | usuario | {json.dumps(dadosJson)}")

        # A operação de cadastramento não é tão simples quanto a operação de login. Aqui, além da mensagem, do socket do cliente e do callback,
        # deve-se enfileirar, também, a própria fila para o armazenamento dos dados. O banco de dados recuperará dados que não serão devolvidos
        # para o cliente automaticamente. Os dados serão guardados na estrutura de dados temporários na fila de mensagens, até o cliente enviar
        # o código de confirmação válido.
        print("[Servidor][Cadastramento] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, cb.cadastramentoCallback, self.conexaoCliente, "cadastramento", self.conexaoServidor, self.fila)
        