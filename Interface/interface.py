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

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import (
   QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QFileDialog,QFormLayout, QSpacerItem, QSizePolicy,
   QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QFrame, QStackedWidget, QPushButton, QComboBox
) 

class FormularioOpcoes(QWidget):
    def __init__(self, campos, largura=300, altura=40):
        super().__init__()

        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.inputs = {}
        self.botoes_adicionar = {}

        for nome in campos:
            # Label
            label = QLabel(f"{nome}:")
            label.setStyleSheet("font-size: 25px;")

            # ComboBox
            combo = QComboBox()
            combo.setFixedSize(largura, altura)
            combo.setStyleSheet("font-size: 18px;")

            # Botão
            botao_adicionar = QPushButton("Adicionar")
            botao_adicionar.setFixedSize(100, 40)
            botao_adicionar.hide()
            botao_adicionar.setStyleSheet("font-size: 18px;")

            # Layout para Combo + Botão
            layout_combo = QHBoxLayout()
            layout_combo.addWidget(combo)
            layout_combo.addWidget(botao_adicionar)

            # Container vertical para alinhar corretamente
            campo_layout = QVBoxLayout()
            campo_layout.addLayout(layout_combo)

            form_layout.addRow(label, campo_layout)

            # Armazenar para uso posterior
            self.inputs[nome] = combo
            self.botoes_adicionar[nome] = botao_adicionar

        layout_principal.addLayout(form_layout)
        self.setLayout(layout_principal)

    def ativar_botao_adicionar(self, campo, acao):
        botao = self.botoes_adicionar[campo]
        botao.clicked.connect(lambda: acao)
        botao.show()

    def adicionar_opcao(self, campo, opcao="Nova opção"):
        combo = self.inputs[campo]
        combo.addItem(opcao)

class Formulario(QWidget):
    def __init__(self, campos=[], largura=300, altura=30):
        super().__init__()

        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignTop)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)  # Centraliza o formulário

        self.inputs = {}
        self.erros = {}

        for nome in campos:
            entrada = QLineEdit()
            entrada.setPlaceholderText(f"Digite seu {nome.lower()}")
            entrada.setFixedSize(largura, altura)
            entrada.setStyleSheet("font-size: 25px;")

            label = QLabel(f"{nome}:")
            label.setStyleSheet("font-size: 25px;")

            erro_label = QLabel("")
            erro_label.setStyleSheet("color: red; font-size: 18px;")
            erro_label.setVisible(False)

            self.inputs[nome] = entrada
            self.erros[nome] = erro_label

            campo_layout = QVBoxLayout()
            campo_layout.addWidget(entrada)
            campo_layout.addWidget(erro_label)

            form_layout.addRow(label, campo_layout)
            self.inputs[nome] = entrada

        layout_principal.addLayout(form_layout)
        self.setLayout(layout_principal)

    def preencher_campos(self, valores: dict):
        """
        Preenche os campos do formulário com os valores fornecidos.
        Exemplo: {"Nome": "Ana", "Email": "ana@email.com"}
        """
        for chave, valor in valores.items():
            if chave in self.inputs:
                self.inputs[chave].setText(str(valor))

    def validar_tipos(self, campos_tipos: dict):
        """
        Valida os campos do formulário com base no tipo esperado.
        
        :param campos_tipos: dicionário no formato {"Nome": str, "Idade": int, ...}
        :return: se houve erro (True) ou não (False)
        """
        has_error = False

        for nome, tipo_esperado in campos_tipos.items():
            texto = self.inputs[nome].text().strip()

            if tipo_esperado == str:
                if not texto:
                    erro = "Este campo não pode estar vazio."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                else:
                    self.erros[nome].setText(str(""))

            elif tipo_esperado == int:
                try:
                    int(texto)
                except ValueError:
                    erro = "Digite um número inteiro válido."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                else:
                    self.erros[nome].setText(str(""))
                
            elif tipo_esperado == float:
                try:
                    float(texto)
                except ValueError:
                    erro ="Digite um número decimal válido."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                self.erros[nome].setText(str(""))

            elif tipo_esperado == bool:
                if texto.lower() not in ["true", "false"]:
                    erro = "Digite 'true' ou 'false'."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                self.erros[nome].setText(str(""))

            if nome.lower() == "email":
                if not vu.check_email(texto):
                    erro = "Email inválido."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                else:
                    self.erros[nome].setText(str(""))

            elif nome.lower() == "cpf":
                if not vu.check_cpf(texto):
                    erro = "CPF inválido."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                else:
                    self.erros[nome].setText(str(""))

        return has_error
    
    def exibir_erros(self):
        """
        Exibe os erros do dicionário de erros.
        """
        for nome, erro in self.erros.items():
            texto = erro.text()
            if texto:
                erro.setVisible(True)
            else:
                erro.setVisible(False)

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
        self.tela_lista = self.criar_tela_lista_anuncios(self.anuncios)

        self.tela_inicial = self.criar_tela_inicial()

        self.stack.addWidget(self.tela_inicial)

    def botao_voltar(self):
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

        return voltar
    
    def botao_confirmar(self, acao):
        botao_confirmar = QPushButton("Confirmar")
        botao_confirmar.setFixedSize(110, 30)
        botao_confirmar.setStyleSheet("""
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
        botao_confirmar.clicked.connect(acao)

        return botao_confirmar
    
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
        botao_perfil.clicked.connect(self.abrir_tela_perfil)

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
        botao_lojas.clicked.connect(self.abrir_tela_minhas_lojas)

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
        botao_pedidos.clicked.connect(self.abrir_tela_meus_pedidos)

        # Adicionando os botões ao layout da barra lateral
        menu_layout.addWidget(botao_perfil, alignment=Qt.AlignmentFlag.AlignHCenter)  # Alinhando ao centro
        menu_layout.addWidget(botao_lojas, alignment=Qt.AlignmentFlag.AlignHCenter)  # Alinhando ao centro
        menu_layout.addWidget(botao_pedidos, alignment=Qt.AlignmentFlag.AlignHCenter)  # Alinhando ao centro
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

        barra_superior.addWidget(botao_selecionar_arquivo, alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(botao_menu)
        barra_superior.addWidget(QLabel("<h2>Produtos disponíveis:</h2>"), alignment=Qt.AlignmentFlag.AlignLeft)
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

    def criar_tela_inicial(self):
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

    def criar_tela_lista_anuncios(self, anuncios):
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
            bloco = self.criar_bloco_anuncio(anuncio, largura_bloco, altura_bloco)
            self.grid.addWidget(bloco, i // 5, i % 5)

        scroll.setWidget(conteudo)
        return scroll

    def criar_bloco_anuncio(self, anuncio: Anuncio, largura, altura):
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

        bloco.mousePressEvent = lambda e: self.abrir_tela_detalhes_anuncio(anuncio)
        return bloco

    def abrir_tela_detalhes_anuncio(self, anuncio):
        tela_detalhes = self.criar_tela_detalhes_anuncio(anuncio)
        self.stack.addWidget(tela_detalhes)
        self.stack.setCurrentWidget(tela_detalhes)
    
    def abrir_tela_detalhes_loja(self, loja):
        tela_detalhes = self.criar_tela_detalhes_loja(loja)
        self.stack.addWidget(tela_detalhes)
        self.stack.setCurrentWidget(tela_detalhes)

    def criar_tela_detalhes_anuncio(self, anuncio: Anuncio):
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
        loja.clicked.connect(lambda: self.abrir_tela_detalhes_loja(anuncio.produto.loja))
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
        
        comprar.clicked.connect(lambda: self.abrir_tela_comprar(anuncio))
        layout_horizontal_2.addWidget(comprar, alignment=Qt.AlignmentFlag.AlignRight)

        layout_vertical.addLayout(layout_horizontal_2)

        return tela

    def criar_tela_detalhes_loja(self, loja: Loja):
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

        anuncios = self.criar_tela_lista_anuncios(loja.anuncios)
        self.atualizar_lista_anuncios(loja.anuncios)
        layout_vertical.addWidget(anuncios)

        return tela

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
    
    def abrir_tela_comprar(self, anuncio: Anuncio):
        tela_comprar = self.criar_tela_comprar(anuncio)
        self.stack.addWidget(tela_comprar)
        self.stack.setCurrentWidget(tela_comprar)

    def criar_tela_comprar(self, anuncio: Anuncio):
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

    def comprar(self, anuncio: Anuncio, formularioOp: FormularioOpcoes):
        anuncio.subtrair_quantidade(1)
        
    def abrir_tela_cadastro(self):
        tela_cadastro = self.criar_tela_cadastro()
        self.stack.addWidget(tela_cadastro)
        self.stack.setCurrentWidget(tela_cadastro)

    def criar_tela_cadastro(self):
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
        botao_login.clicked.connect(self.abrir_tela_login)
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignRight)

        return tela
    
    def abrir_tela_login(self):
        tela_login = self.criar_tela_login()
        self.stack.addWidget(tela_login)
        self.stack.setCurrentWidget(tela_login)

    def criar_tela_login(self):
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
        botao_cadastrar.clicked.connect(self.abrir_tela_cadastro)
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignRight)

        return tela
    
    def abrir_tela_perfil(self):
        tela_perfil = self.criar_tela_perfil()
        self.stack.addWidget(tela_perfil)
        self.stack.setCurrentWidget(tela_perfil)

    def criar_tela_perfil(self):
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
        botao_endereco.clicked.connect(self.abrir_tela_meus_enderecos)
        layout_conteudo.addStretch()
        layout_conteudo.addWidget(botao_endereco, alignment=Qt.AlignmentFlag.AlignLeft)

        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def abrir_tela_meus_enderecos(self):
        tela_meus_enderecos = self.criar_tela_meus_enderecos()
        self.stack.addWidget(tela_meus_enderecos)
        self.stack.setCurrentWidget(tela_meus_enderecos)

    def criar_tela_meus_enderecos(self):
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
                lambda: self.abrir_tela_endereco(f"{i}")
            ))
            layout_vertical2.addWidget(botao_editar[i])

        layout_horizontal2.addLayout(layout_vertical2)
        layout_conteudo.addLayout(layout_horizontal2)

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
        #botao_adicionar.clicked.connect(lambda: formulario.exibir_erros())
        layout_conteudo.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela
    
    def abrir_tela_endereco(self, endereco):
        tela_endereco = self.criar_tela_endereco(endereco)
        self.stack.addWidget(tela_endereco)
        self.stack.setCurrentWidget(tela_endereco)

    def criar_tela_endereco(self, endereco):
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

    def abrir_tela_minhas_lojas(self):
        tela_lojas = self.criar_tela_minhas_lojas()
        self.stack.addWidget(tela_lojas)
        self.stack.setCurrentWidget(tela_lojas)

    def criar_tela_minhas_lojas(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_vertical.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

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

        loja = [
            {"nome": "João Silva"},
            {"nome": "Maria Lima"},
            {"nome": "Carlos Souza"},
        ]

        for pedido in loja:
            bloco_botao = QPushButton()
            bloco_botao.setStyleSheet("""
                QPushButton {
                    border: 2px solid #444;
                    border-radius: 10px;
                    padding: 15px;
                    background-color: #222;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """)
            bloco_botao.setFixedHeight(100)  # Ajuste conforme quiser
            bloco_botao.setCursor(Qt.CursorShape.PointingHandCursor)

            conteudo = QWidget()
            conteudo_layout = QHBoxLayout(conteudo)  # HBox: imagem à esquerda, texto à direita
            conteudo_layout.setContentsMargins(10, 10, 10, 10)

            # Imagem (exemplo com caminho fixo)
            imagem_label = QLabel()
            imagem_label.setPixmap(QPixmap("imagens/notebook.png").scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
            imagem_label.setFixedSize(64, 64)

            # Textos
            textos = QWidget()
            textos_layout = QVBoxLayout(textos)
            textos_layout.setContentsMargins(10, 0, 0, 0)  # Espaço entre imagem e texto

            nome = QLabel(f"Nome: {pedido['nome']}")
            nome.setStyleSheet("font-size: 16px; color: white;")

            textos_layout.addWidget(nome)

            # Montagem
            conteudo_layout.addWidget(imagem_label)
            conteudo_layout.addWidget(textos)
            bloco_botao.setLayout(conteudo_layout)


            for widget in [nome]:
                widget.setStyleSheet("font-size: 16px; color: white;")

            conteudo_layout.addWidget(nome)

            bloco_botao.setLayout(conteudo_layout)
            bloco_botao.clicked.connect(lambda _, p=pedido: print(f"Pedido clicado: {p['nome']}"))

            layout_loja.addWidget(bloco_botao)

        layout_loja.addStretch()
        scroll_area.setWidget(conteudo_scroll)

        layout_vertical.addWidget(scroll_area)
        layout_vertical.addStretch()

        return tela
    
    def abrir_tela_nova_loja(self, loja):
        tela_loja = self.criar_tela_nova_loja(loja)
        self.stack.addWidget(tela_loja)
        self.stack.setCurrentWidget(tela_loja)

    def criar_tela_nova_loja(self, loja):
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
    
    def abrir_tela_novo_produto(self, produto):
        tela_produto = self.criar_tela_novo_produto(produto)
        self.stack.addWidget(tela_produto)
        self.stack.setCurrentWidget(tela_produto)

    def criar_tela_novo_produto(self, produto):
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
    
    def abrir_tela_meus_pedidos(self):
        tela_pedidos = self.criar_tela_meus_pedidos()
        self.stack.addWidget(tela_pedidos)
        self.stack.setCurrentWidget(tela_pedidos)

    def criar_tela_meus_pedidos(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_vertical.addWidget(self.botao_voltar(), alignment=Qt.AlignmentFlag.AlignLeft)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Meus Pedidos</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addSpacing(40)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        conteudo_scroll = QWidget()
        layout_pedidos = QVBoxLayout(conteudo_scroll)
        layout_pedidos.setSpacing(15)

        pedidos = [
            {"nome": "João Silva", "email": "joao@example.com", "pontuacao": 850},
            {"nome": "Maria Lima", "email": "maria@example.com", "pontuacao": 910},
            {"nome": "Carlos Souza", "email": "carlos@example.com", "pontuacao": 720},
        ]

        for pedido in pedidos:
            bloco_botao = QPushButton()
            bloco_botao.setStyleSheet("""
                QPushButton {
                    border: 2px solid #444;
                    border-radius: 10px;
                    padding: 15px;
                    background-color: #222;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #333;
                }
            """)
            bloco_botao.setFixedHeight(100)  # Ajuste conforme quiser
            bloco_botao.setCursor(Qt.CursorShape.PointingHandCursor)

            conteudo = QWidget()
            conteudo_layout = QVBoxLayout(conteudo)
            conteudo_layout.setContentsMargins(10, 10, 10, 10)

            nome = QLabel(f"Nome: {pedido['nome']}")
            email = QLabel(f"Email: {pedido['email']}")
            pontuacao = QLabel(f"Pontuação: {pedido['pontuacao']}")

            for widget in [nome, email, pontuacao]:
                widget.setStyleSheet("font-size: 16px; color: white;")

            conteudo_layout.addWidget(nome)
            conteudo_layout.addWidget(email)
            conteudo_layout.addWidget(pontuacao)

            bloco_botao.setLayout(conteudo_layout)
            bloco_botao.clicked.connect(lambda _, p=pedido: print(f"Pedido clicado: {p['nome']}"))

            layout_pedidos.addWidget(bloco_botao)

        layout_pedidos.addStretch()
        scroll_area.setWidget(conteudo_scroll)

        layout_vertical.addWidget(scroll_area)
        layout_vertical.addStretch()

        return tela

if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = MarketplaceUI()
   window.show()
   sys.exit(app.exec())
