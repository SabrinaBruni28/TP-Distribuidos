import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.usuario import Usuario, Usuario_Identificado
from cliente_socket import UnixSocketClient
from models.endereco import Endereco
from models.anuncio import Anuncio
from models.produto import Produto
from models.pedido import Pedido
from models.loja import Loja
import json

class ClienteAplicacao():
    def __init__(self, ip, porta):
        self.anuncios = []
        self.usuario = Usuario()
        self.socket = UnixSocketClient(ip, porta)

    def divide_mensagem(self, stringMensagem):
        if not stringMensagem:
            return [""]
        return [ws.strip() for ws in stringMensagem.split('|')]
    
    def logout(self):
        self.usuario = Usuario()
    
    def is_identificado(self):
        return isinstance(self.usuario, Usuario_Identificado)

    def is_inteiro(self, valor):
        return type(valor) is int

    def atualiza_anuncios(self):
        anuncios =[]
        for anuncio in self.anuncios:
            if anuncio.quantidade_disponivel:
                anuncios.append(anuncio)
        self.anuncios = anuncios 

    def atualiza_anuncios_loja(self, loja: Loja):
        anuncios =[]
        for anuncio in loja.anuncios:
            if anuncio.quantidade_disponivel:
                anuncios.append(anuncio)
        loja.anuncios = anuncios 

    def atualiza_anuncio_produto(self, produto):
        for i, a in enumerate(self.anuncios):
            if a.produto.id == produto.id:
                a.produto = produto
                return produto
        return False

    def atualiza_anuncio(self, anuncio):
        for i, a in enumerate(self.anuncios):
            if a.id == anuncio.id:
                self.anuncios[i] = anuncio
                return anuncio
        return False

    def cadastrar(self, usuario: Usuario_Identificado):
        mensagem = f"cadastramento|{usuario.to_dict_cadastramento()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "email_confirmacao":
            return [True]
        
        elif resposta[0] == "erro":
            return False, resposta[1]

        return False, ""
        
    def email_confirmacao(self, codigo):
        mensagem = f"codigo|{codigo}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return [True]
        
        elif resposta[0] == "erro":
            return False, resposta[1]
        
        return False, ""
        
    def login(self, usuario: Usuario_Identificado):
        mensagem = f"login|{usuario.to_dict_login()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return [True]
        
        elif resposta[0] == "erro":
            return False, resposta[1]
        
        return False, ""

    def visualizar_anuncios(self):
        mensagem = f"visualizar|todos_anuncios"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            anuncios = []
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "anuncios":
                    anuncio = Anuncio.from_dict(resposta[1])
                    anuncios.append(anuncio)
                    imagem = anuncio.produto.imagens[0]
                    if imagem:
                        self.socket.receive_image(path=f"uploads/{imagem}")
                else:
                    return False
            return True, anuncios
        return False   
    
    def visualizar_anuncio(self, anuncio: Anuncio):
        mensagem = f"visualizar|anuncio|{anuncio.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio = Anuncio.from_dict(resposta[1])
            for imagem in anuncio.produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True, anuncio
        return False
    
    def visualizar_produto(self, produto: Produto):
        mensagem = f"visualizar|produto|{produto.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto = Produto.from_dict(resposta[1])
            for imagem in produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True, produto
        return False
    
    def visualizar_loja(self, loja: Loja):
        mensagem = f"visualizar|loja|{loja.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            loja = Loja.from_dict(resposta[1])
            if loja.imagem:
                self.socket.receive_image(path=f"uploads/{loja.imagem}")

            lista_imagens = [anuncio.produto.imagens[0] for anuncio in loja.anuncios]
            for imagem in lista_imagens:
                    self.socket.receive_image(path=f"uploads/{imagem}")
            return True, loja
        return False
    
    def visualizar_minha_loja(self, loja: Loja):
        mensagem = f"visualizar|minha_loja|{loja.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "minha_loja":
            loja = self.usuario.editar_loja(loja, Loja.from_dict(resposta[1]))
            lista_imagens = [produto.imagens[0] for produto in loja.produtos]
            for imagem in lista_imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True, loja
        return False
    
    def visualizar_minhas_lojas(self):
        mensagem = f"visualizar|minhas_lojas|{self.usuario.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            lojas = []
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "minhas_lojas":
                    loja = Loja.from_dict(resposta[1])
                    lojas.append(loja)
                    if loja.imagem:
                        self.socket.receive_image(path=f"uploads/{loja.imagem}")
                else:
                    return False
            return True, lojas
        return False

    def visualizar_meus_enderecos(self):
        mensagem = f"visualizar|meus_enderecos|{self.usuario.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            enderecos = []
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "meus_enderecos":
                    enderecos.append(Endereco.from_dict(resposta[1]))
                else:
                    return False
            return True, enderecos
        return False
    
    def visualizar_pedido(self, pedido: Pedido):
        mensagem = f"visualizar|pedido|{pedido.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            pedido = Pedido.from_dict(resposta[1])
            for imagem in pedido.produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False, pedido

    def visualizar_meus_pedidos(self):
        mensagem = f"visualizar|meus_pedidos|{self.usuario.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            pedidos = []
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "meus_pedidos":
                    pedidos.append(Pedido.from_dict(resposta[1]))
                else:
                    return False
            self.usuario.pedidos = pedidos
            return True, pedidos
        return False

    def editar_anuncio(self, anuncio: Anuncio, novos_dados):
        mensagem = f"editar|anuncio|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            dict_resposta = json.loads(resposta[1])
            anuncio.preco = dict_resposta.get("preco", anuncio.preco)
            anuncio.quantidade_disponivel = dict_resposta.get("quantidade_disponivel", anuncio.quantidade_disponivel)
            anuncio.chave_pix = dict_resposta.get("chave_pix", anuncio.chave_pix)
            anuncio.pausado = dict_resposta.get("pausado", anuncio.pausado)

            return True, anuncio
        return False
    
    def editar_produto(self, produto: Produto, novos_dados):
        mensagem = f"editar|produto|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto = Produto.from_dict(resposta[1])
            return True, produto
        return False
    
    def editar_loja(self, loja: Loja, novos_dados):
        mensagem = f"editar|loja|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        editar_imagem = novos_dados.get("imagem", 0)
        if editar_imagem:
            self.socket.send_image(f"uploads/{editar_imagem}")

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            dict_resposta = json.loads(resposta[1])
            loja.nome = dict_resposta.get("nome", loja.nome)
            loja.imagem = dict_resposta.get("imagem", loja.imagem)

            imagem = dict_resposta.get("imagem", 0)
            if editar_imagem and imagem:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True, loja
        return False
    
    def editar_usuario(self, novos_dados):
        mensagem = f"editar|usuario|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "usuario":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return [True]
        
        elif resposta[0] == "erro":
            return False, resposta[1]
        
        return False, ""
    
    def editar_endereco(self, endereco: Endereco, novos_dados):
        mensagem = f"editar|endereco|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            endereco = Endereco.from_dict(resposta[1])
            return True, endereco
        return False
    
    def criar_anuncio(self, anuncio: Anuncio):
        mensagem = f"criar|anuncio|{anuncio.to_dict_personalizado()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio = Anuncio.from_dict(resposta[1])
            return True, anuncio
        return False
    
    def criar_produto(self, produto: Produto):
        mensagem = f"criar|produto|{produto.to_dict_personalizado()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        for imagem in produto.imagens:
            self.socket.send_image(f"uploads/{imagem}")

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto_resposta = Produto.from_dict(resposta[1])
            produto.loja.criar_produto(produto_resposta)

            for imagem in produto_resposta.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False
    
    def criar_loja(self, loja: Loja):
        mensagem = f"criar|loja|{self.usuario.id}|{loja.to_dict_personalizado()}"
        self.socket.send(mensagem)
        if loja.imagem:
            self.socket.send_image(f"uploads/{loja.imagem}")
        
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            loja = Loja.from_dict(resposta[1])
            self.usuario.criar_loja(loja)
            if loja.imagem:
                self.socket.receive_image(path=f"uploads/{loja.imagem}")
            return True
        return False
    
    def criar_pedido(self, pedido: Pedido):
        mensagem = f"criar|pedido|{self.usuario.id}|{pedido.to_dict_personalizado()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            self.usuario.criar_pedido(Pedido.from_dict(resposta[1]))
            return True
        return False
    
    def criar_endereco(self, endereco: Endereco):
        mensagem = f"criar|endereco|{self.usuario.id}|{endereco.to_dict_personalizado()}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            self.usuario.criar_endereco(Endereco.from_dict(resposta[1]))
            return True
        return False

    def criar_imagem(self, produto: Produto, imagem):
        mensagem = f"criar|imagem|{produto.id}"
        self.socket.send(mensagem)
        self.socket.send_image(f"uploads/{imagem}")
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "imagem":
            produto.criar_imagem(resposta[1])
            self.socket.receive_image(path=f"uploads/{resposta[1]}")
            return True
        return False
    
    def excluir_anuncio(self, anuncio: Anuncio):
        mensagem = f"excluir|anuncio|{anuncio.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            return True
        return False
    
    def excluir_produto(self, produto: Produto):
        mensagem = f"excluir|produto|{produto.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            return True
        return False
    
    def excluir_loja(self, loja: Loja):
        mensagem = f"excluir|loja|{loja.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            self.usuario.apagar_loja(loja)
            return True
        return False
    
    def excluir_endereco(self, endereco: Endereco):
        mensagem = f"excluir|endereco|{endereco.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            self.usuario.apagar_endereco(endereco)
            return True
        return False
    
    def excluir_imagem(self, produto: Produto, imagem):
        mensagem = f"excluir|imagem|{imagem}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "imagem":
            produto.apagar_imagem(imagem)
            return True
        return False

    def confirmar_pedido(self, pedido: Pedido, loja: Loja):
        mensagem = f"pedido|confirmar|{pedido.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.confirmar_pedido(pedido)
            return True
        return False
    
    def cancelar_pedido(self, pedido: Pedido, loja: Loja):
        mensagem = f"pedido|cancelar|{pedido.id}"
        self.socket.send(mensagem)
        self.socket.limpar_buffer_socket()

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.cancelar_pedido(pedido)
            return True
        return False
