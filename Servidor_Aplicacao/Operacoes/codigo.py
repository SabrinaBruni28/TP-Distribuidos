from Operacoes import operacao
from Operacoes import server_operation as op

class Codigo(operacao.Operacao):
    def __init__(self, mensagem, socket_cliente, fila_mensagens):
        super().__init__(mensagem, socket_cliente, fila_mensagens)
        print("[Código] Entrou em codigo.")
        print(f"[Código] Mensagem que chegou aqui: {self.mensagemCliente.camposMensagem}")

    def run(self):
        self.getOperacao()

    def getOperacao(self):
        self.codigo()

    def codigo(self):
        from Estruturas.mensagem import Mensagem
        codigoEnviadoCliente = self.mensagemCliente.camposMensagem[1]

        status, dados = self.fila.dadosTemp.verificarCodigo(self.conexaoCliente, codigoEnviadoCliente)

        if status == "erro":
            print(f"[Servidor][Codigo]: {status}, {dados}.")

        mensagemRetorno = Mensagem.produtorMensagem(str(f"{status} | {dados}"))
        op.enviaMensagem(self.conexaoCliente, mensagemRetorno)