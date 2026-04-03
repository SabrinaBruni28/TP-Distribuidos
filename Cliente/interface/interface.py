import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.loja import Loja
from models.pedido import Pedido
from models.produto import Produto
from models.anuncio import Anuncio
from models.endereco import Endereco
from models.usuario import Usuario, Usuario_Identificado
from cliente_aplicacao import ClienteAplicacao
from forms import Formulario, FormularioOpcoes
from view_utils import CarrosselImagem, WidgetHelper, CaixaConfirmacao, ViewHelper, Threads
from utils import Utils

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
   QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QDialog, QGraphicsOpacityEffect,
   QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QStackedWidget
)

ip = "127.0.0.1"
porta = 9090

class MarketplaceUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caldeirão")
        self.setGeometry(100, 100, 1000, 600)
        self.showMaximized()
        Utils.cria_pasta("uploads/")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.view = ViewHelper()
        self.grid = None
        self.imagem = None

        self.handler = InterfaceHandler(parent=self, stack=self.stack)
        self.handler.visualizar_anuncios(self.tela_inicial)

    ##############  AUXILIARES  ################
    def substituir_imagem(self):
        nome_imagem = WidgetHelper.abrir_dialogo_arquivo(self)
        if nome_imagem:
            self.imagem = nome_imagem
            return True

        self.imagem = None
        return False

    def excluir_imagem(self, obj):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar",
            mensagem=f"Você tem certeza que deseja excluir a imagem {obj}?",
            largura=500
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            self.imagem = ""
            return True

        self.imagem = None
        dialogo.close()
        return False

    def closeEvent(self, event):
        dialogo = CaixaConfirmacao(self, titulo="Confirmar saída", mensagem="Você tem certeza que deseja sair?")
        resposta = dialogo.exec()

        if resposta == QDialog.DialogCode.Accepted:
            Utils.excluir_arquivos_pasta("uploads")
            event.accept()
        else:
            event.ignore()

    def toggle_menu(self):
        if self.barra_lateral.isVisible():
            self.barra_lateral.hide()
        else:
            self.barra_lateral.show()

    def mostrar_barra_pesquisa(self):
        self.input_busca.show()
        self.botao_reset.show()
        self.input_busca.setFocus()
        self.input_busca.textChanged.connect(self.aplicar_filtro)

    def aplicar_filtro(self, texto):
        texto = texto.lower().strip()
        anuncios_filtrados = [
            a for a in self.handler.aplicacao.anuncios if texto in a.produto.nome.lower()
        ]
        self.atualizar_lista_anuncios(anuncios_filtrados)

    def resetar_busca(self):
        self.input_busca.clear()
        self.input_busca.hide()
        self.botao_reset.hide()
        self.atualizar_lista_anuncios(self.handler.aplicacao.anuncios)

    def atualizar_lista_anuncios(self, nova_lista):
        # Remove widgets antigos
        if self.grid:
            for i in reversed(range(self.grid.count())):
                widget = self.grid.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

        largura_bloco = 250
        altura_bloco = 300

        for i, anuncio in enumerate(nova_lista):
            bloco = self.bloco_anuncio(anuncio, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)

    def comprar(self, anuncio: Anuncio, formularioOp: FormularioOpcoes):
        valores = formularioOp.obter_valores()
        if not valores["Endereço"]:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Adicione um endereço"
            )
            return

        pedido = Pedido(
            anuncio=anuncio, 
            quantidade=int(valores["Quantidade"]),
            endereco=self.handler.aplicacao.usuario.get_endereco(valores["Endereço"])
        )
        self.view.abrir_tela(self.stack, lambda: self.tela_pagamento(pedido, anuncio))
    
    #############  BLOCOS  #################
    def bloco_anuncio(self, anuncio: Anuncio, largura, altura):
        bloco = WidgetHelper.bloco(largura, altura)
        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        imagem_label = WidgetHelper.imagem(anuncio.produto.imagens[0], scaled=170)
        layout.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_nome = WidgetHelper.label_b(anuncio.produto.nome)
        layout.addWidget(label_nome, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_preco = WidgetHelper.label_preco(anuncio.preco)
        layout.addWidget(label_preco, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.handler.visualizar_anuncio(self.tela_detalhes_anuncio, anuncio)
        return bloco

    def bloco_anuncio_loja(self, anuncio: Anuncio, loja: Loja, largura, altura):
        bloco = WidgetHelper.bloco(largura, altura)
        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        if anuncio.produto.imagens:
            imagem_label = WidgetHelper.imagem(anuncio.produto.imagens[0], scaled=170)
            layout.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addSpacing(5)

        label_nome = WidgetHelper.label_b(anuncio.produto.nome)
        layout.addWidget(label_nome, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_preco = WidgetHelper.label_preco(anuncio.preco)
        layout.addWidget(label_preco, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.handler.visualizar_anuncio(self.tela_editar_anuncio, anuncio)
        return bloco

    def bloco_produto(self, produto: Produto, loja: Loja, largura, altura):
        bloco = WidgetHelper.bloco(largura, altura)
        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        imagem_label = WidgetHelper.imagem(produto.imagens[0])
        layout.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_nome = WidgetHelper.label_b(produto.nome)
        layout.addWidget(label_nome, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.handler.visualizar_produto(self.tela_editar_produto, produto)
        return bloco
    
    def bloco_pedido(self, pedido: Pedido, largura, altura, pedido_confirmado = True, botao_confirmar = False, botao_loja = True):
        bloco = WidgetHelper.bloco(largura, altura)
        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        label_data = WidgetHelper.label_b(pedido.data)
        layout.addWidget(label_data, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_nome = WidgetHelper.label_b(pedido.anuncio.produto.nome)
        layout.addWidget(label_nome, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_qnt = WidgetHelper.label_b(pedido.quantidade)
        layout.addWidget(label_qnt, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        label_preco = WidgetHelper.label_preco(pedido.quantidade * pedido.anuncio.preco)
        layout.addWidget(label_preco, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.handler.visualizar_pedido(self.tela_detalhes_pedido, pedido, pedido_confirmado, botao_confirmar, botao_loja)
        return bloco
    
    def bloco_loja(self, loja: Loja, largura, altura):
        bloco = WidgetHelper.bloco(largura, altura)
        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        if loja.imagem:
            imagem_label = WidgetHelper.imagem(loja.imagem, scaled=180)
            layout.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addSpacing(5)

        label_nome = WidgetHelper.label_b(loja.nome)
        layout.addWidget(label_nome, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.handler.visualizar_minha_loja(loja, self.tela_detalhes_minha_loja)
        return bloco
    
    ###################  TELAS  ########################
    def tela_inicial(self):
        self.handler.aplicacao.atualiza_anuncios()
        tela = QWidget()

        # Layout horizontal principal (menu + conteúdo)
        layout_h = QHBoxLayout(tela)

        # Adiciona a barra lateral ao layout principal (inicialmente oculta)
        self.barra_lateral = self.menu_lateral()
        layout_h.addWidget(self.barra_lateral)
        
        # Layout vertical para o conteúdo da tela
        layout_conteudo = QVBoxLayout()

        barra_superior = self.barra_superior()
        layout_conteudo.addLayout(barra_superior)
        
        anuncios = self.handler.aplicacao.anuncios

        if anuncios:
            tela_lista = self.tela_lista_anuncios_gerais(anuncios)
            layout_conteudo.addWidget(tela_lista)
        else:
            label = WidgetHelper.label_b("Nenhum anúncio disponível.", 20, alignment=Qt.AlignmentFlag.AlignCenter)
            layout_conteudo.addWidget(label)

        # Agora adiciona o conteúdo principal no layout horizontal
        layout_h.addLayout(layout_conteudo)

        return tela

    def tela_comprar(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)

        titulo = WidgetHelper.label_span("Comprar", 50)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = FormularioOpcoes(campos=["Quantidade", "Endereço"],largura=600, altura=50)

        for end in self.handler.aplicacao.usuario.enderecos:
            formulario.adicionar_opcao(campo="Endereço", opcao=end.__str__())

        formulario.ativar_botao_adicionar(campo="Endereço", acao=lambda: self.view.abrir_tela(self.stack, self.tela_criar_endereco))

        for i in range(anuncio.quantidade_disponivel):
            formulario.adicionar_opcao(campo="Quantidade", opcao=str(i+1))

        layout_vertical.addWidget(formulario, alignment=Qt.AlignmentFlag.AlignHCenter)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.comprar(anuncio, formulario)
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela
    
    def tela_pagamento(self, pedido: Pedido, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)
        layout_vertical.addSpacing(10)

        titulo = WidgetHelper.label_span("Pagamento", 50)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        try:
            dados = Utils.gerar_qrcode_pix(
                nome=anuncio.produto.nome,
                chave=anuncio.chave_pix,
                cidade="Florestal",
                valor=pedido.calcular_total(),
                descricao="Pagamento de pedido",
                pagamento_multiplo=False,
                nome_arquivo="images/qrcode",
                salvar_png = True,
                salvar_svg = False
            )
        except (Exception, AttributeError) as e:
            self.view.set_tela(self.stack, -1)
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self,
                backcolor="#f44336",
                posicao="superior_direita",
                mensagem="Erro ao gerar qrcode!"
            )
            print("Erro ao gerar QR Code:", e)
            return None

        imagem_label = WidgetHelper.imagem(pasta="images/",imagem="qrcode.png", scaled=300)
        layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addSpacing(10)

        string = WidgetHelper.label_span(dados['payload'], 12, Qt.AlignmentFlag.AlignCenter)
        string.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        string.setWordWrap(True)
        string.setMaximumWidth(500)
        layout_vertical.addWidget(string, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_copiar = WidgetHelper.botao(
            nome="Copiar chave", fonte=15,
            backcolor="",
            hover='#D3D3D3', pressed='#000000',
            acao=lambda: (
                WidgetHelper.copiar_texto(string),
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Chave pix copiada!"
                )
            )
        )
        layout_vertical.addWidget(botao_copiar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addSpacing(10)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.handler.criar_pedido(pedido, anuncio)
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela
    
    def tela_codigo_confirmacao(self, id_confirmacao):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(50)

        titulo = WidgetHelper.label_span("Código de Confirmação", 50)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Código"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=500, altura=50,
            acao=lambda: self.handler.confirmar_codigo(id_confirmacao, formulario)
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela

    def tela_cadastro(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(30)

        titulo = WidgetHelper.label_span("Cadastramento", 60)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Nome", "CPF", "Email", "Senha"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_cadastrar = WidgetHelper.botao(
            nome="Cadastrar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.handler.cadastrar(formulario)
        )
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela

    def tela_login(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addSpacing(30)

        titulo = WidgetHelper.label_span("Login", 60)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Email", "Senha"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_login = WidgetHelper.botao(
            nome="Entrar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.handler.login(formulario)
        )
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_cadastrar = WidgetHelper.botao(
            nome="Cadastrar",
            acao=lambda: self.view.abrir_tela(self.stack, self.tela_cadastro)
        )
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignRight)

        return tela
    
    def tela_meus_enderecos(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = WidgetHelper.label_span("Meus Endereços", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        layout_horizontal2 = QHBoxLayout()
        usuario = self.handler.aplicacao.usuario
        quantidade = len(usuario.enderecos)

        if quantidade:
            formulario = Formulario(
                campos=[f"Endereço {i+1}" for i in range(quantidade)],
                largura=800,
                altura=50
            )
            formulario.preencher_campos(
                {f"Endereço {i+1}": usuario.enderecos[i].__str__() for i in range(quantidade)}
            )
            formulario.bloquear_campos([f"Endereço {i+1}" for i in range(quantidade)])
            layout_horizontal2.addWidget(formulario)

            layout_vertical2 = QVBoxLayout()
        
            botao_editar = []
            for i in range(quantidade):
                botao = WidgetHelper.botao(
                    nome="Editar",
                    acao=lambda _, i=i: self.view.abrir_tela(self.stack, lambda: self.tela_editar_endereco(usuario.enderecos[i]))
                )
                botao_editar.append(botao)
                layout_vertical2.addWidget(botao)

            layout_horizontal2.addLayout(layout_vertical2)
            layout_conteudo.addLayout(layout_horizontal2)
        else:
            label = WidgetHelper.label_b("Você não possui endereços.", 20, alignment=Qt.AlignmentFlag.AlignCenter)
            layout_conteudo.addWidget(label)

        botao_adicionar = WidgetHelper.botao(
                nome="Adicionar",
                acao=lambda: self.view.abrir_tela(self.stack, self.tela_criar_endereco)
            )
        layout_conteudo.addStretch()
        layout_conteudo.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def tela_minhas_lojas(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)
        layout_horizintal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizintal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_adicionar = WidgetHelper.botao(
            nome="Adicionar",
            acao=lambda: self.view.abrir_tela(self.stack, self.tela_criar_loja)
        )
        layout_horizintal.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizintal)
        layout_vertical.addSpacing(40)

        titulo = WidgetHelper.label_span("Minhas Lojas", 50)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        # Scroll area e seu conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        conteudo_scroll = QWidget()
        layout_loja = QVBoxLayout(conteudo_scroll)
        layout_loja.setSpacing(15)

        lojas = self.handler.aplicacao.usuario.lojas

        if lojas:
            # Adiciona os blocos no layout do conteúdo do scroll
            blocos = self.tela_lista_lojas(lojas)
            layout_loja.addWidget(blocos)
        else:
            label = WidgetHelper.label_b("Você não possui lojas.", 20, alignment=Qt.AlignmentFlag.AlignCenter)
            layout_loja.addWidget(label)

        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def tela_meus_pedidos(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(40)

        titulo = WidgetHelper.label_span("Meus Pedidos", 50)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        layout_horizontal2 = QHBoxLayout()

        botao_pedidos_confirmados = WidgetHelper.botao(
            nome="Pedidos Confirmados", fonte=18,
            largura=250,
        )
        layout_horizontal2.addWidget(botao_pedidos_confirmados)

        botao_pedidos_em_andamento = WidgetHelper.botao(
            nome="Pedidos Em Andamento", fonte=18,
            largura=230
        )
        layout_horizontal2.addWidget(botao_pedidos_em_andamento)

        pedidos_confirmados = self.handler.aplicacao.usuario.pedidos_confirmados
        pedidos_andamento = self.handler.aplicacao.usuario.pedidos_andamento

        if pedidos_confirmados:
            lista_pedidos_confirmados = self.tela_lista_pedidos(pedidos_confirmados, pedido_confirmado=True, botao_loja=True)
        else:
            lista_pedidos_confirmados = WidgetHelper.label_b("Você não possui pedidos confirmados.", 20, alignment=Qt.AlignmentFlag.AlignCenter)

        if pedidos_andamento:
            lista_pedidos_em_andamento = self.tela_lista_pedidos(pedidos_andamento, pedido_confirmado=False, botao_loja=True)
        else:
            lista_pedidos_em_andamento = WidgetHelper.label_b("Você não possui pedidos em andamento.", 20, alignment=Qt.AlignmentFlag.AlignCenter)

        # Container para trocar os conteúdos
        container_listas = QStackedWidget()
        container_listas.addWidget(lista_pedidos_confirmados)
        container_listas.addWidget(lista_pedidos_em_andamento)

        botao_pedidos_confirmados.clicked.connect(lambda: container_listas.setCurrentWidget(lista_pedidos_confirmados))
        botao_pedidos_em_andamento.clicked.connect(lambda: container_listas.setCurrentWidget(lista_pedidos_em_andamento))

        layout_vertical.addLayout(layout_horizontal2)
        layout_vertical.addSpacing(10)
        layout_vertical.addWidget(container_listas)

        return tela
    
    ##############  TELAS DE CRIAÇÃO  #################
    def tela_criar_endereco(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar"
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = WidgetHelper.label_span("Criar Endereço", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Rua", "Número", "Bairro", "Cidade", "Estado", "Complemento"],
            largura=600,
            altura=50
        )
        botao_confirmar.clicked.connect(lambda: self.handler.criar_endereco(formulario))
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_criar_loja(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar"
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = WidgetHelper.label_span("Criar Loja", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome"],
            largura=600,
            altura=50
        )
        layout_conteudo.addWidget(formulario)

        layout_horizontal_2 = QHBoxLayout()
        layout_horizontal_2.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        imagem = ""
        label_imagem = QLabel()
        layout_horizontal_2.addWidget(label_imagem)

        botao_substituir = WidgetHelper.botao(
            nome="Adicionar imagem", 
            fonte=10, largura=100, altura=30,
            acao= lambda: (self.substituir_imagem(), atualiza_imagem())
        )
        layout_horizontal_2.addWidget(botao_substituir)

        botao_excluir_img = WidgetHelper.botao(
            nome="Excluir imagem", fonte=10,
            largura=100, altura=30,
            acao= lambda: (self.excluir_imagem(imagem), atualiza_imagem())
        )
        layout_horizontal_2.addWidget(botao_excluir_img)
        botao_excluir_img.hide()

        layout_conteudo.addLayout(layout_horizontal_2)

        def atualiza_imagem():
            nonlocal imagem, label_imagem, botao_excluir_img, botao_substituir
            if self.imagem:
                imagem = self.imagem
                label_imagem.show()
                botao_substituir.setText("Substituir imagem")
                botao_excluir_img.show()
                label_imagem.setPixmap(WidgetHelper.imagem(imagem, pixmap=True))

            elif self.imagem == "":
                imagem = self.imagem
                label_imagem.clear()
                label_imagem.hide()
                botao_substituir.setText("Adicionar imagem")
                botao_excluir_img.hide()

        botao_confirmar.clicked.connect(lambda: self.handler.criar_loja(formulario, imagem))
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_criar_produto(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar"
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = WidgetHelper.label_span("Criar Produto", 50)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição"],
            largura=600,
            altura=50
        )
        layout_conteudo.addWidget(formulario)
        
        imagens = []
        layout_imagens = QVBoxLayout()
        layout_imagens.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addLayout(layout_imagens)

        def renderizar_imagens():
            nonlocal layout_imagens
            # Limpa o layout atual
            while layout_imagens.count():
                item = layout_imagens.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
                elif item.layout():
                    # Se o item for um layout (como QHBoxLayout), remova seus widgets também
                    sublayout = item.layout()
                    while sublayout.count():
                        subitem = sublayout.takeAt(0)
                        subwidget = subitem.widget()
                        if subwidget:
                            subwidget.setParent(None)

            # Recria as imagens com botões
            for img in imagens:
                layout_linha = QHBoxLayout()

                label_imagem = WidgetHelper.imagem(img)
                layout_linha.addWidget(label_imagem)

                botao_excluir = WidgetHelper.botao(
                    nome="Excluir imagem", fonte=10,
                    largura=100, altura=30,
                    acao=lambda _, img=img: (
                        self.excluir_imagem(img),
                        imagens.remove(img),
                        renderizar_imagens()
                    )
                )
                layout_linha.addWidget(botao_excluir)

                layout_imagens.addLayout(layout_linha)

            layout_imagens.addStretch()  # <- mover para dentro da função

        botao_confirmar.clicked.connect(lambda: self.handler.criar_produto(formulario, imagens, loja))

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        # Botão para adicionar nova imagem
        botao_adicionar = WidgetHelper.botao(
            nome="Adicionar imagem", largura=200,
            acao=lambda: (
                self.substituir_imagem(),
                imagens.append(self.imagem) if self.imagem else None,
                renderizar_imagens()
            )
        )
        layout_vertical.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela

    def tela_criar_anuncio(self, produto: Produto):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar"
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = WidgetHelper.label_span("Criar Anúncio", 50)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Preço", "Quantidade Disponível", "Chave Pix"],
            largura=600,
            altura=50
        )
        formularioOp = FormularioOpcoes(
            campos=["Pausado"],
            largura=600,
            altura=50
        )
        formularioOp.adicionar_opcao(campo="Pausado", opcao="Sim")
        formularioOp.adicionar_opcao(campo="Pausado", opcao="Não")
        botao_confirmar.clicked.connect(lambda: self.handler.criar_anuncio(formulario, formularioOp, produto))

        layout_form = QVBoxLayout()  # Lado a lado (horizontal)
        layout_form.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_form.addWidget(formulario, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_form.addWidget(formularioOp, alignment=Qt.AlignmentFlag.AlignRight)

        layout_conteudo.addLayout(layout_form)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    ###############  TELAS DE EDIÇÃO  ################
    def tela_editar_perfil(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(nome="Editar")
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = WidgetHelper.label_span("Meu Perfil", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "CPF", "Email", "Senha"],
            largura=600,
            altura=50
        )
        usuario = self.handler.aplicacao.usuario
        formulario.preencher_campos(
            {"Nome": usuario.nome, "CPF": usuario.cpf, "Email": usuario.email, "Senha": "*"*len(usuario.senha)}
        )
        botao_editar.clicked.connect(lambda: self.handler.editar_perfil(formulario))
        layout_conteudo.addWidget(formulario)
        layout_conteudo.addStretch()

        layout_horizontal_2 = QHBoxLayout()

        botao_endereco = WidgetHelper.botao(
            nome="Meus Endereços",
            largura=180,
            acao=lambda: self.handler.visualizar_meus_enderecos(self.tela_meus_enderecos)
        )
        layout_horizontal_2.addWidget(botao_endereco, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_excluir = WidgetHelper.botao(
            nome="Excluir Perfil",
            largura=160,
            acao=self.handler.excluir_usuario
        )
        layout_horizontal_2.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_logout = WidgetHelper.botao(
            nome="Logout",
            largura=100,
            acao=lambda: self.handler.logout()
        )
        layout_horizontal_2.addWidget(botao_logout, alignment=Qt.AlignmentFlag.AlignRight)

        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)
        layout_vertical.addLayout(layout_horizontal_2)

        return tela

    def tela_editar_endereco(self, endereco: Endereco):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(nome="Editar")
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = WidgetHelper.label_span("Endereço", 50)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Rua", "Número", "Bairro", "Cidade", "Estado", "Complemento"],
            largura=600,
            altura=50
        )
        formulario.preencher_campos(
            {
                "Rua": endereco.rua, "Número": endereco.numero, 
                "Bairro": endereco.bairro, "Cidade": endereco.cidade, 
                "Estado": endereco.estado, "Complemento": endereco.complemento
            }
        )
        botao_editar.clicked.connect(lambda: self.handler.editar_endereco(formulario, endereco))
        layout_conteudo.addWidget(formulario)
        layout_conteudo.addStretch()

        layout_horizontal_2 = QVBoxLayout()
        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=lambda: self.handler.excluir_endereco(endereco)
        )
        layout_horizontal_2.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_conteudo.addLayout(layout_horizontal_2)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def tela_editar_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(nome="Editar")
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = WidgetHelper.label_span("Editar Loja", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(campos=["Nome"], largura=600, altura=50)
        formulario.preencher_campos({"Nome": loja.nome})
        layout_conteudo.addWidget(formulario)

        layout_horizontal_2 = QHBoxLayout()
        layout_horizontal_2.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        if loja.imagem:
            label_imagem = WidgetHelper.imagem(loja.imagem)
            layout_horizontal_2.addWidget(label_imagem)
        else:
            label_imagem = QLabel()
            layout_horizontal_2.addWidget(label_imagem)

        botao_substituir = WidgetHelper.botao(
            nome=("Substituir imagem" if loja.imagem else "Adicionar imagem"),
            fonte=10, largura=100, altura=30,
            acao= lambda: (self.substituir_imagem(), atualiza_imagem())
        )
        layout_horizontal_2.addWidget(botao_substituir)

        botao_excluir_img = WidgetHelper.botao(
            nome="Excluir imagem", fonte=10,
            largura=100, altura=30,
            acao= lambda: (self.excluir_imagem(loja.imagem), atualiza_imagem())
        )
        layout_horizontal_2.addWidget(botao_excluir_img)
        botao_excluir_img.hide() if not loja.imagem else None

        layout_conteudo.addLayout(layout_horizontal_2)

        imagem = loja.imagem

        def atualiza_imagem():
            nonlocal imagem, label_imagem, botao_excluir_img, botao_substituir
            if self.imagem:
                imagem = self.imagem
                label_imagem.show()
                botao_substituir.setText("Substituir imagem")
                botao_excluir_img.show()
                label_imagem.setPixmap(WidgetHelper.imagem(imagem, pixmap=True))

            elif self.imagem == "":
                imagem = self.imagem
                label_imagem.clear()
                label_imagem.hide()
                botao_substituir.setText("Adicionar imagem")
                botao_excluir_img.hide()
        
        botao_editar.clicked.connect(lambda: self.handler.editar_loja(self.tela_editar_loja, formulario, loja, imagem))
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=lambda: self.handler.excluir_loja(loja)
        )
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela

    def tela_editar_produto(self, produto: Produto):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(nome="Editar")
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = WidgetHelper.label_span(produto.nome, 50)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos({"Nome": produto.nome, "Descrição": produto.descricao})

        botao_editar.clicked.connect(lambda: self.handler.editar_produto(self.tela_editar_produto, formulario, produto))
        layout_conteudo.addWidget(formulario)

        botao_imagens = WidgetHelper.botao(
            nome="Imagens",
            acao=lambda: self.view.abrir_tela(self.stack, lambda: self.tela_editar_imagens(produto))
        )
        layout_conteudo.addWidget(botao_imagens, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        layout_horizontal_2 = QHBoxLayout()

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=lambda: self.handler.excluir_produto(produto)
        )
        layout_horizontal_2.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_criar = WidgetHelper.botao(
            nome="Criar Anúncio", largura=200,
            acao=lambda: self.view.abrir_tela(self.stack, lambda: self.tela_criar_anuncio(produto))
        )
        layout_horizontal_2.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal_2)

        return tela
    
    def tela_editar_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(nome="Editar")
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = WidgetHelper.label_span(f"Anúncio: {anuncio.produto.nome}", 50)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Preço", "Quantidade Disponível", "Chave Pix"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos(
            {
                "Preço": anuncio.preco, "Quantidade Disponível": anuncio.quantidade_disponivel, 
                "Chave Pix": anuncio.chave_pix
            }
        )

        formularioOp = FormularioOpcoes(
            campos=["Pausado"],
            largura=600,
            altura=50
        )
        formularioOp.adicionar_opcao(campo="Pausado", opcao="Sim")
        formularioOp.adicionar_opcao(campo="Pausado", opcao="Não")
        formularioOp.preencher_campos({"Pausado": "Sim" if anuncio.pausado else "Não"})

        botao_editar.clicked.connect(lambda: self.handler.editar_anuncio(self.tela_editar_anuncio, formulario, formularioOp, anuncio))

        layout_form = QVBoxLayout()  # Lado a lado (horizontal)
        layout_form.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_form.addWidget(formulario, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_form.addWidget(formularioOp, alignment=Qt.AlignmentFlag.AlignRight)

        layout_conteudo.addLayout(layout_form)

        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=lambda: self.handler.excluir_anuncio(anuncio)
        )
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela
    
    def tela_editar_imagens(self, produto: Produto):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar
        layout_horizontal = QHBoxLayout()
        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        titulo = WidgetHelper.label_span("Editar Imagens", 50)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        imagens = produto.imagens
        layout_imagens = QVBoxLayout()
        layout_imagens.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addLayout(layout_imagens)

        for img in imagens:
            layout_linha = QHBoxLayout()

            label_imagem = WidgetHelper.imagem(img)
            layout_linha.addWidget(label_imagem)

            botao_excluir = WidgetHelper.botao(
                nome="Excluir imagem", fonte=10,
                largura=100, altura=30,
                acao=lambda _, img=img: (
                    self.excluir_imagem(img),
                    self.handler.excluir_imagem(produto, img) if self.imagem == "" else None
                )
            )
            layout_linha.addWidget(botao_excluir)

            layout_imagens.addLayout(layout_linha)

        layout_conteudo.addStretch()

        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        # Botão para adicionar nova imagem
        botao_adicionar = WidgetHelper.botao(
            nome="Adicionar imagem", largura=200,
            acao=lambda: (
                self.substituir_imagem(),
                self.handler.criar_imagem(produto, self.imagem) if self.imagem else None
            )
        )
        layout_vertical.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela

    ###############  TELAS DETALHES  #################
    def tela_detalhes_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_loja = WidgetHelper.botao(
            nome="Loja", fonte=15,
            largura=100,
            acao=lambda: self.handler.visualizar_loja(self.tela_detalhes_loja, anuncio.produto.loja)
        )
        layout_horizontal.addWidget(botao_loja, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal)

        carrossel = CarrosselImagem(anuncio.produto.imagens, largura=350, altura=350)
        layout_vertical.addWidget(carrossel, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = WidgetHelper.label_span(anuncio.produto.nome, 40)
        layout_vertical.addWidget(titulo)

        descricao = WidgetHelper.label_span(anuncio.produto.descricao, 30)
        descricao.setWordWrap(True)
        layout_vertical.addWidget(descricao)

        preco = WidgetHelper.label_preco(anuncio.preco, tamanho=50)
        layout_vertical.addWidget(preco)

        layout_horizontal_2 = QHBoxLayout()

        quantidade = WidgetHelper.label_span(f"Quantidade disponível: {anuncio.quantidade_disponivel}", 20)
        layout_horizontal_2.addWidget(quantidade, alignment=Qt.AlignmentFlag.AlignLeft)

        comprar = WidgetHelper.botao(
            nome="Comprar", fonte=30,
            largura=200, altura=50,
            acao=lambda: (self.handler.visualizar_meus_enderecos(lambda: self.tela_comprar(anuncio)) if self.handler.aplicacao.is_identificado() else self.view.abrir_tela(self.stack, lambda: self.tela_login()))
        )
        layout_horizontal_2.addWidget(comprar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal_2)

        return tela

    def tela_detalhes_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)

        if loja.imagem:
            imagem_label = WidgetHelper.imagem(loja.imagem)
            layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = WidgetHelper.label_span(loja.nome, 40)
        layout_vertical.addWidget(titulo)

        anuncios = self.tela_lista_anuncios(loja.anuncios)
        layout_vertical.addWidget(anuncios)

        return tela

    def tela_detalhes_minha_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar",
            acao=lambda: self.view.abrir_tela(self.stack, lambda: self.tela_editar_loja(loja))
        )
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        if loja.imagem:
            imagem_label = WidgetHelper.imagem(loja.imagem)
            layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = WidgetHelper.label_span(loja.nome, 40)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        layout_horizontal2 = QHBoxLayout()

        botao_anuncios = WidgetHelper.botao(
            nome="Anúncios", fonte=18,
        )
        layout_horizontal2.addWidget(botao_anuncios)

        botao_produtos = WidgetHelper.botao(
            nome="Produtos", fonte=18,
        )
        layout_horizontal2.addWidget(botao_produtos)

        botao_pedidos_confirmados = WidgetHelper.botao(
            nome="Pedidos Confirmados", fonte=18,
            largura=250,
        )
        layout_horizontal2.addWidget(botao_pedidos_confirmados)

        botao_pedidos_em_andamento = WidgetHelper.botao(
            nome="Pedidos Em Andamento", fonte=18,
            largura=230
        )
        layout_horizontal2.addWidget(botao_pedidos_em_andamento)

        anuncios = loja.anuncios
        produtos = loja.produtos
        pedidos_confirmados = loja.pedidos_confirmados
        pedidos_em_andamento = loja.pedidos_em_andamento

        if anuncios:
            lista_anuncios = self.tela_lista_anuncios_loja(anuncios, loja)
        else:
            lista_anuncios = WidgetHelper.label_b("Esta loja não possui anúncios.", 20, alignment=Qt.AlignmentFlag.AlignCenter)

        lista_produtos = self.tela_lista_produtos(loja, produtos, adicionar=True)

        if pedidos_confirmados:
            lista_pedidos_confirmados = self.tela_lista_pedidos(pedidos_confirmados, pedido_confirmado=True, botao_loja=False)
        else:
            lista_pedidos_confirmados = WidgetHelper.label_b("Esta loja não possui pedidos confirmados.", 20, alignment=Qt.AlignmentFlag.AlignCenter)

        if pedidos_em_andamento:
            lista_pedidos_em_andamento = self.tela_lista_pedidos(pedidos_em_andamento, pedido_confirmado=False, botao_confirmar=True, botao_loja=False)
        else:
            lista_pedidos_em_andamento = WidgetHelper.label_b("Esta loja não possui pedidos em andamento.", 20, alignment=Qt.AlignmentFlag.AlignCenter)

        # Container para trocar os conteúdos
        container_listas = QStackedWidget()
        container_listas.addWidget(lista_anuncios)
        container_listas.addWidget(lista_produtos)
        container_listas.addWidget(lista_pedidos_confirmados)
        container_listas.addWidget(lista_pedidos_em_andamento)

        botao_anuncios.clicked.connect(lambda: container_listas.setCurrentWidget(lista_anuncios))
        botao_produtos.clicked.connect(lambda: container_listas.setCurrentWidget(lista_produtos))
        botao_pedidos_confirmados.clicked.connect(lambda: container_listas.setCurrentWidget(lista_pedidos_confirmados))
        botao_pedidos_em_andamento.clicked.connect(lambda: container_listas.setCurrentWidget(lista_pedidos_em_andamento))

        layout_vertical.addLayout(layout_horizontal2)
        layout_vertical.addSpacing(10)
        layout_vertical.addWidget(container_listas)

        return tela
    
    def tela_detalhes_pedido(self, pedido: Pedido, adicionar_botao_confirmar = False, adicionar_botao_loja = True):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=lambda: self.view.voltar_tela(self.stack)
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        loja_existe = pedido.anuncio.produto.loja

        botao_loja = WidgetHelper.botao(
            nome="Loja", fonte=15,
            acao=lambda e: (
                self.handler.visualizar_loja(self.tela_detalhes_loja, loja_existe)
                if loja_existe
                else
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self,
                    backcolor="#FFC107", fontcolor="#000000",
                    posicao="superior_direita", largura=300,
                    mensagem="Loja excluída!"
                )
            )
        )
        if adicionar_botao_loja:
            layout_horizontal.addWidget(botao_loja, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal)

        titulo = WidgetHelper.label_span(pedido.anuncio.produto.nome, 40)
        layout_vertical.addWidget(titulo)

        carrossel = CarrosselImagem(pedido.anuncio.produto.imagens, largura=300, altura=300)
        layout_vertical.addWidget(carrossel, alignment=Qt.AlignmentFlag.AlignHCenter)

        descricao = WidgetHelper.label_span(pedido.anuncio.produto.descricao, 30)
        descricao.setWordWrap(True)
        layout_vertical.addWidget(descricao)

        preco_total = WidgetHelper.label_preco(f"{pedido.anuncio.preco * pedido.quantidade}",tamanho=35)
        layout_vertical.addWidget(preco_total)

        layout_horizontal_2 = QHBoxLayout()
        quantidade = WidgetHelper.label_span(f"Quantidade: {pedido.quantidade}", 30)
        layout_horizontal_2.addWidget(quantidade)

        preco = WidgetHelper.label_preco(f"{pedido.anuncio.preco:.2f}")
        layout_horizontal_2.addWidget(preco)
        layout_vertical.addLayout(layout_horizontal_2)

        data = WidgetHelper.label_span(f"Data: {pedido.data}", 25)
        layout_vertical.addWidget(data, alignment=Qt.AlignmentFlag.AlignHCenter)

        endereco = WidgetHelper.label_span(f"Endereço: {pedido.endereco.__str__()}", 25)
        layout_vertical.addWidget(endereco, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout_horizontal_3 = QHBoxLayout()

        botao_cancelar = WidgetHelper.botao(
            nome="Cancelar",
            acao=lambda: self.handler.cancelar_pedido(pedido)
        )

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar",
            acao=lambda: self.handler.confirmar_pedido(pedido)
        )

        if adicionar_botao_confirmar:
            layout_horizontal_3.addWidget(botao_cancelar, alignment=Qt.AlignmentFlag.AlignLeft)
            layout_horizontal_3.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addSpacing(10)
        layout_vertical.addLayout(layout_horizontal_3)

        return tela
    
    ############  TELAS LISTA  ##############
    def tela_lista_anuncios_gerais(self, anuncios, largura=250, altura=280):
        scroll, self.grid = WidgetHelper.lista_grid()

        for i, anuncio in enumerate(anuncios):
            bloco = self.bloco_anuncio(anuncio, largura, altura)
            self.grid.addWidget(bloco, i // 5, i % 5)
        return scroll

    def tela_lista_anuncios(self, anuncios, largura=250, altura=280):
        scroll, grid = WidgetHelper.lista_grid()

        for i, anuncio in enumerate(anuncios):
            bloco = self.bloco_anuncio(anuncio, largura, altura)
            grid.addWidget(bloco, i // 5, i % 5)

        return scroll
    
    def tela_lista_anuncios_loja(self, anuncios, loja: Loja, largura=250, altura=280):
        scroll, grid = WidgetHelper.lista_grid()

        for i, anuncio in enumerate(anuncios):
            bloco = self.bloco_anuncio_loja(anuncio, loja, largura, altura)
            if anuncio.pausado:
                efeito = QGraphicsOpacityEffect()
                efeito.setOpacity(0.4)  # valor entre 0 (transparente) e 1 (normal)
                bloco.setGraphicsEffect(efeito)
            grid.addWidget(bloco, i // 5, i % 5)

        return scroll
    
    def tela_lista_produtos(self, loja: Loja, produtos, adicionar=False, largura=250, altura=280):
        scroll, grid = WidgetHelper.lista_grid()

        botao_adicionar = WidgetHelper.botao(
            nome="+", fonte=80,
            largura=largura, altura=altura,
            backcolor='#e0f7fa', fontcolor='#0078d7',
            border='dashed #0078d7',
            hover='#b2ebf2', pressed='#80deea',
            acao=lambda: self.view.abrir_tela(self.stack, lambda: self.tela_criar_produto(loja))
        )

        index = 0
        # Adiciona o botão + primeiro, se existir
        if adicionar:
            grid.addWidget(botao_adicionar, 0, 0)
            index = 1

        for i, produto in enumerate(produtos):
            linha = (i + index) // 5
            coluna = (i + index) % 5
            bloco = self.bloco_produto(produto, loja, largura, altura)
            grid.addWidget(bloco, linha, coluna)

        return scroll
    
    def tela_lista_pedidos(self, pedidos, pedido_confirmado=True, botao_confirmar = False, botao_loja = True, largura=250, altura=250):
        scroll, grid = WidgetHelper.lista_grid()

        for i, pedido in enumerate(pedidos):
            bloco = self.bloco_pedido(pedido, largura, altura, pedido_confirmado, botao_confirmar, botao_loja)
            grid.addWidget(bloco, i // 5, i % 5)

        return scroll
    
    def tela_lista_lojas(self, lojas, largura=250, altura=250):
        scroll, grid = WidgetHelper.lista_grid()

        for i, loja in enumerate(lojas):
            bloco = self.bloco_loja(self.handler.aplicacao.usuario.lojas[i], largura, altura)
            grid.addWidget(bloco, i // 5, i % 5)

        return scroll
    
    ##########  PARTES DE TELAS  #############
    def menu_lateral(self):
        # Crie o menu lateral e esconda no início
        menu_lateral = QFrame()
        menu_lateral.setFrameShape(QFrame.Shape.StyledPanel)
        menu_lateral.setFixedWidth(250)
        menu_lateral.hide()

        # Layout para a barra lateral
        menu_layout = QVBoxLayout(menu_lateral)
        menu_layout.setSpacing(0)  # Definir o espaçamento entre os botões como 0
        menu_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens

        botao_perfil = WidgetHelper.botao(
            nome="Meu Perfil", fontcolor="gray",
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao= lambda: self.view.abrir_tela(self.stack, self.tela_editar_perfil)
        )

        botao_lojas = WidgetHelper.botao(
            nome="Minhas Lojas", fontcolor="gray",
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao=lambda: self.handler.visualizar_minhas_lojas(self.tela_minhas_lojas)
        )

        botao_pedidos = WidgetHelper.botao(
            nome="Meus Pedidos", fontcolor="gray",
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao= lambda: self.handler.visualizar_meus_pedidos(self.tela_meus_pedidos)
        )

        # Adicionando os botões ao layout da barra lateral
        menu_layout.addWidget(botao_perfil, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_lojas, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_pedidos, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addStretch()  # Adiciona um espaçador para empurrar os botões para cima

        return menu_lateral
    
    def barra_superior(self):
        # Barra superior com botões
        barra_superior = QHBoxLayout()

        botao_menu = WidgetHelper.botao(
            nome="≡", fonte=40,
            largura=50, altura=50,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000', fontcolor="gray",
            acao= self.toggle_menu
        )

        botao_login = WidgetHelper.botao(
            nome="Login", fonte=15,
            largura=100, altura=30,
            acao= lambda: self.view.abrir_tela(self.stack, self.tela_login)
        )

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Pesquisar produto...")
        self.input_busca.setFixedWidth(500)
        self.input_busca.setFixedHeight(40)
        self.input_busca.hide()

        self.botao_reset = WidgetHelper.botao(
            nome="❌", fonte=50,
            largura=50, altura=50,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000',
            acao= self.resetar_busca
        )
        self.botao_reset.hide()

        btn_pesquisa = WidgetHelper.botao(
            nome="🔍", fonte=40,
            largura=100, altura=50,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000',
            acao= self.mostrar_barra_pesquisa
        )

        btn_atualizar = WidgetHelper.botao(
            nome="⟲", fonte=40,
            largura=100, altura=50,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000', fontcolor="gray",
            acao= lambda: (self.handler.visualizar_anuncios(self.tela_inicial), self.atualizar_lista_anuncios(self.handler.aplicacao.anuncios))
        )

        if self.handler.aplicacao.is_identificado():
            barra_superior.addWidget(botao_menu)
        else:
            barra_superior.addWidget(botao_login)

        barra_superior.addWidget(QLabel("<h2>Produtos disponíveis:</h2>"), alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(self.botao_reset)
        barra_superior.addWidget(self.input_busca)
        barra_superior.addWidget(btn_pesquisa)
        barra_superior.addWidget(btn_atualizar)

        return barra_superior

class InterfaceHandler:
    def __init__(self, parent, stack):
        self.parent = parent
        self.stack = stack
        self.aplicacao = ClienteAplicacao(ip, porta)
        self.thread = Threads(stack)
        self.view = ViewHelper()

    def logout(self):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar logout",
            mensagem=f"Você tem certeza que deseja deslogar?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            self.aplicacao.logout()
            self.view.set_tela(self.stack, 0)
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent, 
                backcolor="#4CAF50",
                posicao="superior_direita",
                mensagem="Logout realizado com Sucesso!"
            )

        else:
            dialogo.close()

    def visualizar_anuncios(self, tela = None):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                self.aplicacao.anuncios = resposta[1]

            if tela:
                self.view.abrir_tela(self.stack, tela)
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=self.aplicacao.visualizar_anuncios,
            atualizar_tela=False, abrir_tela=tela, voltar_tela=tela
        ) 

    def visualizar_anuncio(self, tela, anuncio):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                anuncio = resposta[1]
                self.view.abrir_tela(self.stack, lambda: tela(anuncio))
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.visualizar_anuncio(anuncio),
            atualizar_tela=False
        ) 

    def visualizar_produto(self, tela, produto: Produto):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                produto = resposta[1]
                self.view.abrir_tela(self.stack, lambda: tela(produto))
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.visualizar_produto(produto),
            atualizar_tela=False
        ) 

    def visualizar_loja(self, tela, loja: Loja):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                loja = resposta[1]
                self.view.abrir_tela(self.stack, lambda: tela(loja))
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.visualizar_loja(loja),
            atualizar_tela=False
        ) 

    def visualizar_minha_loja(self, loja: Loja, tela):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                loja = resposta[1]
                self.view.abrir_tela(self.stack, lambda: tela(loja))
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.visualizar_minha_loja(loja),
            atualizar_tela=False
        ) 

    def visualizar_minhas_lojas(self, tela):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                self.aplicacao.usuario.lojas = resposta[1]
                self.view.abrir_tela(self.stack, tela)
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=self.aplicacao.visualizar_minhas_lojas,
            atualizar_tela=False
        ) 

    def visualizar_meus_pedidos(self, tela):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                self.aplicacao.usuario.pedidos_andamento = resposta[0]
                self.aplicacao.usuario.pedidos_confirmados = resposta[1]
                self.view.abrir_tela(self.stack, tela)
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=self.aplicacao.visualizar_meus_pedidos,
            atualizar_tela=False
        )

    def visualizar_pedido(self, tela, pedido: Pedido, pedido_confirmado, botao_confirmar, botao_loja):
        def ao_visualizar(resposta):
            nonlocal tela, botao_confirmar, botao_loja
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                pedido = resposta[1]
                self.view.abrir_tela(self.stack, lambda: tela(pedido, botao_confirmar, botao_loja))
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.visualizar_pedido(pedido, pedido_confirmado),
            atualizar_tela=False
        )
    
    def visualizar_meus_enderecos(self, tela):
        def ao_visualizar(resposta):
            nonlocal tela
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem=f"Erro ao visualizar!"
                )
            else:
                self.aplicacao.usuario.enderecos = resposta[1]
                self.view.abrir_tela(self.stack, tela)
        # Executa:
        self.thread.executar(
            acao=ao_visualizar,
            requisicao=self.aplicacao.visualizar_meus_enderecos,
            atualizar_tela=False
        )

    def confirmar_codigo(self, id_confirmacao, formulario: Formulario):
        erro = formulario.validar_tipos({"Código": int})
        if erro:
            formulario.exibir_erros()
            return

        valores = formulario.obter_valores()
        def ao_confirmar_codigo(resposta):
            if resposta[0]:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Cadastro realizado com Sucesso!"
                )
                self.aplicacao.usuario = Usuario_Identificado.from_dict(resposta[1])
                self.view.set_tela(self.stack, -4)

            elif resposta[1] == "codigo_invalido":
                formulario.definir_erros_especificos({"Código": "Código de confirmação inválido"})
                formulario.exibir_erros()

            elif resposta[1] == "limite_excedido":
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Limite de tentativas excedido!"
                )
                self.view.set_tela(self.stack, -2)

            elif resposta[1] == "tempo_excedido":
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Limite de tempo excedido!"
                )
                self.view.set_tela(self.stack, -2)

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao confirmar código!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.email_confirmacao(id_confirmacao, valores["Código"]),
            acao=ao_confirmar_codigo,
            atualizar_tela=False
        )

    def cadastrar(self, formulario: Formulario):
        erro = formulario.validar_tipos({"Nome": str, "CPF": str, "Email": str, "Senha": str})
        if erro:
            formulario.exibir_erros()
            return
        
        valores = formulario.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        usuario = Usuario_Identificado.from_dict(valores)
        def ao_cadastrar(resposta):
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao realizar cadastramento!"
                )

            elif isinstance(resposta, list):
                erros = {}
                if "cpf" in resposta:
                    erros["CPF"] = "CPF já cadastrado!"
                if "email" in resposta:
                    erros["Email"] = "Email já cadastrado!"
                if erros:
                    formulario.definir_erros_especificos(erros)
                    formulario.exibir_erros()

            elif resposta:
                self.view.abrir_tela(self.stack, lambda: self.parent.tela_codigo_confirmacao(resposta))

        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.cadastrar(usuario),
            acao=ao_cadastrar,
            atualizar_tela=False
        )

    def login(self, formulario: Formulario):
        erro = formulario.validar_tipos({"Email": str, "Senha": str})
        if erro:
            formulario.exibir_erros()
            return
        
        valores = formulario.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        usuario = Usuario_Identificado.from_dict(valores)
        def ao_login(resposta):
            if resposta[0]:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Login realizado com Sucesso!"
                )
                self.aplicacao.usuario = Usuario_Identificado.from_dict(resposta[1])
                self.view.set_tela(self.stack, -2)
            
            elif resposta[1] == "dados_incorretos":
                formulario.definir_erros_especificos({"Email": "Credenciais inválidas", "Senha": "Credenciais inválidas"})
                formulario.exibir_erros()

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao realizar login!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.login(usuario),
            acao=ao_login,
            atualizar_tela=False
        )

    def criar_pedido(self, pedido: Pedido, anuncio: Anuncio):   
        def ao_criar_pedido(resposta):
            nonlocal anuncio
            if resposta:
                anuncio.subtrair_quantidade(pedido.quantidade)
                if anuncio.quantidade_disponivel == 0:
                    self.aplicacao.apagar_anuncio(anuncio)
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Pedido Criado com Sucesso!"
                )
                self.aplicacao.usuario.criar_pedido(Pedido.from_dict(resposta[1]))
                self.view.set_tela(self.stack,-3)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar pedido!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.criar_pedido(pedido),
            acao=ao_criar_pedido
        )
    
    def criar_loja(self, formulario: Formulario, imagem):
        erro = formulario.validar_tipos({"Nome": str})
        if erro:
            formulario.exibir_erros()
            return
        
        valores = formulario.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        loja = Loja.from_dict(valores)  
        if imagem:
            loja.imagem = imagem

        def ao_criar_loja(resposta):
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Loja Criada com Sucesso!"
                )
                self.aplicacao.usuario.criar_loja(resposta[1])
                self.view.set_tela(self.stack,-2)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar loja!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.criar_loja(loja),
            acao=ao_criar_loja,
            atualizar_tela=False
        )          

    def criar_endereco(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Rua": str, "Número": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
            return
        
        valores = formulario.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        endereco = Endereco.from_dict(valores)
        def ao_criar_endereco(resposta):
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Endereço Criado com Sucesso!"
                )
                self.aplicacao.usuario.criar_endereco(Endereco.from_dict(resposta[1]))
                self.view.set_tela(self.stack, -2)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar endereço!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.criar_endereco(endereco),
            acao=ao_criar_endereco,
            atualizar_tela=False
        )

    def criar_produto(self, formulario: Formulario, imagens: list, loja: Loja):
        erro = formulario.validar_tipos({"Nome": str, "Descrição": str})
        if erro:
            formulario.exibir_erros()
            return
        elif not imagens:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="O produto não pode ficar sem imagem"
            )
            return
        
        valores = formulario.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        produto = Produto.from_dict(valores)
        produto.loja = loja  
        produto.imagens = imagens
        def ao_criar_produto(resposta):
            nonlocal loja
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Produto Criado com Sucesso!"
                )
                produto = resposta[1]
                loja.criar_produto(produto)
                self.view.set_tela(self.stack, -2)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar produto!"
                )

        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.criar_produto(produto),
            acao=ao_criar_produto,
            atualizar_tela=False
        )

    def criar_anuncio(self, formulario: Formulario, formularioOp: FormularioOpcoes, produto: Produto):
        erro = formulario.validar_tipos(
            {
                "Preço": float, "Preço": "positivo", 
                "Quantidade Disponível": int, "Quantidade Disponível": "positivo",
                "Chave Pix": str
            }
        )
        valores = formulario.obter_valores()
        valores = valores | formularioOp.obter_valores()
        valores = {Utils.normalizar_chave(k): v for k, v in valores.items()}
        valores["pausado"] = True if valores["pausado"] == "Sim" or not  valores["quantidade_disponivel"] else False

        if erro:
            formulario.exibir_erros()
            return

        elif not Utils.validar_chave_pix(valores["chave_pix"]):
            formulario.definir_erros_especificos({"Chave Pix": "Chave pix inválida!\nExemplo: (xx) xxxxx-xxxx, xxx.xxx.xxx-xx, xx.xxx.xxx/xxxx-xx, \nusuario@exemplo.com, ou chave aleatória"})
            formulario.exibir_erros()
            return

        anuncio = Anuncio.from_dict(valores)
        anuncio.produto = produto
        def ao_criar_anuncio(resposta):
            nonlocal anuncio
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    posicao="superior_direita",
                    mensagem="Anúncio Criado com Sucesso!"
                )
                anuncio = resposta[1]
                loja = self.aplicacao.usuario.get_loja(anuncio.produto.loja)
                loja.criar_anuncio(anuncio)
                self.view.set_tela(self.stack, -3)
                self.aplicacao.anuncios.append(anuncio)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar anúncio!"
                )
        # Executa:
        self.thread.executar(
            requisicao=lambda: self.aplicacao.criar_anuncio(anuncio),
            acao=ao_criar_anuncio,
            atualizar_tela=False
        )

    def criar_imagem(self, produto: Produto, imagem):
        def ao_criar_imagem(resposta):
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao criar imagem!"
                )
            else:
                produto.criar_imagem(resposta[1])
                self.view.atualiza_tela(self.stack)
        # Executa:
        self.thread.executar(
            acao=ao_criar_imagem,
            requisicao=lambda: self.aplicacao.criar_imagem(produto, imagem),
        )

    def editar_produto(self, tela, formulario: Formulario, produto: Produto):
        erro = formulario.validar_tipos({"Nome": str, "Descrição": str})
        if erro:
            formulario.exibir_erros()
            return
        
        valores_alterados = formulario.obter_valores_alterados({"Nome": produto.nome, "Descrição": produto.descricao})
        valores_alterados = {Utils.normalizar_chave(k): v for k, v in valores_alterados.items()}
        if valores_alterados:
            valores_alterados["id"] = produto.id
            def ao_editar_produto(resposta):
                nonlocal  tela, produto
                if resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=600,
                        mensagem="Você não pode editar um produto com pedidos pendentes!"
                    )
                elif resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Produto Editado com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(produto.loja)
                    produto = loja.editar_produto(produto, resposta[1])
                    loja.atualiza_anuncio(produto)
                    self.aplicacao.atualiza_anuncio_produto(produto)
                    self.view.abrir_tela(self.stack, lambda: tela(produto), excluir_anterior=True)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao editar produto!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.editar_produto(produto, valores_alterados),
                acao=ao_editar_produto,
                atualizar_tela=False
            )
            
        else:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Nenhuma alteração realizada"
            )

    def editar_loja(self, tela, formulario: Formulario, loja: Loja, imagem):
        erro = formulario.validar_tipos({ "Nome": str})

        if erro:
            formulario.exibir_erros()
            return
        
        valores_alterados = formulario.obter_valores_alterados({"Nome": loja.nome})
        if imagem != loja.imagem:
            valores_alterados['imagem'] = imagem

        if valores_alterados:
            valores_alterados["id"] = loja.id
            valores_alterados = {Utils.normalizar_chave(k): v for k, v in valores_alterados.items()}
            def ao_editar_loja(resposta):
                nonlocal loja, tela
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Loja Editada com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.editar_loja(loja, resposta[1])
                    self.view.abrir_tela(self.stack, lambda: tela(loja), excluir_anterior=True)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao editar loja!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.editar_loja(loja, valores_alterados),
                acao=ao_editar_loja,
                atualizar_tela=False
            )

        else:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Nenhuma alteração realizada"
            )

    def editar_endereco(self, formulario: Formulario, endereco: Endereco):
        erro = formulario.validar_tipos(
            {"Rua": str, "Número": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
            return
        
        valores_alterados = formulario.obter_valores_alterados(
            {
                "Rua": endereco.rua, "Número": endereco.numero,
                "Bairro": endereco.bairro, "Cidade": endereco.cidade, 
                "Estado": endereco.estado, "Complemento": endereco.complemento
            }
        )
        valores_alterados = {Utils.normalizar_chave(k): v for k, v in valores_alterados.items()}
        if valores_alterados:
            valores_alterados["id"] = endereco.id
            def ao_editar_endereco(resposta):
                nonlocal endereco
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Endereço Editado com Sucesso!"
                    )
                    self.aplicacao.usuario.editar_endereco(endereco, resposta[1])
                    self.view.atualiza_tela(self.stack)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao editar endereço!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.editar_endereco(endereco, valores_alterados),
                acao=ao_editar_endereco,
                atualizar_tela=False
            )

        else:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Nenhuma alteração realizada"
            )
    
    def editar_perfil(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Nome": str, "CPF": str, "Email": str, "Senha": str}
        )
        if erro:
            formulario.exibir_erros()
            return
        
        usuario = self.aplicacao.usuario
        valores_alterados = formulario.obter_valores_alterados(
            {"Nome": usuario.nome, "CPF": usuario.cpf, "Email": usuario.email, "Senha": "*"*len(usuario.senha)}
        )
        valores_alterados = {Utils.normalizar_chave(k): v for k, v in valores_alterados.items()}
        if valores_alterados:
            valores_alterados["id"] = usuario.id
            def ao_editar_perfil(resposta):
                if resposta[0]:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Perfil Editado com Sucesso!"
                    )
                    self.aplicacao.usuario = Usuario_Identificado.from_dict(resposta[1])
                    self.view.atualiza_tela(self.stack)

                elif resposta[1]:
                    erros = {}
                    if "cpf" in resposta[1]:
                        erros["CPF"] = "CPF já cadastrado!"
                    if "email" in resposta[1]:
                        erros["Email"] = "Email já cadastrado!"
                    if erros:
                        formulario.definir_erros_especificos(erros)
                        formulario.exibir_erros()

                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao editar perfil!"
                    )
                    self.view.atualiza_tela(self.stack)
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.editar_usuario(valores_alterados),
                acao=ao_editar_perfil,
                atualizar_tela=False
            )

        else:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Nenhuma alteração realizada"
            )
    
    def editar_anuncio(self, tela, formulario: Formulario, formularioOp: FormularioOpcoes, anuncio: Anuncio):
        erro = formulario.validar_tipos({
            "Preço": float,
            "Quantidade Disponível": int,
            "Chave Pix": str
        })

        if erro:
            formulario.exibir_erros()
            return

        valores_alterados = formulario.obter_valores_alterados({
            "Preço": anuncio.preco,
            "Quantidade Disponível": anuncio.quantidade_disponivel,
            "Chave Pix": anuncio.chave_pix
        })

        valores_alterados |= formularioOp.obter_valores_alterados({
            "Pausado": "Sim" if anuncio.pausado else "Não"
        })

        novo_pausado = valores_alterados.get("Pausado")
        nova_quantidade = int(valores_alterados.get("Quantidade Disponível", anuncio.quantidade_disponivel))

        if novo_pausado is not None:
            if novo_pausado == "Sim":
                valores_alterados["Pausado"] = True
            else:
                if nova_quantidade <= 0:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=680,
                        mensagem="Não é possível despausar um anúncio com quantidade indisponível!"
                    )
                    return
                valores_alterados["Pausado"] = False

        if nova_quantidade <= 0:
            valores_alterados["Pausado"] = True

        valores_alterados = {
            Utils.normalizar_chave(k): v
            for k, v in valores_alterados.items()
        }

        if valores_alterados:
            valores_alterados["id"] = anuncio.id
            def ao_editar_anuncio(resposta):
                nonlocal anuncio, tela
                if resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=600,
                        mensagem="Você não pode editar um anúncio com pedidos pendentes!"
                    )
                elif resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Anúncio Editado com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(anuncio.produto.loja)
                    anuncio = loja.editar_anuncio(anuncio, resposta[1])
                    self.view.abrir_tela(self.stack, lambda: tela(anuncio), excluir_anterior=True)
                    self.aplicacao.atualiza_anuncio(anuncio)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao editar anúncio!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.editar_anuncio(anuncio, valores_alterados),
                acao=ao_editar_anuncio,
                atualizar_tela=False
            )

        else:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent,
                backcolor="#FFC107", fontcolor="#000000",
                posicao="superior_direita",
                mensagem="Nenhuma alteração realizada"
            )

    def excluir_loja(self, loja: Loja):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar excluir loja",
            mensagem=f"Você tem certeza que deseja excluir loja {loja.nome}?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_loja(resposta):
                nonlocal loja
                if resposta is True:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Loja Excluída com Sucesso!"
                    )
                    for a in loja.anuncios:
                        self.aplicacao.apagar_anuncio(a)
                    self.aplicacao.usuario.apagar_loja(loja)
                    self.view.set_tela(self.stack, -3)
                elif resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=600,
                        mensagem="Você não pode excluir uma loja com pedidos pendentes!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao excluir loja!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.excluir_loja(loja),
                acao=ao_excluir_loja,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def excluir_produto(self, produto: Produto):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar excluir produto",
            mensagem=f"Você tem certeza que deseja excluir produto {produto.nome}?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_produto(resposta):
                nonlocal produto
                if resposta is True:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Produto Excluído com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(produto.loja)
                    loja.apagar_produto(produto)
                    self.aplicacao.apagar_anuncios(produto)
                    self.view.set_tela(self.stack, -2)
                elif resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=600,
                        mensagem="Você não pode excluir um produto com pedidos pendentes!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao excluir produto!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.excluir_produto(produto),
                acao=ao_excluir_produto,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def excluir_anuncio(self, anuncio: Anuncio):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar excluir anúncio",
            mensagem=f"Você tem certeza que deseja excluir esse anúncio?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_anuncio(resposta):
                nonlocal anuncio
                if resposta is True:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Anúncio Excluído com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(anuncio.produto.loja)
                    loja.apagar_anuncio(anuncio)
                    self.aplicacao.apagar_anuncio(anuncio)
                    self.view.set_tela(self.stack, -2)
                elif resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=600,
                        mensagem="Você não pode excluir um anúncio com pedidos pendentes!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao excluir anúncio!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.excluir_anuncio(anuncio),
                acao=ao_excluir_anuncio,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def excluir_endereco(self, endereco: Endereco):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar excluir endereço",
            mensagem=f"Você tem certeza que deseja excluir esse endereço?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_endereco(resposta):
                nonlocal endereco
                if resposta is True:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Endereço Excluído com Sucesso!"
                    )
                    self.aplicacao.usuario.apagar_endereco(endereco)
                    self.view.set_tela(self.stack, -2)
                elif resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=610,
                        mensagem="Você não pode excluir um endereço com pedidos pendentes!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao excluir endereço!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.excluir_endereco(endereco),
                acao=ao_excluir_endereco,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def excluir_imagem(self, produto: Produto, imagem):
        def ao_excluir_imagem(resposta):
            nonlocal produto, imagem
            if not resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#f44336",
                    posicao="superior_direita",
                    mensagem="Erro ao excluir imagem!"
                )
            else:
                produto.apagar_imagem(imagem)
                self.view.atualiza_tela(self.stack)
        if len(produto.imagens) == 1:
            WidgetHelper.mostrar_alerta_temporario(
                parent_widget=self.parent, fontcolor="#000000",
                backcolor="#FFC107",
                posicao="superior_direita",
                mensagem="O produto não pode ficar sem imagem"
            )
        else:
            # Executa:
            self.thread.executar(
                acao=ao_excluir_imagem,
                requisicao=lambda: self.aplicacao.excluir_imagem(imagem),
            )

    def excluir_usuario(self):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar excluir perfil",
            mensagem=f"Você tem certeza que deseja seu perfil?",
            largura=450
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_usuario(resposta):
                if resposta is True:
                    self.aplicacao.usuario = Usuario()
                    self.view.set_tela(self.stack, -2)
                    self.visualizar_anuncios(self.parent.tela_inicial)
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Perfil Excluído com Sucesso!"
                    )

                elif resposta == "pedidos_pendentes":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#FFC107", fontcolor="#000000",
                        posicao="superior_direita", largura=650,
                        mensagem="Você não pode excluir um perfil com lojas ou pedidos pendentes!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao excluir perfil!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=self.aplicacao.excluir_usuario,
                acao=ao_excluir_usuario,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def cancelar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar cancelamento", 
            mensagem=f"Você tem certeza que deseja cancelar pedido {pedido.id}?",
            largura=500
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_cancelar_pedido(resposta):
                nonlocal pedido
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Pedido Cancelado com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(pedido.anuncio.produto.loja)
                    loja.cancelar_pedido(pedido)
                    self.view.set_tela(self.stack, -2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao cancelar pedido!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.cancelar_pedido(pedido),
                acao=ao_cancelar_pedido,
                atualizar_tela=False
            )

        else:
            dialogo.close()

    def confirmar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(
            self.parent, titulo="Confirmar", 
            mensagem=f"Você tem certeza que deseja confirmar pedido {pedido.id}?",
            largura=500
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_confirmar_pedido(resposta):
                nonlocal pedido
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        posicao="superior_direita",
                        mensagem="Pedido Confirmado com Sucesso!"
                    )
                    loja = self.aplicacao.usuario.get_loja(pedido.anuncio.produto.loja)
                    loja.confirmar_pedido(pedido)
                    self.view.set_tela(self.stack, -2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        posicao="superior_direita",
                        mensagem="Erro ao confirmar pedido!"
                    )
            # Executa:
            self.thread.executar(
                requisicao=lambda: self.aplicacao.confirmar_pedido(pedido),
                acao=ao_confirmar_pedido,
                atualizar_tela=False
            )

        else:
            dialogo.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        porta = int(sys.argv[2])

    app = QApplication(sys.argv)
    window = MarketplaceUI()
    window.show()
    sys.exit(app.exec())
