from Operacoes import operacao
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
import json

class Codigo(operacao.Operacao):
    def __init__(self, mensagem, fila_mensagens):
        self.mensagem = mensagem
        self.fila = fila_mensagens

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.codigo()

    def codigo(self, idCliente, codigo):
        from Estruturas.mensagem import Mensagem
        print("[Servidor][Código] Código recebido.")
        
        status, dados = self.fila.dadosTemp.verificarCodigo(idCliente, codigo)

        print(f"[Servidor][Código] Código que o cliente enviou: {codigo}")
        print(f"[Servidor][Código] ID do código: {idCliente}")
        return self.decisorCodigo(status, dados)

    def decisorCodigo(self, status, dados):
        if status == "ok":
            print("[Servidor][Código] Código confirmado.")
            reqID = op.gerarID()

            self.fila.registraRequisicao(reqID)

            print(f"[Servidor][Código] Enviando requisição para a fila...")
            self.fila.enfileira(f"codigo", dados, reqID)

            return self.fila.esperarRespostaDoBancoDeRespostas(reqID)

        elif status == "erro":
            print("[Servidor][Código] Código inválido. Retornando ao cliente.")
            return dados