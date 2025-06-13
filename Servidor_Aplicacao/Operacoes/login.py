from Operacoes import server_operation as op
from Estruturas.requisicao import Requisicao

class Login():
    def __init__(self, fila_mensagens):
        self.fila = fila_mensagens

    def logar(self, dados):
        print("[Servidor][Login] Operação de Login recebida.")

        # Gero um ID para a requisição do cliente
        requisicao = Requisicao.produzRequisicao("login", dados)

        # Registro a requisição -com seu ID- 
        self.fila.registraRequisicao(requisicao)

        # Coloco essa requisição do Servidor na Fila de Requisições para ela ser enviada ao banco
        # quando este estiver livre.
        print(f"[Servidor][Login][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
        self.fila.enfileira(requisicao)

        # Espero a resposta do Banco de Dados para retornar ao cliente
        return self.fila.esperarRespostaDoBancoDeRespostas(requisicao.idRequisicao)