import sys, os, shutil
# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.loja import Loja
from models.anuncio import Anuncio
from models.produto import Produto
from models.usuario import Usuario_Identificado
from models.validation_utils import ValidationUtils as vu
from models.cliente import UnixSocketClient
from models.endereco import Endereco
from forms import Formulario, FormularioOpcoes
from models.pedido import Pedido

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import (
   QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QFileDialog,QFormLayout, QSpacerItem, QSizePolicy,
   QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QFrame, QStackedWidget, QPushButton, QComboBox
)

class CarrosselImagem(QWidget):
    def __init__(self, lista_caminhos_imagem, largura=200, altura=200):
        super().__init__()
        self.imagens = lista_caminhos_imagem
        self.index = 0
        self.largura = largura
        self.altura = altura

        # Imagem
        self.label_imagem = QLabel()
        self.label_imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_imagem.setFixedSize(self.largura, self.altura)

        # Botões
        self.btn_anterior = QPushButton("◀")
        self.btn_anterior.clicked.connect(self.imagem_anterior)
        self.btn_proximo = QPushButton("▶")
        self.btn_proximo.clicked.connect(self.imagem_proxima)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.btn_anterior, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.label_imagem, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_proximo, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

        self.setFixedWidth(self.largura + 100)  # 40 px para cada botão
        self.setFixedHeight(self.altura)
        layout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetFixedSize)

        # Mostrar a primeira imagem
        self.mostrar_imagem()

    def mostrar_imagem(self):
        if not self.imagens:
            return
        
        pixmap = QPixmap(self.imagens[self.index])
        pixmap = pixmap.scaled(
            self.largura, self.altura,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label_imagem.setPixmap(pixmap)

        # Ativa ou desativa os botões
        if len(self.imagens) <= 1:
            self.btn_anterior.setEnabled(False)
            self.btn_proximo.setEnabled(False)
        else:
            self.btn_anterior.setEnabled(self.index > 0)
            self.btn_proximo.setEnabled(self.index < len(self.imagens) - 1)

    def imagem_anterior(self):
        self.index = (self.index - 1) % len(self.imagens)
        self.mostrar_imagem()

    def imagem_proxima(self):
        self.index = (self.index + 1) % len(self.imagens)
        self.mostrar_imagem()

class MarketplaceUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caldeirão")
        self.setGeometry(100, 100, 1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.menu_lateral = self.criar_menu_lateral()
        self.barra_superior = self.criar_barra_superior()

        self.anuncios = self.criar_lista_anuncios()
        self.tela_lista = self.tela_lista_anuncios(self.anuncios)

        self.tela_inicial = self.tela_inicial()

        self.stack.addWidget(self.tela_inicial)

    def copiar_texto(self, label):
            clipboard = QApplication.clipboard()
            texto_sem_html = label.text()  # Isso ainda está com HTML
            # Se quiser extrair só o texto puro:
            from PyQt6.QtGui import QTextDocument
            doc = QTextDocument()
            doc.setHtml(texto_sem_html)
            texto_puro = doc.toPlainText()

            clipboard.setText(texto_puro)

    def botao_voltar(self):
        voltar = QPushButton("Voltar")
        voltar.setFixedSize(110, 30)
        voltar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        voltar.clicked.connect(self.voltar_para_lista)

        return voltar
    
    def botao(self, nome, fonte, acao = None):
        botao = QPushButton(nome)
        botao.setFixedSize(110, 30)
        botao.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        if acao:
            botao.clicked.connect(acao)

        return botao
    
    def botao_confirmar(self, acao = None):
        botao_confirmar = QPushButton("Confirmar")
        botao_confirmar.setFixedSize(110, 30)
        botao_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        if acao:
            botao_confirmar.clicked.connect(acao)

        return botao_confirmar
    
    def botao_adicionar(self, acao = None):
        botao_adicionar = QPushButton("Adicionar")
        botao_adicionar.setFixedSize(110, 30)
        botao_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        if acao:
            botao_adicionar.clicked.connect(acao)
        return botao_adicionar
    
    def botao_excluir(self, acao = None):
        botao_excluir = QPushButton("Excluir")
        botao_excluir.setFixedSize(110, 30)
        botao_excluir.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        if acao:
            botao_excluir.clicked.connect(acao)
        return botao_excluir

    def botao_editar(self, acao = None):
        botao_editar = QPushButton("Editar")
        botao_editar.setFixedSize(110, 30)
        botao_editar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        if acao:
            botao_editar.clicked.connect(acao)
        return botao_editar
    
    def abrir_dialogo_arquivo(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Escolher arquivo",
            "",
            "Todos os arquivos (*.*);;Imagens (*.png *.jpg *.jpeg);;Textos (*.txt)"
        )
        if caminho_arquivo:
            # Caminho de destino onde o arquivo será salvo (pode mudar para o que quiser)
            nome_arquivo = os.path.basename(caminho_arquivo)
            destino = os.path.join("uploads", nome_arquivo)

            # Cria a pasta "uploads" se ela não existir
            os.makedirs("uploads", exist_ok=True)

            # Copia o arquivo para a pasta destino
            shutil.copy(caminho_arquivo, destino)

    def abrir_tela(self, nova_tela):
        self.stack.addWidget(nova_tela)
        self.stack.setCurrentWidget(nova_tela)

    def voltar_para_lista(self):
        self.stack.setCurrentWidget(self.tela_inicial)
        self.atualizar_lista_anuncios(self.anuncios)

    def toggle_menu(self):
        if self.menu_lateral.isVisible():
            self.menu_lateral.hide()
        else:
            self.menu_lateral.show()

    def mostrar_barra_pesquisa(self):
        self.input_busca.show()
        self.botao_reset.show()
        self.input_busca.setFocus()
        self.input_busca.textChanged.connect(self.aplicar_filtro)

    def aplicar_filtro(self, texto):
        texto = texto.lower().strip()
        anuncios_filtrados = [
            a for a in self.anuncios if texto in a.produto.nome.lower()
        ]
        self.atualizar_lista_anuncios(anuncios_filtrados)

    def resetar_busca(self):
        self.input_busca.clear()
        self.input_busca.hide()
        self.botao_reset.hide()
        self.atualizar_lista_anuncios(self.anuncios)

    def atualizar_lista_anuncios(self, nova_lista):
        # Remove widgets antigos
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        largura_bloco = 250
        altura_bloco = 300
        lista = []

        for anuncio in nova_lista:
            if not anuncio.pausado:
                lista.append(anuncio)

        for i, anuncio in enumerate(lista):
            bloco = self.criar_bloco_anuncio(anuncio, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)
    
    def comprar(self, anuncio: Anuncio, formularioOp: FormularioOpcoes):
        anuncio.subtrair_quantidade(1)
        self.abrir_tela(self.tela_pagamento(anuncio))

    def criar_menu_lateral(self):
        # Crie o menu lateral e esconda no início
        menu_lateral = QFrame()
        menu_lateral.setFrameShape(QFrame.Shape.StyledPanel)
        menu_lateral.setFixedWidth(250)
        menu_lateral.hide()

        # Layout para a barra lateral
        menu_layout = QVBoxLayout(menu_lateral)
        menu_layout.setSpacing(0)  # Definir o espaçamento entre os botões como 0
        menu_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens

        # Exemplo de adição de botões à barra lateral
        botao_perfil = QPushButton("Meu Perfil")
        botao_perfil.setFixedSize(250, 100)  # Tamanho fixo do botão
        botao_perfil.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 25px;
                margin: 20;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        botao_perfil.clicked.connect(lambda: self.abrir_tela(self.tela_perfil()))

        botao_lojas = QPushButton("Minhas lojas")
        botao_lojas.setFixedSize(250, 100)  # Tamanho fixo do botão
        botao_lojas.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 25px;
                margin: 20;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        botao_lojas.clicked.connect(lambda: self.abrir_tela(self.tela_minhas_lojas()))

        botao_pedidos = QPushButton("Meus Pedidos")
        botao_pedidos.setFixedSize(250, 100)  # Tamanho fixo do botão
        botao_pedidos.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 25px;
                margin: 20;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        botao_pedidos.clicked.connect(lambda: self.abrir_tela(self.tela_meus_pedidos()))

        # Adicionando os botões ao layout da barra lateral
        menu_layout.addWidget(botao_perfil, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_lojas, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_pedidos, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addStretch()  # Adiciona um espaçador para empurrar os botões para cima

        return menu_lateral
    
    def criar_barra_superior(self):
        # Barra superior com botões
        barra_superior = QHBoxLayout()

        botao_menu = QPushButton("≡")
        botao_menu.setFixedSize(50, 50)
        botao_menu.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 40px;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        botao_menu.clicked.connect(self.toggle_menu)

        botao_login = QPushButton("Login")
        botao_login.setFixedSize(100, 30)
        botao_login.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)   
        botao_login.clicked.connect(lambda: self.abrir_tela(self.tela_login()))

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Pesquisar produto...")
        self.input_busca.setFixedWidth(500)
        self.input_busca.setFixedHeight(40)
        self.input_busca.hide()

        self.botao_reset = QPushButton("❌")
        self.botao_reset.setFixedSize(50, 50)
        self.botao_reset.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        self.botao_reset.hide()
        self.botao_reset.clicked.connect(self.resetar_busca)

        btn_pesquisa = QPushButton("🔍")
        btn_pesquisa.setFixedSize(100, 50)
        btn_pesquisa.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 40px;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)
        btn_pesquisa.clicked.connect(self.mostrar_barra_pesquisa)

        botao_selecionar_arquivo = QPushButton("Selecionar Arquivo")
        botao_selecionar_arquivo.clicked.connect(self.abrir_dialogo_arquivo)
        btn_pesquisa.setFixedSize(100, 50)
        btn_pesquisa.setStyleSheet("""
            QPushButton {
                border: 2px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 40px;
            }
            QPushButton:hover {
                background-color: #D3D3D3;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """)

        if True:
            barra_superior.addWidget(botao_menu)
        else:
            barra_superior.addWidget(botao_login)

        barra_superior.addWidget(QLabel("<h2>Produtos disponíveis:</h2>"), alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(botao_selecionar_arquivo, alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(self.botao_reset)
        barra_superior.addWidget(self.input_busca)
        barra_superior.addWidget(btn_pesquisa)

        return barra_superior

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

    def criar_bloco_anuncio(self, anuncio: Anuncio, largura, altura, editar = False):
        bloco = QFrame()
        bloco.setFixedSize(QSize(largura, altura))
        bloco.setFrameShape(QFrame.Shape.StyledPanel)
        bloco.setStyleSheet("""
            QFrame {
                border: 1px;
                border-radius: 8px;
                background-color: #fff;
                color: #000;
                font-size: 20px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        imagem_label = QLabel()
        pixmap = QPixmap(anuncio.produto.imagens[0]).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(f"<b>{anuncio.produto.nome}</b>")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preco_label = QLabel(f"R$ {anuncio.preco:.2f}")
        preco_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(imagem_label)
        layout.addSpacing(5)
        layout.addWidget(nome_label)
        layout.addWidget(preco_label)

        bloco.mousePressEvent = lambda e: self.abrir_tela( self.tela_anuncio(anuncio) if editar else self.tela_detalhes_anuncio(anuncio))
        return bloco
    
    def criar_bloco_produto(self, produto: Produto, largura, altura):
        bloco = QFrame()
        bloco.setFixedSize(QSize(largura, altura))
        bloco.setFrameShape(QFrame.Shape.StyledPanel)
        bloco.setStyleSheet("""
            QFrame {
                border: 1px;
                border-radius: 8px;
                background-color: #fff;
                color: #000;
                font-size: 20px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        imagem_label = QLabel()
        pixmap = QPixmap(produto.imagens[0]).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        nome_label = QLabel(f"<b>{produto.nome}</b>")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(imagem_label)
        layout.addSpacing(5)
        layout.addWidget(nome_label)

        bloco.mousePressEvent = lambda e: self.abrir_tela(self.tela_produto(produto))
        return bloco
    
    def criar_bloco_pedido(self, pedido: Pedido, largura, altura, confirmar):
        bloco = QFrame()
        bloco.setFixedSize(QSize(largura, altura))
        bloco.setFrameShape(QFrame.Shape.StyledPanel)
        bloco.setStyleSheet("""
            QFrame {
                border: 1px;
                border-radius: 8px;
                background-color: #fff;
                color: #000;
                font-size: 20px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        data_label = QLabel(f"<b>{pedido.data.strftime('%d/%m/%Y - %H:%M')}</b>")
        data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(data_label)
        layout.addSpacing(5)

        nome_label = QLabel(f"<b>{pedido.produto.nome}</b>")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(nome_label)
        layout.addSpacing(5)

        qnt_label = QLabel(f"<b>{pedido.quantidade}</b>")
        qnt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qnt_label)
        layout.addSpacing(5)

        preco_label = QLabel(f"<span style='font-size: 30px; color: green'>R$ {pedido.quantidade * pedido.preco}</span>")
        preco_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preco_label)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.abrir_tela(self.tela_detalhes_pedido(pedido, confirmar))
        return bloco
    
    def criar_bloco_loja(self, loja: Loja, largura, altura):
        bloco = QFrame()
        bloco.setFixedSize(QSize(largura, altura))
        bloco.setFrameShape(QFrame.Shape.StyledPanel)
        bloco.setStyleSheet("""
            QFrame {
                border: 1px;
                border-radius: 8px;
                background-color: #fff;
                color: #000;
                font-size: 20px;
            }
            QFrame:hover {
                background-color: #f0f0f0;
            }
        """)

        layout = QVBoxLayout(bloco)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        imagem_label = QLabel()
        pixmap = QPixmap(loja.imagem).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(imagem_label)

        nome_label = QLabel(f"<b>{loja.nome}</b>")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(nome_label)
        layout.addSpacing(5)

        bloco.mousePressEvent = lambda e: self.abrir_tela(self.tela_minha_loja(loja))
        return bloco
    
    def tela_lista_anuncios(self, anuncios, editar = False):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        vbox = QVBoxLayout(conteudo)

        self.grid = QGridLayout()
        vbox.addLayout(self.grid)  # adiciona o grid ao layout vertical
        vbox.addStretch()  # empurra tudo para cima

        largura_bloco = 250
        altura_bloco = 300
        for i, anuncio in enumerate(anuncios):
            bloco = self.criar_bloco_anuncio(anuncio, largura_bloco, altura_bloco, editar)
            self.grid.addWidget(bloco, i // 5, i % 5)

        scroll.setWidget(conteudo)
        return scroll
    
    def tela_lista_produtos(self, produtos, adicionar=False):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        vbox = QVBoxLayout(conteudo)

        grid = QGridLayout()
        vbox.addLayout(grid)
        vbox.addStretch()

        largura_bloco = 250
        altura_bloco = 300

        index = 0

        botao_adicionar = QPushButton("+")
        botao_adicionar.setFixedSize(largura_bloco, altura_bloco)
        botao_adicionar.setStyleSheet("""
            QPushButton {
                background-color: #e0f7fa;
                border: 2px dashed #0078d7;
                border-radius: 15px;
                font-size: 80px;
                font-weight: bold;
                color: #0078d7;
            }
            QPushButton:hover {
                background-color: #b2ebf2;
            }
            QPushButton:pressed {
                background-color: #80deea;
            }
        """)
        botao_adicionar.clicked.connect(lambda: self.abrir_tela(self.tela_criar_produto()))

        # Adiciona o botão + primeiro, se existir
        if adicionar:
            grid.addWidget(botao_adicionar, 0, 0)
            index = 1

        for i, produto in enumerate(produtos):
            linha = (i + index) // 5
            coluna = (i + index) % 5
            bloco = self.criar_bloco_produto(produto, largura_bloco, altura_bloco)
            grid.addWidget(bloco, linha, coluna)

        scroll.setWidget(conteudo)
        return scroll
    
    def tela_lista_pedidos(self, pedidos, confirmar = False):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        vbox = QVBoxLayout(conteudo)

        self.grid = QGridLayout()
        vbox.addLayout(self.grid)  # adiciona o grid ao layout vertical
        vbox.addStretch()  # empurra tudo para cima

        largura_bloco = 250
        altura_bloco = 220
        for i, pedido in enumerate(pedidos):
            bloco = self.criar_bloco_pedido(pedido, largura_bloco, altura_bloco, confirmar)
            self.grid.addWidget(bloco, i // 5, i % 5)

        scroll.setWidget(conteudo)
        return scroll
    
    def tela_lista_lojas(self, lojas):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        vbox = QVBoxLayout(conteudo)

        self.grid = QGridLayout()
        vbox.addLayout(self.grid)  # adiciona o grid ao layout vertical
        vbox.addStretch()  # empurra tudo para cima

        largura_bloco = 250
        altura_bloco = 220
        for i, loja in enumerate(lojas):
            bloco = self.criar_bloco_loja(loja, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)

        scroll.setWidget(conteudo)
        return scroll
    
    def tela_inicial(self):
        tela = QWidget()

        # Layout horizontal principal (menu + conteúdo)
        layout_h = QHBoxLayout(tela)

        # Adiciona a barra lateral ao layout principal (inicialmente oculta)
        layout_h.addWidget(self.menu_lateral)
        
        # Layout vertical para o conteúdo da tela
        layout_conteudo = QVBoxLayout()

        layout_conteudo.addLayout(self.barra_superior)

        layout_conteudo.addWidget(self.tela_lista)

        # Agora adiciona o conteúdo principal no layout horizontal
        layout_h.addLayout(layout_conteudo)

        return tela

    def tela_detalhes_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        loja = QPushButton("Loja")
        loja.setFixedSize(100, 30)
        loja.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        loja.clicked.connect(lambda: self.abrir_tela(self.tela_detalhes_loja(anuncio.produto.loja)))
        layout_horizontal.addWidget(loja, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal)

        carrossel = CarrosselImagem(anuncio.produto.imagens, largura=350, altura=350)
        layout_vertical.addWidget(carrossel, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel(f"<span style='font-size: 40px; font-weight: bold'>{anuncio.produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)

        descricao = QLabel(f"<span style='font-size: 20px'>{anuncio.produto.descricao}</span>")
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(descricao)

        preco = QLabel(f"<span style='font-size: 30px; color: green'>R$ {anuncio.preco:.2f}</span>")
        preco.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(preco)

        layout_horizontal_2 = QHBoxLayout()

        quantidade = QLabel(f"<span style='font-size: 20px'>Quantidade disponível: {anuncio.quantidade_disponivel}</span>")
        layout_horizontal_2.addWidget(quantidade, alignment=Qt.AlignmentFlag.AlignLeft)

        comprar = QPushButton("Comprar")
        comprar.setFixedSize(200, 50)
        comprar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        
        comprar.clicked.connect(lambda: self.abrir_tela(self.tela_comprar(anuncio)))
        layout_horizontal_2.addWidget(comprar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal_2)

        return tela

    def tela_detalhes_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)

        imagem_label = QLabel()
        pixmap = QPixmap(loja.imagem).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel(f"<span style='font-size: 40px; font-weight: bold'>{loja.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)

        anuncios = self.tela_lista_anuncios(loja.anuncios)
        self.atualizar_lista_anuncios(loja.anuncios)
        layout_vertical.addWidget(anuncios)

        return tela
    
    def tela_detalhes_pedido(self, pedido: Pedido, confirmar = False):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        loja = QPushButton(f"Loja")
        loja.setFixedSize(100, 30)
        loja.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        loja.clicked.connect(lambda: self.abrir_tela(self.tela_detalhes_loja(pedido.produto.loja)))
        layout_horizontal.addWidget(loja, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        titulo = QLabel(f"<span style='font-size: 40px; font-weight: bold'>{pedido.produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(titulo)

        carrossel = CarrosselImagem(pedido.produto.imagens, largura=300, altura=300)
        layout_vertical.addWidget(carrossel, alignment=Qt.AlignmentFlag.AlignHCenter)

        descricao = QLabel(f"<span style='font-size: 30px'>{pedido.produto.descricao}</span>")
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(descricao)

        preco_total = QLabel(f"<span style='font-size: 35px; color: green'>R${pedido.preco * pedido.quantidade}</span>")
        preco_total.setWordWrap(True)
        preco_total.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(preco_total)

        layout_horizontal_2 = QHBoxLayout()
        quantidade = QLabel(f"<span style='font-size: 30px'>Quantidade: {pedido.quantidade}</span>")
        quantidade.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_horizontal_2.addWidget(quantidade)

        preco = QLabel(f"<span style='font-size: 30px; color: green'>R$ {pedido.preco:.2f}</span>")
        preco.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_horizontal_2.addWidget(preco)
        layout_vertical.addLayout(layout_horizontal_2)

        layout_horizontal_3 = QHBoxLayout()

        endereco = QLabel(f"<span style='font-size: 25px;n'>Endereço: {pedido.endereco.__str__()}</span>")
        endereco.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_horizontal_3.addWidget(endereco)

        data = QLabel(f"<span style='font-size: 25px;'>Data: {pedido.data.strftime('%d/%m/%Y - %H:%M')}</span>")
        data.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_horizontal_3.addWidget(data)

        layout_vertical.addLayout(layout_horizontal_3)

        layout_horizontal_4 = QHBoxLayout()

        botao_cancelar = QPushButton(f"Cancelar")
        botao_cancelar.setFixedSize(100, 30)
        botao_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        #botao_cancelar.clicked.connect(lambda: self.abrir_tela(self.tela_detalhes_loja(pedido.produto.loja)))

        botao_confirmar = self.botao_confirmar()

        if confirmar:
            layout_horizontal_4.addWidget(botao_cancelar, alignment=Qt.AlignmentFlag.AlignLeft)
            layout_horizontal_4.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addSpacing(10)
        layout_vertical.addLayout(layout_horizontal_4)

        return tela

    def tela_comprar(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Comprar</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = FormularioOpcoes(campos=["Quantidade", "Endereço"],largura=600, altura=50)
        end = Endereco(rua="Aristides Teixeira Duarte", numero=234, bairro="California", cidade="Florestal", estado="MG", complemento="Apartamento 205")
        formulario.adicionar_opcao(campo="Endereço", opcao=end.__str__())
        end = Endereco(rua="São José", numero=92, bairro="Saõ Jośe do Triunfo", cidade="Viçosa", estado="MG", complemento="Casa")
        formulario.adicionar_opcao(campo="Endereço", opcao=end.__str__())
        formulario.ativar_botao_adicionar(campo="Endereço", acao=formulario.adicionar_opcao(campo="Endereço"))
        for i in range(anuncio.quantidade_disponivel):
            formulario.adicionar_opcao(campo="Quantidade", opcao=str(i+1))

        #layout_vertical.addWidget(formulario1, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(formulario, alignment=Qt.AlignmentFlag.AlignHCenter)

        botao_confirmar = QPushButton("Confirmar")
        botao_confirmar.setFixedSize(200, 50)
        botao_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        botao_confirmar.clicked.connect(lambda: self.comprar(anuncio, formulario))
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela
    
    def tela_pagamento(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)
        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)
        layout_vertical.addSpacing(10)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Pagamento</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(20)

        dados = vu.gerar_qrcode_pix(
            nome="Leticia",
            chave="136.689.956-30",
            cidade="São Paulo",
            valor=12.50,
            descricao="Pagamento do almoço",
            pagamento_multiplo=False,
            nome_arquivo="qrcode",
            salvar_png = True,
            salvar_svg = False
        )

        imagem_label = QLabel()
        pixmap = QPixmap("qrcode").scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addSpacing(10)

        string = QLabel(f"<span style='font-size: 12px; font-weight: 950'>{dados['payload']}</span>")
        string.setAlignment(Qt.AlignmentFlag.AlignCenter)
        string.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        string.setWordWrap(True)
        string.setMaximumWidth(500)
        layout_vertical.addWidget(string, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_copiar = QPushButton("Copiar texto")
        botao_copiar.clicked.connect(lambda: self.copiar_texto(string))
        layout_vertical.addWidget(botao_copiar, alignment=Qt.AlignmentFlag.AlignCenter)

        layout_vertical.addSpacing(10)

        botao_confirmar = QPushButton("Confirmar")
        botao_confirmar.setFixedSize(200, 50)
        botao_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        #botao_confirmar.clicked.connect(lambda: self.comprar(anuncio, formulario))
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela

    def tela_cadastro(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_vertical.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addSpacing(50)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Cadastramento</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Nome", "CPF", "Email", "Senha"], largura=600, altura=50)
        formulario.validar_tipos({"Nome": str, "CPF": str, "Email": str, "Senha": str})
        layout_vertical.addWidget(formulario)

        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.setFixedSize(200, 50)
        botao_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        botao_cadastrar.clicked.connect(lambda: formulario.exibir_erros())
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_login = QPushButton("Login")
        botao_login.setFixedSize(110, 30)
        botao_login.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        botao_login.clicked.connect(lambda: self.abrir_tela(self.tela_login()))
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignRight)

        return tela

    def tela_login(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_vertical.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addSpacing(50)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Login</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Email", "Senha"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_login = QPushButton("Entrar")
        botao_login.setFixedSize(200, 50)
        botao_login.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        
        #botao_login.clicked.connect(lambda: self.login_usuario(formulario))
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_cadastrar = QPushButton("Cadastrar")
        botao_cadastrar.setFixedSize(110, 30)
        botao_cadastrar.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        botao_cadastrar.clicked.connect(lambda: self.abrir_tela(self.tela_cadastro()))
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignRight)

        return tela

    def tela_perfil(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = self.botao_editar(None)
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Meu Perfil</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "CPF", "Email", "Senha"],
            largura=600,
            altura=50
        )
        formulario.preencher_campos(
            {"Nome": "João Silva", "CPF": "123.456.789-10", "Email": "joaosilva@gmail.com"}
        )
        formulario.validar_tipos(
            {"Nome": str, "CPF": str, "Email": str}
        )
        botao_editar.clicked.connect(lambda: formulario.exibir_erros())
        layout_conteudo.addWidget(formulario)

        botao_endereco = QPushButton("Meus Endereços")
        botao_endereco.setFixedSize(180, 50)
        botao_endereco.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        botao_endereco.clicked.connect(lambda: self.abrir_tela(self.tela_meus_enderecos()))
        layout_conteudo.addStretch()
        layout_conteudo.addWidget(botao_endereco, alignment=Qt.AlignmentFlag.AlignLeft)

        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_meus_enderecos(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Meus enderecos</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        layout_horizontal2 = QHBoxLayout()

        formulario = Formulario(
            campos=[f"Endereço{i+1}" for i in range(10)],
            largura=600,
            altura=50
        )
        formulario.preencher_campos(
            {f"Endereço{i+1}": f"endereço{i+1}" for i in range(10)}
        )
        formulario.validar_tipos(
            {f"Endereço{i+1}": str for i in range(10)}
        )
        layout_horizontal2.addWidget(formulario)

        layout_vertical2 = QVBoxLayout()
       
        botao_editar = []
        for i in range(10):
            botao_editar.append(self.botao_editar(
                lambda: self.abrir_tela(self.tela_meu_endereco(f"{i}"))
            ))
            layout_vertical2.addWidget(botao_editar[i])

        layout_horizontal2.addLayout(layout_vertical2)
        layout_conteudo.addLayout(layout_horizontal2)

        botao_adicionar = self.botao_adicionar(lambda: self.abrir_tela(self.tela_criar_endereco()))
        layout_conteudo.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_meu_endereco(self, endereco):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = self.botao_editar(None)
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Endereço {endereco}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Rua", "N°", "Bairro", "Cidade", "Estado", "Complemento"],
            largura=600,
            altura=50
        )
        formulario.preencher_campos(
            {"Rua": "", "N°": "", "Bairro": "", "Cidade": "", "Estado": "", "Complemento": ""}
        )
        formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        botao_editar.clicked.connect(lambda: formulario.exibir_erros())
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def tela_criar_endereco(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_criar = self.botao_confirmar(None)
        layout_horizontal.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Endereço</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Rua", "N°", "Bairro", "Cidade", "Estado", "Complemento"],
            largura=600,
            altura=50
        )
        formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        botao_criar.clicked.connect(lambda: formulario.exibir_erros())
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_minhas_lojas(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)
        layout_horizintal = QHBoxLayout()

        layout_horizintal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        botao_adicionar = self.botao_adicionar(lambda: self.abrir_tela(self.tela_criar_loja()))
        layout_horizintal.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizintal)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Minhas Lojas</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addSpacing(40)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        conteudo_scroll = QWidget()
        layout_loja = QVBoxLayout(conteudo_scroll)
        layout_loja.setSpacing(15)

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

        blocos = self.tela_lista_lojas(lojas)
        layout_vertical.addWidget(blocos)
        layout_vertical.addStretch()

        return tela
    
    def tela_minha_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = self.botao_editar(lambda: self.abrir_tela(self.tela_loja(loja)))
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal)
        layout_vertical.addSpacing(20)

        imagem_label = QLabel()
        pixmap = QPixmap(loja.imagem).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        imagem_label.setPixmap(pixmap)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(imagem_label, alignment=Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel(f"<span style='font-size: 40px; font-weight: bold'>{loja.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        layout_horizontal2 = QHBoxLayout()

        botao_anuncios = QPushButton("Anuncios")
        botao_anuncios.setFixedSize(110, 30)
        botao_anuncios.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        layout_horizontal2.addWidget(botao_anuncios)

        botao_produtos = QPushButton("Produtos")
        botao_produtos.setFixedSize(110, 30)
        botao_produtos.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        layout_horizontal2.addWidget(botao_produtos)

        botao_pedidos_confirmados = QPushButton("Pedidos Confirmados")
        botao_pedidos_confirmados.setFixedSize(220, 30)
        botao_pedidos_confirmados.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        layout_horizontal2.addWidget(botao_pedidos_confirmados)

        botao_pedidos_em_andamento = QPushButton("Pedidos Em Andamento")
        botao_pedidos_em_andamento.setFixedSize(220, 30)
        botao_pedidos_em_andamento.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: 2px solid #005fa3;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
        """)
        layout_horizontal2.addWidget(botao_pedidos_em_andamento)

        lista_anuncios = self.tela_lista_anuncios(loja.anuncios, editar=True)
        lista_produtos = self.tela_lista_produtos(loja.produtos, adicionar=True)
        lista_pedidos_confirmados = self.tela_lista_pedidos(loja.pedidos_confirmados)
        lista_pedidos_em_andamento = self.tela_lista_pedidos(loja.pedidos_em_andamento, confirmar=True)

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
    
    def tela_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        botao_criar = self.botao_editar()
        layout_horizontal.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Editar Loja</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Imagem"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos(
            {
                "Nome": loja.nome, 
                "Imagem": loja.imagem
            }
        )
    
        formulario.validar_tipos(
            {
                "Nome": str, 
                "Imagem": str
            }
        )
    
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        botao_excluir = self.botao_excluir()
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela

    def tela_criar_loja(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_criar = self.botao_confirmar(None)
        layout_horizontal.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Loja</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Imagem"],
            largura=600,
            altura=50
        )
    
        formulario.validar_tipos(
            {"Nome": str, "Imagem": str}
        )
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_produto(self, produto):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        botao_editar = self.botao_editar()
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>{produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição", "Imagens"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos( {"Nome": produto.nome, "Descrição": produto.descricao, "Imagens": produto.imagens[0]})
    
        formulario.validar_tipos(
            {"Nome": str, "Descrição": str, "Imagens": str}
        )
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        layout_horizontal_2 = QHBoxLayout()

        botao_excluir = self.botao_excluir()
        layout_horizontal_2.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_criar = self.botao(nome="Criar Anúncio",fonte=15, acao=lambda: self.abrir_tela(self.tela_criar_anuncio(produto)))
        layout_horizontal_2.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal_2)

        return tela
    
    def tela_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        botao_criar = self.botao_editar()
        layout_horizontal.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Anúncio: {anuncio.produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Preço", "Quantidade Disponível", "Chave Pix", "Pausado"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos(
            {
                "Preço": anuncio.preco, 
                "Quantidade Disponível": anuncio.quantidade_disponivel, 
                "Chave Pix": anuncio.chave_pix, 
                "Pausado": anuncio.pausado
            }
        )
    
        formulario.validar_tipos(
           {
                "Preço": float, 
                "Quantidade Disponível": int, 
                "Chave Pix": str, 
                "Pausado": bool
            }
        )
    
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        botao_excluir = self.botao_excluir()
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela
    
    def tela_criar_produto(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        botao_criar = self.botao_confirmar(None)
        layout_horizontal.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Produto</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição", "Imagens"],
            largura=600,
            altura=50
        )
    
        formulario.validar_tipos(
            {"Nome": str, "Descrição": str, "Imagens": str}
        )
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def tela_criar_anuncio(self, produto):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = self.botao_confirmar()
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Anúncio</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addSpacing(40)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Preço", "Quantidade Disponível", "Chave Pix", "Pausado"],
            largura=600,
            altura=50
        )
    
        formulario.validar_tipos(
           {
                "Preço": float, 
                "Quantidade Disponível": int, 
                "Chave Pix": str, 
                "Pausado": bool
            }
        )
    
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_meus_pedidos(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_vertical.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Meus Pedidos</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addSpacing(40)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

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

        blocos = self.tela_lista_pedidos(pedidos)
        layout_vertical.addWidget(blocos)

        return tela

if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = MarketplaceUI()
   window.show()
   sys.exit(app.exec())
