from models.usuario import Usuario, Usuario_Identificado
from models.cliente import UnixSocketClient
from models.endereco import Endereco
from models.anuncio import Anuncio
from models.produto import Produto
from models.pedido import Pedido
from models.loja import Loja

class Main():
    def __init__(self):
        end = Endereco(rua="Aristides Teixeira Duarte", numero=234, bairro="California", cidade="Florestal", estado="MG", complemento="Apartamento 205")
        # Produtos
        p1 = Produto(id=1, nome="Notebook Dell", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p2 = Produto(id=2, nome="Mouse sem fio", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p3 = Produto(id=3, nome="Cadeira Gamer", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p4 = Produto(id=4, nome="Monitor 24\"", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p5 = Produto(id=5, nome="Teclado Mecânico", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p6 = Produto(id=6, nome="Webcam Full HD", descricao="ifediejide", imagens=["imagens/notebook.png"])

        # Anúncios
        a1 = Anuncio(id=1, produto=p1)
        a2 = Anuncio(id=2, produto=p2)
        a3 = Anuncio(id=3, produto=p3)
        a4 = Anuncio(id=4, produto=p6)

        # Pedidos
        pedido1 = Pedido(id=1, produto=p1, preco=3620.0)
        pedido2 = Pedido(id=2, produto=p3, preco=950.0)
        pedido3 = Pedido(id=3, produto=p5, preco=440.0)
        pedido4 = Pedido(id=4, produto=p6, preco=200.0)

        # Loja 1: completa
        loja1 = Loja(
            id=101,
            nome="Digital Tech",
            imagem="imagens/notebook.png",
            produtos=[p1, p2, p3, p4, p5, p1, p2, p3, p4, p5, p1, p2, p3, p4, p5],
            anuncios=[a1, a2, a3, a1, a2, a3, a1, a2, a3],
            pedidos_confirmados=[pedido1, pedido2, pedido3, pedido1, pedido2, pedido3, pedido1, pedido2, pedido3],
            pedidos_em_andamento=[pedido1, pedido2, pedido3]
        )

        # Loja 2: simples
        loja2 = Loja(
            id=102,
            nome="WebStore",
            imagem="imagens/notebook.png",
            produtos=[p6],
            anuncios=[a4],
            pedidos_confirmados=[pedido4]
        )

        # Loja 3: vazia
        loja3 = Loja(
            id=103,
            nome="Nova Loja",
            imagem="imagens/notebook.png"
        )

        # Lista de lojas
        lojas = [loja1, loja2, loja3]

        # Produtos
        p1 = Produto(id=1, nome="Notebook Dell", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p2 = Produto(id=2, nome="Mouse sem fio", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p3 = Produto(id=3, nome="Cadeira Gamer", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p4 = Produto(id=4, nome="Monitor 24\"", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p5 = Produto(id=5, nome="Teclado Mecânico", descricao="dinedendine", imagens=["imagens/tablet.png"])
        p6 = Produto(id=6, nome="Webcam Full HD", descricao="ifediejide", imagens=["imagens/notebook.png"])
        
        pedidos = [
            Pedido(id=1, produto=p1, preco=3620.0),
            Pedido(id=2, produto=p3, preco=950.0),
            Pedido(id=3, produto=p5, preco=440.0),
            Pedido(id=4, produto=p6, preco=200.0),
        ]
        #self.usuario = Usuario()

        self.usuario = Usuario_Identificado(
            nome="Sabrina Bruni de Souza Faria",
            cpf="136.689.956-30",
            email="sabrina.b.faria@ufv.br",
            senha="123**",
            enderecos=[end],
            lojas=lojas,
            pedidos=pedidos
        )
        self.anuncios = []
        #self.socket = UnixSocketClient(ip="192.168.1.102", port=5000)

    def divide_mensagem(self, stringMensagem):
        [ws.strip() for ws in stringMensagem.split('|')]
    
    def is_identificado(self):
        return isinstance( self.usuario, Usuario_Identificado)

    def cadastrar(self, usuario: Usuario_Identificado):
        return True
        mensagem = f"cadastramento|{usuario.to_dict_cadastramento()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "email_confirmacao":
            return True, "sucesso"
        
        elif resposta[0] == "erro":
            return False, resposta[1]
        
    def email_confirmacao(self, codigo):
        return True, ""
        mensagem = f"codigo|{codigo}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return True, "sucesso"
        
        elif resposta[0] == "erro":
            return False, resposta[1]
        
    def login(self, usuario: Usuario_Identificado):
        mensagem = f"login|{usuario.to_dict_login()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return True
        
        elif resposta[0] == "erro":
            return resposta[1]
        
    def visualizar_anuncios(self):
        self.anuncios = self.criar_lista_anuncios()
        return
        mensagem = f"visualizar|todos_anuncios"
        self.socket.send(mensagem)
        print("Enviar:", mensagem)
        print("Reposta:")
        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncios":
            for i in range(0, len(resposta)):
                print(resposta[i])
                #self.anuncios.append(Anuncio.from_dict(resposta[i]))
            return True
        print(resposta)
        return False
    
    def visualizar_anuncio(self, anuncio: Anuncio):
        mensagem = f"visualizar|anuncio|{anuncio.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio = Anuncio.from_dict(resposta[1])
            return True
        
        return False
    
    def visualizar_produto(self, produto: Produto):
        mensagem = f"visualizar|produto|{produto.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto = Produto.from_dict(resposta[1])
            return True
        
        return False
    
    def visualizar_loja(self, loja: Loja):
        mensagem = f"visualizar|loja|{loja.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            loja = Loja.from_dict(resposta[1])
            return True
        
        return False
    
    def visualizar_minha_loja(self, loja: Loja):
        mensagem = f"visualizar|minha_loja|{loja.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "minha_loja":
            loja = Loja.from_dict(resposta[1])
            return True
        
        return False
    
    def visualizar_minhas_lojas(self):
        mensagem = f"visualizar|minhas_lojas|{self.usuario.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "minhas_lojas":
            for i in range(1, len(resposta)):
                self.usuario.lojas.append(Loja.from_dict(resposta[i]))
            return True
        
        return False
    
    def visualizar_pedido(self, pedido: Pedido):
        mensagem = f"visualizar|pedido|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            pedido = Pedido.from_dict(resposta[1])
            return True
        
        return False

    def visualizar_meus_pedidos(self):
        mensagem = f"visualizar|meus_pedidos|{self.usuario.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "meus_pedidos":
            for i in range(1, len(resposta)):
                self.usuario.pedidos.append(Pedido.from_dict(resposta[i]))
            return True
        
        return False

    def editar_anuncio(self, anuncio: Anuncio, novos_dados):
        return True
        mensagem = f"editar|anuncio|{anuncio.id}|{novos_dados}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio = Anuncio.from_dict(resposta[1])
            return True
        
        return False
    
    def editar_produto(self, produto: Produto, novos_dados):
        return True
        mensagem = f"editar|produto|{produto.id}|{novos_dados}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto = Produto.from_dict(resposta[1])
            return True
        
        return False
    
    def editar_loja(self, loja: Loja, novos_dados):
        return True
        mensagem = f"editar|loja|{loja.id}|{novos_dados}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            loja = Loja.from_dict(resposta[1])
            return True
        
        return False
    
    def editar_usuario(self, novos_dados):
        return True
        mensagem = f"editar|usuario|{self.usuario.id}|{novos_dados}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "usuario":
            self.usuario = Usuario_Identificado.from_dict(resposta[1])
            return True
        
        elif resposta[0] == "erro":
            return resposta[1]
        
        return False
    
    def editar_endereco(self, endereco: Endereco, novos_dados):
        return True
        mensagem = f"editar|endereco|{endereco.id}|{novos_dados}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            endereco = Endereco.from_dict(resposta[1])
            return True

        return False
    
    def criar_anuncio(self, anuncio: Anuncio):
        return True
        mensagem = f"criar|anuncio|{anuncio.to_dict_personalisado()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio.produto.loja.criar_anuncio(Anuncio.from_dict(resposta[1]))
            return True
        
        return False
    
    def criar_produto(self, produto: Produto):
        return True
        mensagem = f"criar|produto|{produto.to_dict_personalisado()}"
        self.socket.send(mensagem)

        for imagem in produto.imagens:
            self.socket.send_image(imagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto.loja.criar_produto(Produto.from_dict(resposta[1]))

            for imagem in produto.imagens:
                self.socket.receive_image(path=imagem)

            return True
        
        return False
    
    def criar_loja(self, loja: Loja):
        return True
        mensagem = f"criar|loja|{self.usuario.id}|{loja.to_dict_personalisado()}"
        self.socket.send(mensagem)
        self.socket.send_image(loja.imagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "loja":
            self.usuario.criar_loja(Loja.from_dict(resposta[1]))
            self.socket.receive_image(path=loja.imagem)
            return True
        
        return False
    
    def criar_pedido(self, pedido: Pedido):
        return True
        mensagem = f"criar|pedido|{self.usuario.id}|{pedido.to_dict_personalisado()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "pedido":
            self.usuario.criar_pedido(Pedido.from_dict(resposta[1]))
            return True
        
        return False
    
    def criar_endereco(self, endereco: Endereco):
        return True
        mensagem = f"criar|endereco|{self.usuario.id}|{endereco.to_dict_personalisado()}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "endereco":
            self.usuario.criar_endereco(Endereco.from_dict(resposta[1]))
            return True
        
        return False
    
    def excluir_anuncio(self, anuncio: Anuncio):
        return True
        mensagem = f"excluir|anuncio|{anuncio.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "anuncio":
            anuncio.produto.loja.apagar_anuncio(anuncio)
            return True
        
        return False
    
    def excluir_produto(self, produto: Produto):
        return True
        mensagem = f"excluir|produto|{produto.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "produto":
            produto.loja.apagar_produto(produto)
            return True
        
        return False
    
    def excluir_loja(self, loja: Loja):
        return True
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
            self.usuario.apagar_endereco(endereco)
            return True
        
        return False
    
    def confirmar_pedido(self, pedido: Pedido, loja: Loja):
        return True
        mensagem = f"pedido|confirmar|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.confirmar_pedido(pedido)
            return True
        
        return False
    
    def cancelar_pedido(self, pedido: Pedido, loja: Loja):
        return True
        mensagem = f"pedido|cancelar|{pedido.id}"
        self.socket.send(mensagem)

        resposta = self.divide_mensagem(self.socket.receive())
        if resposta[0] == "ok":
            loja.cancelar_pedido(pedido)
            return True
        
        return False
    


    def criar_lista_anuncios(self):
        return [
            Anuncio(
                produto=Produto(
                    nome="Notebook", 
                    descricao="Notebook potente com 16GB RAM",
                    imagens=["imagens/notebook.png", "imagens/smartphone.png", "imagens/notebook.png"],
                    loja=Loja(
                        nome="Ferramentas", 
                        imagem="imagens/tablet.png"
                    )
                ),
                preco=10.90,
                quantidade_disponivel=10,
                chave_pix="13668995630"
            ),
            Anuncio(
                produto=Produto(
                    nome="Tablet", 
                    descricao="Notebook potente com 16GB RAM",
                    imagens=["imagens/tablet.png"],
                    loja=Loja(
                        nome="Ferramentas", 
                        imagem="imagens/tablet.png"
                    )
                ),
                preco=100.90,
                quantidade_disponivel=20,
                chave_pix="13668995630"
            ),
        ] * 20