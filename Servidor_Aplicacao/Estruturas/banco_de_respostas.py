import threading
import logging

class BancoDeRespostas:
    def __init__(self):
        self._respostas = {}
        self._events = {}
        self._lock = threading.Lock()

    # Essa função aqui é a que marca no banco de respostas um Event vazio
    # para que haja um "aguardo" pela resposta do banco
    def criaRequisicao(self, id_requisicao):
        # No caso de uma requisição com aquele ID já ocorrer.
        # Só imagino isso acontecer em caso de duplicação :/
        with self._lock:
            if id_requisicao in self._events:
                raise RuntimeError(f"Requisição com ID {id_requisicao} já existe. Possível duplicação acontecendo.")
            
            event = threading.Event()
            self._events[id_requisicao] = event

        print(f"[Banco de Respostas][ID: {id_requisicao}] Requisição registrada.")

    # Essa função aqui é para ser chamada quando o servidor de aplicação
    # estiver esperando uma resposta do banco de dados.
    def esperaResposta(self, id_requisicao):
        # Primeiro, é bom conferir se a requisição da qual se espera uma resposta foi criada.
        with self._lock:
            event = self._events.get(id_requisicao)
            if event is None:
                raise KeyError(f"Requisição com ID {id_requisicao} não existe. Esperando por uma resposta que não vai chegar. Há! Olha minha vida de parquera aí...")
            
        # Espera a notificação de que uma nova resposta do banco de dados chegou
        print(f"[Banco de Resposta] Esperando resposta.")
        event.wait()
        
        # Retorna a resposta do servidor
        with self._lock:
            resposta = self._respostas.pop(id_requisicao)

            self._events.pop(id_requisicao)

            print(f"[Banco de Respostas] Retornando resposta do banco: {resposta}")
            return resposta
        
    def guardarResposta(self, id_requisicao, resposta):
        # Novamente, bom conferir se a requisição correspondente a essa resposta existe
        with self._lock:
            if id_requisicao not in self._events:
                # Se não existir, por hora vou permitir uma "resposta perdida",
                # qualquer coisa eu tiro
                self._respostas[id_requisicao] = resposta
                return
            
            print(f"[Banco de Respostas] Resposta guardada na tabela de respostas.")
            # Guarda a resposta na tabela de respostas
            self._respostas[id_requisicao] = resposta
            event = self._events[id_requisicao]

        # Notifica que uma resposta chegou
        print(f"[Banco de Respostas] Servidor notificado.")
        event.set()