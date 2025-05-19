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
        print("IP:", ip, "Porta:", porta)
        self.anuncios = []
        #self.usuario = Usuario()
        self.usuario = Usuario_Identificado(
            id=0, nome="Nome", cpf="000.000.000-00", email="email@example.com", senha="senha123",
        )
        self.usuario.enderecos = [Endereco(
            id=0, rua="Aristides", numero=50, bairro="California", cidade="Florestal", estado="MG", complemento="Complemento"
        )]
        self.socket = UnixSocketClient(ip, porta)

    def chamar(self, obj, *args, **kwargs):
        nome_funcao = f"visualizar_{obj}"
        func = getattr(self, nome_funcao, None)
        if func:
            try:
                resposta = func(*args, **kwargs)
                return resposta
            except TypeError as e:
                print(f"Erro ao chamar '{nome_funcao}': {e}")
        else:
            print(f"Função '{nome_funcao}' não encontrada.")
            return False

    def divide_mensagem(self, stringMensagem):
        if not stringMensagem:
            return [""]
        return [ws.strip() for ws in stringMensagem.split('|')]
    
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

    def atributos_preenchidos(self, obj, incluir=None):
        atributos = vars(obj)
        for nome, valor in atributos.items():
            if incluir and nome not in incluir:
                continue  # ignora atributos que não estão na lista
            if not valor:
                return False
        return True

    def _atributos_preenchidos(self, obj, ignorar=None):
        atributos = vars(obj)
        for nome, valor in atributos.items():
            if ignorar and nome in ignorar:
                continue  # ignora os atributos da lista
            if not valor:
                return False
        return True

    def cadastrar(self, usuario: Usuario_Identificado):
        mensagem = f"cadastramento|{usuario.to_dict_cadastramento()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "email_confirmacao":
            return [True]
        
        elif resposta[0] == "erro":
            return False, resposta[1]

        return False, ""
        
    def email_confirmacao(self, codigo):
        mensagem = f"codigo|{codigo}"
        self.socket.send(mensagem)

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

        quantidade = self.socket.receive_size()
        print("Quantidade de anuncios:", quantidade)
        if self.is_inteiro(quantidade):
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "anuncios":
                    anuncio = Anuncio.from_dict(resposta[1])
                    print(anuncio)
                    self.anuncios.append(anuncio)
                    for imagem in anuncio.produto.imagens:
                        self.socket.receive_image(path=f"uploads/{imagem}")
                else:
                    return False
            return True
        return False   
    
    def visualizar_anuncio(self, anuncio: Anuncio):
        if self._atributos_preenchidos(anuncio, ignorar=["pausado"]):
            return True

        mensagem = f"visualizar|anuncio|{anuncio.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio = Anuncio.from_dict(resposta[1])
            for imagem in anuncio.produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False
    
    def visualizar_produto(self, produto: Produto):
        if self.atributos_preenchidos(produto):
            return True

        mensagem = f"visualizar|produto|{produto.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto = Produto.from_dict(resposta[1])
            for imagem in produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False
    
    def visualizar_loja(self, loja: Loja):
        if self.atributos_preenchidos(loja, incluir=['id', 'nome', 'anuncios']):
            return True

        mensagem = f"visualizar|loja|{loja.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            loja = Loja.from_dict(resposta[1])
            if loja.imagem:
                self.socket.receive_image(path=f"uploads/{loja.imagem}")

            for anuncio in loja.anuncios:
                for imagem in anuncio.produto.imagens:
                    self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False
    
    def visualizar_minha_loja(self, loja: Loja):
        if self._atributos_preenchidos(loja, ignorar=["imagem"]):
            return True

        mensagem = f"visualizar|minha_loja|{loja.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "minha_loja":
            loja = Loja.from_dict(resposta[1])
            for produto in loja.produtos:
                for imagem in produto.imagens:
                    self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False
    
    def visualizar_minhas_lojas(self):
        if self.usuario.lojas:
            return True

        mensagem = f"visualizar|minhas_lojas|{self.usuario.id}"
        self.socket.send(mensagem)

        quantidade = self.socket.receive_size()
        print("Quantidade de lojas:", quantidade)
        if self.is_inteiro(quantidade):
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "minhas_lojas":
                    loja = Loja.from_dict(resposta[1])
                    self.usuario.lojas.append(loja)
                    if loja.imagem:
                        self.socket.receive_image(path=f"uploads/{loja.imagem}")
                else:
                    return False
            return True
        return False

    def visualizar_meus_enderecos(self):
        if self.usuario.enderecos:
            return True

        mensagem = f"visualizar|meus_enderecos|{self.usuario.id}"
        self.socket.send(mensagem)
        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "meus_enderecos":
                    self.usuario.enderecos.append(Endereco.from_dict(resposta[1]))
                else:
                    return False
            return True
        return False
    
    def visualizar_pedido(self, pedido: Pedido):
        if self.atributos_preenchidos(pedido):
            return True

        mensagem = f"visualizar|pedido|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            pedido = Pedido.from_dict(resposta[1])
            for imagem in pedido.produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")
            return True
        return False

    def visualizar_meus_pedidos(self):
        if self.usuario.pedidos:
            return True

        mensagem = f"visualizar|meus_pedidos|{self.usuario.id}"
        self.socket.send(mensagem)
        quantidade = self.socket.receive_size()
        if self.is_inteiro(quantidade):
            for i in range(quantidade):
                resposta = self.divide_mensagem(self.socket.receive())
                if resposta[0] == "meus_pedidos":
                    self.usuario.pedidos.append(Pedido.from_dict(resposta[i]))
                else:
                    return False
            return True
        return False

    def editar_anuncio(self, anuncio: Anuncio, novos_dados):
        mensagem = f"editar|anuncio|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio.produto.loja.editar_anuncio(anuncio, Anuncio.from_dict(resposta[1]))
            return True
        return False
    
    def editar_produto(self, produto: Produto, novos_dados):
        mensagem = f"editar|produto|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto.loja.editar_produto(produto, Produto.from_dict(resposta[1]))
            return True
        return False
    
    def editar_loja(self, loja: Loja, novos_dados):
        mensagem = f"editar|loja|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)

        if novos_dados.get("imagem", 0):
            self.socket.send_image(novos_dados["imagem"])

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            self.usuario.editar_loja(loja, Loja.from_dict(resposta[1]))
            if loja.imagem:
                self.socket.receive_image(path=f"uploads/{loja.imagem}")
            return True
        return False
    
    def editar_usuario(self, novos_dados):
        mensagem = f"editar|usuario|{json.dumps(novos_dados)}"
        self.socket.send(mensagem)

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

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            self.usuario.editar_endereco(endereco, Endereco.from_dict(resposta[1]))
            return True
        return False
    
    def criar_anuncio(self, anuncio: Anuncio):
        mensagem = f"criar|anuncio|{anuncio.to_dict_personalizado()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio.produto.loja.criar_anuncio(Anuncio.from_dict(resposta[1]))
            return True
        return False
    
    def criar_produto(self, produto: Produto):
        mensagem = f"criar|produto|{produto.to_dict_personalizado()}"
        self.socket.send(mensagem)

        for imagem in produto.imagens:
            self.socket.send_image(imagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto.loja.criar_produto(Produto.from_dict(resposta[1]))

            for imagem in produto.imagens:
                self.socket.receive_image(path=f"uploads/{imagem}")

            return True
        return False
    
    def criar_loja(self, loja: Loja):
        mensagem = f"criar|loja|{self.usuario.id}|{loja.to_dict_personalizado()}"
        self.socket.send(mensagem)
        if loja.imagem:
            self.socket.send_image(loja.imagem)

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

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            self.usuario.criar_pedido(Pedido.from_dict(resposta[1]))
            return True
        return False
    
    def criar_endereco(self, endereco: Endereco):
        mensagem = f"criar|endereco|{self.usuario.id}|{endereco.to_dict_personalizado()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            self.usuario.criar_endereco(Endereco.from_dict(resposta[1]))
            return True
        return False

    def criar_imagem(self, produto: Produto, imagem):
        mensagem = f"criar|imagem|{produto.id}"
        self.socket.send(mensagem)
        self.socket.send_image(imagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "imagem":
            produto.criar_imagem(resposta[1])
            self.socket.receive_image(resposta[1])
            return True
        return False
    
    def excluir_anuncio(self, anuncio: Anuncio):
        mensagem = f"excluir|anuncio|{anuncio.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio.produto.loja.apagar_anuncio(anuncio)
            return True
        return False
    
    def excluir_produto(self, produto: Produto):
        mensagem = f"excluir|produto|{produto.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto.loja.apagar_produto(produto)
            return True
        return False
    
    def excluir_loja(self, loja: Loja):
        mensagem = f"excluir|loja|{loja.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            self.usuario.apagar_loja(loja)
            return True
        return False
    
    def excluir_endereco(self, endereco: Endereco):
        mensagem = f"excluir|endereco|{endereco.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            print("Excluindo endereco")
            print(endereco)
            print(self.usuario.enderecos)
            self.usuario.apagar_endereco(endereco)
            print(self.usuario.enderecos)
            return True
        return False
    
    def excluir_imagem(self, produto: Produto, imagem):
        mensagem = f"excluir|imagem|{imagem}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "imagem":
            produto.apagar_imagem(imagem)
            return True
        return False

    def confirmar_pedido(self, pedido: Pedido, loja: Loja):
        mensagem = f"pedido|confirmar|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.confirmar_pedido(pedido)
            return True
        return False
    
    def cancelar_pedido(self, pedido: Pedido, loja: Loja):
        mensagem = f"pedido|cancelar|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.cancelar_pedido(pedido)
            return True
        return False
