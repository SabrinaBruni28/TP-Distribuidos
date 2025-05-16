import socket
import threading
import json
from Operacoes import thread_email as correio
from Operacoes import server_operation as op
from Operacoes import thread_email as correio
from Operacoes import operacao
from Operacoes import callback
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
        if (self.mensagemCliente.camposMensagem[1] == "abortar"):
            self.fila.dadosTemp.abortar(self.conexaoCliente)
            print("[Servidor][Cadastramento] Cadastro abortado.")
            return
        
        dados = self.mensagemCliente.camposMensagem[1]
        dadosJson = json.loads(dados)
        mensagemServidor = Mensagem.produtorMensagem(f"criar | usuario | {json.dumps(dadosJson)}")

        print("[Servidor][Cadastramento] Enviando requisição para a fila...")
        self.fila.enfileira(mensagemServidor, callback.cadastramentoCallback, self.conexaoCliente, "cadastrar", self.conexaoServidor, self.fila)
        