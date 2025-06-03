import socket
import threading
import logging
from Estruturas.mensagem import Mensagem
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Estruturas.banco_de_respostas import BancoDeRespostas
from Operacoes import server_operation as op
from queue import Queue, Empty
from Operacoes import callback as cb
from Operacoes import imagem as img

# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
class FilaDeMensagensV2(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self._respostas = BancoDeRespostas
        self._respostas.start()
        self.dadosTemp = DadosTemporariosConfirmacao()
        self.bancoURI = None

    