from Operacoes import operacao
from Operacoes import server_operation as op
from Operacoes import callback as cb
from Estruturas.mensagem import Mensagem
import json

class Codigo(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.codigo()

    def codigo(self):
        from Estruturas.mensagem import Mensagem
        print("[Servidor][Codigo] Código recebido.")

        codigoEnviadoCliente = self.mensagemCliente.camposMensagem[1]
        
        status, dados = self.fila.dadosTemp.verificarCodigo(self.conexaoCliente, codigoEnviadoCliente)

        self.decisorCodigo(status, dados)

    def decisorCodigo(self, status, dados):
        if status == "ok":
            dadosJson = json.dumps(dados)
            mensagemServidor = Mensagem.produtorMensagem(f"criar | usuario | {dadosJson}")
            self.fila.enfileira(mensagemServidor, cb.codigoCallback, self.conexaoCliente, tipo="codigo")

        elif status == "erro":
            mensagemAoCliente = Mensagem.produtorMensagem(f"{status} | {dados}")
            op.enviaMensagem(self.conexaoCliente, mensagemAoCliente)