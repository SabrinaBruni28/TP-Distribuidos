import socket
import threading
import logging
from Estruturas.mensagem import Mensagem
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Operacoes import server_operation as op
from queue import Queue, Empty
from Operacoes import callback as cb
from Operacoes import imagem as img

class BancoDeRespostas:
    def __init__(self):
        self._respostas = {}
        self._events = {}
        self._lock = threading.Lock()

    # Essa função aqui é a que marca no banco de respostas um Event vazio
    # para que haja um "aguardo" pela resposta do banco
    def criaRequisicao(self, id):
        # No caso de uma requisição com aquele ID já ocorrer.
        # Só imagino isso acontecer em caso de duplicação :/
        with self._lock:
            if id in self._events:
                raise RuntimeError(f"Requisição com ID {id} já existe. Possível duplicação acontecendo.")
            
            event = threading.Event()
            self._events[id] = event

    # Essa função aqui é para ser chamada quando o servidor de aplicação
    # estiver esperando uma resposta do banco de dados.
    def esperaResposta(self, id):
        # Primeiro, é bom conferir se a requisição da qual se espera uma resposta foi criada.
        with self._lock:
            event = self._events.get(id)
            if event is None:
                raise KeyError(f"Requisição com ID {id} não existe. Esperando por uma resposta que não vai chegar. Há! Olha minha vida de parquera aí...")
            
        # Espera a notificação de que uma nova resposta do banco de dados chegou
        event.wait()
        
        # Retorna a resposta do servidor
        with self._lock:
            resposta = self._respostas.pop(id)

            self._events.pop(id)

            return resposta
        
    def guardarResposta(self, id, resposta):
        # Novamente, bom conferir se a requisição correspondente a essa resposta existe
        with self._lock:
            if id not in self._events:
                # Se não existir, por hora vou permitir uma "resposta perdida",
                # qualquer coisa eu tiro
                self._respostas[id] = resposta
                return
            
            # Guarda a resposta na tabela de respostas
            self._respostas[id] = resposta
            event = self._events[id]

        # Notifica que uma resposta chegou
        event.set()