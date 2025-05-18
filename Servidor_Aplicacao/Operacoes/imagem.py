import threading
import json
from Estruturas.mensagem import Mensagem
from Operacoes import server_operation as op

class Imagem():
    def __init__(self, dados, socket_cliente, tipo: str, campo: str = ""):
        self.dados_cliente = dados
        self.cliente = socket_cliente
        self.quantidade = 0
        self.tipo = tipo
        self.campo = campo
    
    def run(self):
        return self.decisor(self.tipo)


    def decisor(self, tipo: str):
        match tipo:
            case "loja":
                return self.loja()

            case "produto":
                return self.produto()
            
            case "imagem":
                return self.imagem()
            
            case _:
                return None


    def loja(self):
        dadosJson = json.loads(self.dados)
        if dadosJson.get(self.campo) == "":
            return None
        
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
    
    def imagem(self):
        mensagemImagemLoja = Mensagem.receptorMensagemETamanho(self.cliente)

        imagens = []
        imagens.append(mensagemImagemLoja.stringMensagem)

        return imagens
    