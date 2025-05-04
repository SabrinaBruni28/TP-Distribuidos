import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import (
   QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
   QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QFrame, QStackedWidget, QPushButton
)

class Produto:
    def __init__(self, nome, descricao, preco, imagem_path):
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.imagens = imagem_path

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
        self.setWindowTitle("Marketplace")
        self.setGeometry(100, 100, 1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        # Crie o menu lateral e esconda no início
        self.menu_lateral = QFrame()
        self.menu_lateral.setFrameShape(QFrame.Shape.StyledPanel)
        self.menu_lateral.setFixedWidth(250)
        self.menu_lateral.hide()

        self.produtos = self.criar_lista_produtos()

        self.tela_lista = self.criar_tela_lista_produtos()
        self.stack.addWidget(self.tela_lista)

    def criar_lista_produtos(self):
        return [
            Produto("Notebook", "Notebook potente com 16GB RAM", 4500.00, ["imagens/notebook.png", "imagens/smartphone.png", "imagens/notebook.png"]),
            Produto("Smartphone", "Celular moderno com ótima câmera", 2500.00, ["imagens/smartphone.png", "imagens/smartphone.png"]),
            Produto("Fone Bluetooth", "Fones com cancelamento de ruído", 600.00, ["imagens/fone.png"]),
            Produto("Tablet", "Ideal para leitura e navegação", 1500.00, ["imagens/tablet.png"]),
        ] * 20

    def criar_tela_lista_produtos(self):
        tela = QWidget()

        # Layout horizontal principal (menu + conteúdo)
        layout_h = QHBoxLayout(tela)

        # Adiciona a barra lateral ao layout principal (inicialmente oculta)
        layout_h.addWidget(self.menu_lateral)

        # Layout para a barra lateral
        menu_layout = QVBoxLayout(self.menu_lateral)
        menu_layout.setSpacing(0)  # Definir o espaçamento entre os botões como 0
        menu_layout.setContentsMargins(0, 0, 0, 0)  # Remove as margens

        # Exemplo de adição de botões à barra lateral
        botao_home = QPushButton("Perfil")
        botao_home.setFixedSize(250, 100)  # Tamanho fixo do botão
        botao_home.setStyleSheet("""
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

        botao_categoria = QPushButton("Minhas lojas")
        botao_categoria.setFixedSize(250, 100)  # Tamanho fixo do botão
        botao_categoria.setStyleSheet("""
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

        # Adicionando os botões ao layout da barra lateral
        menu_layout.addWidget(botao_home, alignment=Qt.AlignmentFlag.AlignHCenter)  # Alinhando ao centro
        menu_layout.addWidget(botao_categoria, alignment=Qt.AlignmentFlag.AlignHCenter)  # Alinhando ao centro
        menu_layout.addStretch()  # Adiciona um espaçador para empurrar os botões para cima

        # Layout vertical para o conteúdo da tela
        layout_conteudo = QVBoxLayout()

        # Barra superior com botões
        barra_superior = QHBoxLayout()
        self.botao_menu = QPushButton("≡")
        self.botao_menu.setFixedSize(50, 50)
        self.botao_menu.setStyleSheet("""
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
        self.botao_menu.clicked.connect(self.toggle_menu)

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

        barra_superior.addWidget(self.botao_menu)
        barra_superior.addWidget(QLabel("<h2>Produtos disponíveis:</h2>"), alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(self.botao_reset)
        barra_superior.addWidget(self.input_busca)
        barra_superior.addWidget(btn_pesquisa)

        layout_conteudo.addLayout(barra_superior)

        # Área com produtos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        self.grid = grid

        largura_bloco = 250
        altura_bloco = 300
        for i, produto in enumerate(self.produtos):
            bloco = self.criar_bloco_produto(produto, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)

        scroll.setWidget(container)
        layout_conteudo.addWidget(scroll)

        # Agora adiciona o conteúdo principal no layout horizontal
        layout_h.addLayout(layout_conteudo)

        return tela

    def criar_bloco_produto(self, produto, largura, altura):
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
        preco_label = QLabel(f"R$ {produto.preco:.2f}")
        nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preco_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(imagem_label)
        layout.addSpacing(5)
        layout.addWidget(nome_label)
        layout.addWidget(preco_label)

        bloco.mousePressEvent = lambda e: self.abrir_tela_detalhes(produto)
        return bloco

    def abrir_tela_detalhes(self, produto):
        tela_detalhes = self.criar_tela_detalhes(produto)
        self.stack.addWidget(tela_detalhes)
        self.stack.setCurrentWidget(tela_detalhes)

    def criar_tela_detalhes(self, produto):
        tela = QWidget()
        layout = QVBoxLayout(tela)

        carrossel = CarrosselImagem(produto.imagens, largura=350, altura=350)

        titulo = QLabel(f"<span style='font-size: 40px; font-weight: bold'>{produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preco = QLabel(f"<span style='font-size: 30px; color: green'>R$ {produto.preco:.2f}</span>")
        preco.setAlignment(Qt.AlignmentFlag.AlignCenter)

        descricao = QLabel(f"<span style='font-size: 20px'>{produto.descricao}</span>")
        descricao.setWordWrap(True)
        descricao.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        voltar = QPushButton("Voltar")
        voltar.setFixedSize(100, 30)
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

        layout.addWidget(voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(carrossel, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        layout.addWidget(descricao)
        layout.addWidget(preco)
        layout.addWidget(comprar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela

    def voltar_para_lista(self):
        self.stack.setCurrentWidget(self.tela_lista)

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
        produtos_filtrados = [
            p for p in self.produtos if texto in p.nome.lower()
        ]
        self.atualizar_lista_produtos(produtos_filtrados)

    def resetar_busca(self):
        self.input_busca.clear()
        self.input_busca.hide()
        self.botao_reset.hide()
        self.atualizar_lista_produtos(self.produtos)

    def atualizar_lista_produtos(self, nova_lista):
        # Remove widgets antigos
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        largura_bloco = 250
        altura_bloco = 300
        for i, produto in enumerate(nova_lista):
            bloco = self.criar_bloco_produto(produto, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)

if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = MarketplaceUI()
   window.show()
   sys.exit(app.exec())
