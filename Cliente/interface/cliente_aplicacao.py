import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cliente_middleware import UnixMiddlewareClient
from models.usuario import Usuario, Usuario_Identificado
from models.endereco import Endereco
from models.anuncio import Anuncio
from models.produto import Produto
from models.pedido import Pedido
from models.loja import Loja
from utils import Utils
import json

class ClienteAplicacao():
    def __init__(self, ip, porta):
        self.anuncios = []
        self.usuario = Usuario()
        self.middleware = UnixMiddlewareClient(ip, porta)
    
    def logout(self):
        self.usuario = Usuario()
    
    def is_identificado(self):
        return isinstance(self.usuario, Usuario_Identificado)

    def is_inteiro(self, valor):
        return type(valor) is int

    def atualiza_anuncios(self):
        anuncios =[]
        for anuncio in self.anuncios:
            if anuncio.quantidade_disponivel and not anuncio.pausado:
                anuncios.append(anuncio)
        self.anuncios = anuncios 

    def apagar_anuncios(self, produto: Produto):
        for i, a in enumerate(self.anuncios):
            if a.produto.id == produto.id:
                del self.anuncios[i]

    def apagar_anuncio(self, anuncio: Anuncio):
        for i, a in enumerate(self.anuncios):
            if a.id == anuncio.id:
                del self.anuncios[i]
                return True
        return False

    def atualiza_anuncio_produto(self, produto: Produto):
        for i, a in enumerate(self.anuncios):
            if a.produto.id == produto.id:
                a.produto = produto
                return produto
        return False

    def atualiza_anuncio(self, anuncio: Anuncio):
        for i, a in enumerate(self.anuncios):
            if a.id == anuncio.id:
                self.anuncios[i] = anuncio
                return anuncio
        self.anuncios.append(anuncio)
        return False

    def cadastrar(self, usuario: Usuario_Identificado):
        usuario_dict = usuario.to_dict_cadastramento()
        resposta = self.middleware.chamar_middleware("send", usuario_dict)

        if isinstance(resposta, list):
            return False, resposta[1]
        return [resposta]
        
    def email_confirmacao(self, codigo):
        resposta = self.middleware.chamar_middleware("send", codigo)

        if isinstance(resposta, dict):
            return True, resposta
        return False, resposta
        
    def login(self, usuario: Usuario_Identificado):
        usuario_dict = usuario.to_dict_login()
        resposta = self.middleware.chamar_middleware("logar", usuario_dict)

        if isinstance(resposta, dict):
            return True, resposta
        return False, str(resposta)

    def visualizar_anuncios(self):
        return []
        resposta = self.middleware.chamar_middleware("send")

        if resposta:
            anuncios = []
            for anuncio_dict in resposta:
                anuncio = Anuncio.from_dict(anuncio_dict)
                anuncios.append(anuncio)
                imagem = anuncio.produto.imagens[0]
                if imagem:
                    imagem_byte = self.middleware.chamar_middleware("send", imagem)
                    Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, anuncios
        return False
    
    def visualizar_anuncio(self, anuncio: Anuncio):
        resposta = self.middleware.chamar_middleware("send", anuncio.id)

        if isinstance(resposta, dict):
            anuncio = Anuncio.from_dict(resposta)
            for imagem in anuncio.produto.imagens:
                imagem_byte = self.middleware.chamar_middleware("send", imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, anuncio
        return False
    
    def visualizar_produto(self, produto: Produto):
        resposta = self.middleware.chamar_middleware("send", produto.id)

        if isinstance(resposta, dict):
            produto = Produto.from_dict(resposta)
            for imagem in produto.imagens:
                imagem_byte = self.middleware.chamar_middleware("send", imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, produto
        return False
    
    def visualizar_loja(self, loja: Loja):
        resposta = self.middleware.chamar_middleware("send", loja.id)

        if isinstance(resposta, dict):
            loja = Loja.from_dict(resposta)
            if loja.imagem:
                imagem_byte = self.middleware.chamar_middleware("send", loja.imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{loja.imagem}")

            lista_imagens = [anuncio.produto.imagens[0] for anuncio in loja.anuncios]
            for imagem in lista_imagens:
                imagem_byte = self.middleware.chamar_middleware("send", imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, loja
        return False
    
    def visualizar_minha_loja(self, loja: Loja):
        resposta = self.middleware.chamar_middleware("send", loja.id)

        if isinstance(resposta, dict):
            loja = self.usuario.editar_loja(loja, Loja.from_dict(resposta))
            lista_imagens = [produto.imagens[0] for produto in loja.produtos]
            for imagem in lista_imagens:
                imagem_byte = self.middleware.chamar_middleware("send", imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, loja
        return False
    
    def visualizar_minhas_lojas(self):
        resposta = self.middleware.chamar_middleware("send", self.usuario.id)

        if resposta:
            lojas = []
            for loja_dict in resposta:
                loja = Loja.from_dict(loja_dict)
                lojas.append(loja)
                if loja.imagem:
                    imagem_byte = self.middleware.chamar_middleware("send", loja.imagem)
                    Utils.byte_to_image(imagem_byte, f"uploads/{loja.imagem}")
            return True, lojas
        return False

    def visualizar_meus_enderecos(self):
        resposta = self.middleware.chamar_middleware("send", self.usuario.id)

        if resposta:
            enderecos = []
            for endereco_dict in resposta:
                endereco = Endereco.from_dict(endereco_dict)
                enderecos.append(endereco)
            return True, enderecos
        return False
    
    def visualizar_pedido(self, pedido: Pedido):
        resposta = self.middleware.chamar_middleware("send", pedido.id)

        if isinstance(resposta, dict):
            pedido = Pedido.from_dict(resposta)
            for imagem in pedido.anuncio.produto.imagens:
                imagem_byte = self.middleware.chamar_middleware("send", imagem)
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, pedido
        return False

    def visualizar_meus_pedidos(self):
        resposta = self.middleware.chamar_middleware("send", self.usuario.id)

        if isinstance(resposta, dict):
            pedidos = []
            for pedido_dict in resposta:
                pedido = Pedido.from_dict(pedido_dict)
                pedidos.append(pedido)
            return True, pedidos
        return False

    def editar_anuncio(self, anuncio: Anuncio, novos_dados):
        resposta = self.middleware.chamar_middleware("send", novos_dados)

        if isinstance(resposta, dict):
            anuncio_dict = json.loads(resposta)
            anuncio.preco = anuncio_dict.get("preco", anuncio.preco)
            anuncio.quantidade_disponivel = anuncio_dict.get("quantidade_disponivel", anuncio.quantidade_disponivel)
            anuncio.chave_pix = anuncio_dict.get("chave_pix", anuncio.chave_pix)
            anuncio.pausado = anuncio_dict.get("pausado", anuncio.pausado)
            return True, anuncio
        return False
    
    def editar_produto(self, produto: Produto, novos_dados):
        resposta = self.middleware.chamar_middleware("send", novos_dados)

        if isinstance(resposta, dict):
            produto = Produto.from_dict(resposta)
            return True, produto
        return False
    
    def editar_loja(self, loja: Loja, novos_dados):
        imagem_byte = None
        editar_imagem = novos_dados.get("imagem", 0)
        if editar_imagem:
            imagem_byte = Utils.image_to_byte(f"uploads/{editar_imagem}")

        resposta = self.middleware.chamar_middleware("send", novos_dados, imagem_byte)

        if resposta:
            loja_dict = json.loads(resposta[0])
            loja.nome = loja_dict.get("nome", loja.nome)
            loja.imagem = loja_dict.get("imagem", loja.imagem)

            imagem = loja_dict.get("imagem", 0)
            if editar_imagem and imagem:
                Utils.byte_to_image(resposta[1], f"uploads/{imagem}")
            return True, loja
        return False
    
    def editar_usuario(self, novos_dados):
        resposta = self.middleware.chamar_middleware("send", novos_dados)

        if resposta:
            return True, resposta
        return False, resposta
    
    def editar_endereco(self, endereco: Endereco, novos_dados):
        resposta = self.middleware.chamar_middleware("send", novos_dados)

        if resposta:
            endereco = Endereco.from_dict(resposta)
            return True, endereco
        return False
    
    def criar_anuncio(self, anuncio: Anuncio):
        resposta = self.middleware.chamar_middleware("send", anuncio.to_dict_personalizado())

        if resposta:
            anuncio = Anuncio.from_dict(resposta)
            return True, anuncio
        return False
    
    def criar_produto(self, produto: Produto):
        imagens_byte = []
        for imagem in produto.imagens:
            imagens_byte.append(Utils.image_to_byte(f"uploads/{imagem}"))

        resposta = self.middleware.chamar_middleware("send", produto.to_dict_personalizado(), imagens_byte)
        if resposta:
            produto_resposta = Produto.from_dict(resposta[0])
            for i, imagem_byte in enumerate(resposta[1]):
                imagem = produto.imagens[i]
                Utils.byte_to_image(imagem_byte, f"uploads/{imagem}")
            return True, produto_resposta
        return False
    
    def criar_loja(self, loja: Loja):
        imagem_byte = None
        if loja.imagem:
            imagem_byte = Utils.image_to_byte(f"uploads/{loja.imagem}")

        resposta = self.middleware.chamar_middleware("send", loja.to_dict_personalizado(), imagem_byte)

        if resposta:
            loja = Loja.from_dict(resposta[0])
            if loja.imagem:
                Utils.byte_to_image(resposta[1], f"uploads/{loja.imagem}")
            return True, loja
        return False
    
    def criar_pedido(self, pedido: Pedido):
        resposta = self.middleware.chamar_middleware("send", pedido.to_dict_personalizado())

        if resposta:
            return True, resposta
        return False
    
    def criar_endereco(self, endereco: Endereco):
        resposta = self.middleware.chamar_middleware("send", endereco.to_dict_personalizado())

        if resposta:
            return True, resposta
        return False

    def criar_imagem(self, produto: Produto, imagem):
        imagem_byte = Utils.image_to_byte(f"uploads/{imagem}")
        resposta = self.middleware.chamar_middleware("send", produto.id, imagem_byte)

        if resposta:
            Utils.byte_to_image(resposta[1], f"uploads/{resposta[0]}")
            return True, resposta[0]
        return False
    
    def excluir_anuncio(self, anuncio: Anuncio):
        resposta = self.middleware.chamar_middleware("send", anuncio.id)
        return resposta
    
    def excluir_produto(self, produto: Produto):
        resposta = self.middleware.chamar_middleware("send", produto.id)
        return resposta
    
    def excluir_loja(self, loja: Loja):
        resposta = self.middleware.chamar_middleware("send", loja.id)
        return resposta
    
    def excluir_endereco(self, endereco: Endereco):
        resposta = self.middleware.chamar_middleware("send", endereco.id)
        return resposta
    
    def excluir_imagem(self, produto: Produto, imagem):
        resposta = self.middleware.chamar_middleware("send", produto.id, imagem)
        return resposta

    def confirmar_pedido(self, pedido: Pedido):
        resposta = self.middleware.chamar_middleware("send", pedido.id)
        return resposta
    
    def cancelar_pedido(self, pedido: Pedido):
        resposta = self.middleware.chamar_middleware("send", pedido.id)
        return resposta
