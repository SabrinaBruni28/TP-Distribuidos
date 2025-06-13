import json
from Operacoes import server_operation as op
from ..Estruturas.requisicao import Requisicao

class Imagem():
    def __init__(self, dados, socket_cliente, tipo: str, campo: str = ""):
        self.dados_cliente = dados
        self.cliente = socket_cliente
        self.tipo = tipo
        self.campo = campo
        self.quantidade = 0
    
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
        dadosJson = json.loads(self.dados_cliente)
        if dadosJson.get(self.campo) == "" or dadosJson.get(self.campo) == None:
            return None
        
        mensagemImagemLoja = Mensagem.receptorImagem(self.cliente)

        imagens = []
        imagens.append(mensagemImagemLoja)

        print("[Servidor][Imagem] Imagem da loja recebida.")
        return imagens
    
    
    def produto(self):
        quantidade = op.recebeQuantidade(self.dados_cliente, 'imagens')

        imagensProduto = []
        for i in range(quantidade):
            imagemProduto = Mensagem.receptorImagem(self.cliente)
            imagensProduto.append(imagemProduto)

        if quantidade > 0:
            print("[Servidor][Imagem] Imagem(s) do produto recebida.")
        return imagensProduto
    

    def imagem(self):
        mensagemImagemLoja = Mensagem.receptorImagem(self.cliente)

        imagens = []
        imagens.append(mensagemImagemLoja)

        print("[Servidor][Imagem] Imagem recebida.")
        return imagens
    