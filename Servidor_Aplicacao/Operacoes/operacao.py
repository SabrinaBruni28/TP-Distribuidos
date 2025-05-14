import threading

class Operacao(threading.Thread):
    def __init__(self, mensagem_cliente, socket_cliente, fila_mensagens):
        super().__init__()
        self.mensagemCliente = mensagem_cliente
        self.conexaoCliente = socket_cliente
        self.fila = fila_mensagens
    
    def run(self):
        pass