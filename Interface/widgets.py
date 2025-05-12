import re, sys, os, shutil
# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pybrcode.pix import generate_simple_pix

from PyQt6.QtGui import QPixmap, QPainterPath, QRegion, QMovie
from PyQt6.QtCore import Qt, QTimer, QRectF, QThread, QObject, pyqtSignal

from PyQt6.QtWidgets import (
   QApplication, QWidget, QLabel, QFileDialog,QHBoxLayout, QPushButton, QVBoxLayout, QDialog
)

class WorkerGenerico(QObject):
    terminado = pyqtSignal()

    def __init__(self, funcao):
        super().__init__()
        self.funcao = funcao

    def run(self):
        self.funcao()
        self.terminado.emit()


class WidgetHelper(QWidget):

    @staticmethod
    def carregar_em_thread(funcao_segundo_plano, quando_terminar, tela_loading=None, abrir_tela=None):
        thread = QThread()
        worker = WorkerGenerico(funcao_segundo_plano)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.terminado.connect(thread.quit)
        worker.terminado.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        def ao_terminar():
            if quando_terminar:
                quando_terminar()
        
        worker.terminado.connect(ao_terminar)

        thread.start()

        # Mostrar tela de carregamento se fornecida
        if tela_loading and abrir_tela:
            abrir_tela(tela_loading)

        return thread
    
    @staticmethod
    def criar_tela_carregando_com_spinner(mensagem="Carregando...", gif_path="spinner.gif"):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner animado
        spinner = QLabel()
        movie = QMovie(gif_path)
        spinner.setMovie(movie)
        movie.start()

        # Mensagem opcional
        texto = QLabel(f"<span style='font-size: 20px'>{mensagem}</span>")
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(spinner)
        layout.addWidget(texto)

        return tela

    @staticmethod
    def criar_tela_carregando(mensagem="Carregando..."):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"<span style='font-size: 24px'>{mensagem}</span>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        return tela

    @staticmethod
    def mostrar_alerta_temporario(
        parent_widget, mensagem, duracao_ms=3000,
        largura=110, altura=30, fonte=20, paddingH = 20, paddingV=20,
        fontcolor = 'white', backcolor='#0078d7',
        border = '#000000',
    ):
        
        alerta = QLabel(mensagem, parent_widget)
        alerta.setFixedSize(largura, altura)
        alerta.setStyleSheet(f"""
            QLabel {{
                background-color: {backcolor};
                color: {fontcolor};
                border: 2px solid {border};
                border-radius: 2px;
                padding: 5px;
                font-weight: bold;
                font-size: {fonte}px;
            }}
        """)

        alerta.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Coloca o alerta por cima de tudo
        alerta.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        alerta.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Centraliza no parent
        parent_rect = parent_widget.geometry()
        alerta.adjustSize()
        alerta_width = alerta.width()
        alerta.move(
            parent_rect.x() + parent_rect.width() - alerta_width - paddingH,
            parent_rect.y() + paddingV
        )

        alerta.show()

        # Esconde depois da duração
        QTimer.singleShot(duracao_ms, alerta.close)

    @staticmethod
    def copiar_texto(label: QLabel):
        clipboard = QApplication.clipboard()
        texto_sem_html = label.text()  # Isso ainda está com HTML
        # Se quiser extrair só o texto puro:
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(texto_sem_html)
        texto_puro = doc.toPlainText()

        clipboard.setText(texto_puro)

    @staticmethod
    def botao(
        nome, fonte = 20, largura = 110, altura = 30, 
        fontcolor = 'white', backcolor='#0078d7', 
        hover='#005fa3', pressed='#003f7f',
        border = 'solid #005fa3',
        acao = None,
    ):
        botao = QPushButton(nome)
        botao.setFixedSize(largura, altura)
        botao.setStyleSheet(f"""
            QPushButton {{
                background-color: {backcolor};
                color: {fontcolor};
                border: 2px {border};
                border-radius: 10px;
                font-weight: bold;
                font-size: {fonte}px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
        """)
        if acao:
            botao.clicked.connect(acao)

        return botao
    
    @staticmethod
    def criar_dict_de_atributos(obj, atributos: list):
        return {attr: getattr(obj, attr, None) for attr in atributos}
    
    @staticmethod
    def check_cpf(cpf: str) -> bool:
        """
        Valida um número de CPF (Cadastro de Pessoa Física).

        Parâmetros:
        - cpf: string com ou sem máscara (ex: '12.345.678-95' ou '12345678000195')

        Retorna:
        - True se o CPF for válido, False caso contrário.
        """
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        def calc_digit(digs):
            s = sum(int(d) * i for d, i in zip(digs, range(len(digs) + 1, 1, -1)))
            r = 11 - s % 11
            return '0' if r > 9 else str(r)

        d1 = calc_digit(cpf[:9])
        d2 = calc_digit(cpf[:9] + d1)
        return cpf.endswith(d1 + d2)
    
    @staticmethod
    def check_email(email: str) -> bool:
        """
        Valida se o e-mail fornecido está em um formato válido.

        Parâmetros:
        - email: string com o e-mail a ser validado

        Retorna:
        - True se for um e-mail válido, False caso contrário
        """
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None
    
    @staticmethod
    def gerar_qrcode_pix(
        nome: str,
        chave: str,
        cidade: str,
        valor: float,
        descricao: str = "",
        pagamento_multiplo: bool = False,
        salvar_svg: bool = True,
        salvar_png: bool = True,
        nome_arquivo: str = "pix_qrcode"
    ):
        """
        Gera um QR Code Pix com base nas informações fornecidas e salva como imagem.

        Parâmetros:
        - nome: Nome completo do recebedor (máx. 25 caracteres)
        - chave: Chave Pix (email, CPF, telefone, chave aleatória)
        - cidade: Cidade do recebedor (máx. 15 caracteres)
        - valor: Valor do Pix (float)
        - descricao: Descrição opcional da transação
        - pagamento_multiplo: True para QR Code reutilizável
        - salvar_svg: Salvar versão em SVG
        - salvar_png: Salvar versão em PNG
        - nome_arquivo: Nome base do arquivo (sem extensão)

        Retorna:
        - Dicionário com: payload Pix, base64 PNG e SVG string
        """
        pix = generate_simple_pix(
            fullname=nome,
            key=chave,
            city=cidade,
            value=valor,
            description=descricao,
            mult_transaction=pagamento_multiplo
        )

        try:
            if salvar_svg:
                pix.imageToPath(destDir=".", filename=nome_arquivo, svg=True)
            if salvar_png:
                pix.imageToPath(destDir=".", filename=nome_arquivo, svg=False)
        except Exception as e:
            print("Erro ao salvar imagem:", e)

        return {
            "payload": str(pix),
            "base64_png": pix.toBase64(),
            "svg_string": pix.toSVG()
        }
    
    @staticmethod
    def abrir_dialogo_arquivo(parent):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            parent,
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

class CaixaConfirmacao(QDialog):
    def __init__(self, parent=None, titulo=None, mensagem = None, fonte=20, largura=400, altura=100):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumSize(largura, altura)

        layout = QVBoxLayout()
        mensagem = QLabel(f"<p style='font-size:{fonte}px;'>{mensagem}</p>", self)
        layout.addWidget(mensagem)

        botoes = QHBoxLayout()
        btn_sim = QPushButton("Sim", self)
        btn_nao = QPushButton("Não", self)
        botoes.addWidget(btn_sim)
        botoes.addWidget(btn_nao)

        layout.addLayout(botoes)
        self.setLayout(layout)

        btn_sim.clicked.connect(self.accept)
        btn_nao.clicked.connect(self.reject)