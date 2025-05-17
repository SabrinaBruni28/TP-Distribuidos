import threading
from Estruturas.mensagem import Mensagem
from Operacoes import server_operation as op

class Imagem():
    def __init__(self, mensagem_cliente: Mensagem, socket_cliente, fila_mensagens):
        self.mensagem_cliente = mensagem_cliente
        self.cliente = socket_cliente
        self.quantidade = 0
    
    def run(self):
        tipo = self.mensagem_cliente.camposMensagem[1]

        return self.decisor(tipo)


    def decisor(self, tipo: str):
        match tipo:
            case "loja":
                return self.loja()

            case "produto":
                return self.produto()


    def loja(self):
        mensagemImagemLoja = Mensagem.receptorMensagemETamanho(self.cliente)

        imagens = []
        imagens.append(mensagemImagemLoja.stringMensagem)

        return imagens
    
    def produto(self):
        quantidade = op.recebeQuantidade(self.mensagem_cliente.camposMensagem[2], 'imagens')

        imagensProduto = []
        for i in range(quantidade):
            imagemProduto = Mensagem.receptorMensagemETamanho(self.cliente)
            imagensProduto.append(imagemProduto.stringMensagem)

        return imagensProduto