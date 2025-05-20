import sys, os, shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import Utils
from PyQt6.QtGui import QPixmap, QMovie, QPainter
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, QObject, pyqtSignal

from PyQt6.QtWidgets import (
   QPushButton, QApplication, QWidget, QLabel, QDialog,
   QVBoxLayout, QHBoxLayout, QFrame, QFileDialog, QScrollArea,
   QGridLayout
)

class WorkerGenerico(QObject):
    terminado = pyqtSignal(object)  # envia resultado

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        resultado = self.func()
        self.terminado.emit(resultado)

class Threads:
    def __init__(self, stack):
        self.stack = stack
        self.view = ViewHelper()

    def carregar_em_thread(self, funcao_segundo_plano, quando_terminar=None, tela_loading=None, abrir_tela=None, voltar_tela=None, atualizar=True):
        thread = QThread()
        worker = WorkerGenerico(funcao_segundo_plano)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.terminado.connect(lambda resultado: self._finalizar_thread(
            thread, worker, quando_terminar, voltar_tela, resultado, atualizar
        ))
        
        thread.start()
        if abrir_tela and tela_loading:
            self.view.abrir_tela(stack=self.stack, funcao_criadora=tela_loading, salvar_tela=False)

    def _finalizar_thread(self, thread, worker, quando_terminar=None, voltar_tela=None, resultado=None, atualizar=True):
        thread.quit()
        thread.wait()
        thread.deleteLater()
        worker.deleteLater()

        if voltar_tela:
            self.view.voltar_tela(self.stack, excluir_funcao=False, atualizar_tela=atualizar)

        if quando_terminar:
            quando_terminar(resultado)

    def executar_mensagem(self, requisicao, acao, mensagem="Carregando ...", atualizar_tela=True):
        tela_carregando = lambda: ViewHelper.tela_carregando_com_spinner(
            mensagem, gif_path="images/spinner.gif"
        )

        self.carregar_em_thread(
            funcao_segundo_plano=requisicao,
            tela_loading=tela_carregando,
            abrir_tela= True,
            voltar_tela=True,
            quando_terminar=acao,
            atualizar=atualizar_tela
        )

class WidgetHelper(QWidget):
    @staticmethod
    def lista_grid():
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        vbox = QVBoxLayout(conteudo)

        grid = QGridLayout()
        vbox.addLayout(grid)
        vbox.addStretch()
        scroll.setWidget(conteudo)

        return scroll, grid

    @staticmethod
    def label_preco(preco_label, aligment=Qt.AlignmentFlag.AlignCenter, tamanho=30):
        preco_label = QLabel(f"<span style='font-size: {tamanho}px; color: green'>R$ {preco_label}</span>")
        preco_label.setAlignment(aligment)
        return preco_label

    @staticmethod
    def label_b(label, aligment=Qt.AlignmentFlag.AlignCenter):
        label_b = QLabel(f"<b>{label}</b>")
        label_b.setAlignment(aligment)
        return label_b
    
    @staticmethod
    def label_span(label, tamanho, aligment=Qt.AlignmentFlag.AlignCenter):
        label_span = QLabel(f"<span style='font-size: {tamanho}px'>{label}</span>")
        label_span.setAlignment(aligment)
        return label_span

    @staticmethod
    def bloco(largura, altura):
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
        return bloco

    @staticmethod
    def imagem(imagem, pasta="uploads/", scaled=200, pixmap=False):
        imagem_label = QLabel()
        caminho = Utils.caminho_imagem(pasta + imagem)

        # Carrega a imagem original
        original_pixmap = QPixmap(caminho)

        # Redimensiona mantendo a proporção, sem ultrapassar o tamanho definido
        imagem_redimensionada = original_pixmap.scaled(
            scaled, scaled,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Cria um pixmap quadrado branco com o tamanho total desejado
        base_pixmap = QPixmap(scaled, scaled)
        base_pixmap.fill(Qt.GlobalColor.transparent)

        # Desenha a imagem redimensionada no centro da base
        painter = QPainter(base_pixmap)
        x = (scaled - imagem_redimensionada.width()) // 2
        y = (scaled - imagem_redimensionada.height()) // 2
        painter.drawPixmap(x, y, imagem_redimensionada)
        painter.end()

        # Define o pixmap final no label
        imagem_label.setPixmap(base_pixmap)
        imagem_label.setFixedSize(scaled, scaled)
        imagem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if pixmap:
            return imagem_label.pixmap()
        return imagem_label

    @staticmethod
    def mostrar_alerta_temporario(
        parent_widget, mensagem, duracao_ms=3000,
        largura=400, altura=50, fonte=20,
        paddingH=20, paddingV=20,
        fontcolor='white', backcolor='#0078d7',
        border='#000000',
        posicao='inferior_direita'  # <-- novo parâmetro
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

        # Calcula a posição com base na string
        parent_pos = parent_widget.mapToGlobal(parent_widget.rect().topLeft())
        x = y = 0

        if 'direita' in posicao:
            x = parent_pos.x() + parent_widget.width() - largura - paddingH
        elif 'esquerda' in posicao:
            x = parent_pos.x() + paddingH

        if 'superior' in posicao:
            y = parent_pos.y() + paddingV
        elif 'inferior' in posicao:
            y = parent_pos.y() + parent_widget.height() - altura - paddingV

        alerta.move(x, y)
        alerta.show()

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
    def abrir_dialogo_arquivo(parent):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(
            parent,
            "Escolher arquivo",
            "",
            "Imagens (*.png *.jpg *.jpeg)"
        )
        if caminho_arquivo:
            # Caminho de destino onde o arquivo será salvo (pode mudar para o que quiser)
            nome_arquivo = os.path.basename(caminho_arquivo)
            destino = os.path.join("uploads", nome_arquivo)

            # Cria a pasta "uploads" se ela não existir
            os.makedirs("uploads", exist_ok=True)

            # Copia o arquivo para a pasta destino
            shutil.copy(caminho_arquivo, destino)
            return nome_arquivo

class ViewHelper(QWidget):
    funcoes_telas = []

    def __init__(self):
        pass

    def set_tela(self, stack, index):
        total = stack.count()

        # Converte índice negativo em positivo
        if index < 0:
            index = total + index

        if index < 0 or index >= total:
            return

        # Chama novamente a função para obter a tela atualizada
        funcao_criadora = self.__class__.funcoes_telas[index]
        self.sobrescrever_tela(stack, funcao_criadora, index)

        # Remove widgets e funções após o índice atual
        for i in range(len(self.__class__.funcoes_telas) - 1, index, -1):
            if i < stack.count():
                self.excluir_tela(stack, i, excluir_funcao=True)
            else:
                # Só remove da lista de funções, caso não exista mais o widget
                del self.__class__.funcoes_telas[i]

    def voltar_tela(self, stack, excluir_funcao = True, atualizar_tela=True):
        index = stack.currentIndex()
        stack.setCurrentIndex(index - 1)
        self.excluir_tela(stack, index, excluir_funcao)
        if atualizar_tela:
            self.atualiza_tela(stack)

    def abrir_tela(self, stack, funcao_criadora, excluir_anterior=False, salvar_tela=True):
        tela = funcao_criadora()
        if not tela:
            return None
        
        if salvar_tela:
            self.__class__.funcoes_telas.append(funcao_criadora)

        if excluir_anterior:
            index = stack.currentIndex()
            self.excluir_tela(stack, index, excluir_funcao=False)

        stack.addWidget(tela)
        stack.setCurrentWidget(tela)

    def excluir_tela(self, stack, index, excluir_funcao = True):
        widget = stack.widget(index)
        stack.removeWidget(widget)
        widget.deleteLater()
        if excluir_funcao:
            del self.__class__.funcoes_telas[index]

    def sobrescrever_tela(self, stack, funcao_criadora: QWidget, index: int = None):
        if index is None:
            index = stack.currentIndex()

        if 0 <= index < stack.count():
            self.excluir_tela(stack, index, excluir_funcao=False)
            tela = funcao_criadora()
            stack.insertWidget(index, tela)
            stack.setCurrentIndex(index)
            if index < len(self.__class__.funcoes_telas):
                self.__class__.funcoes_telas[index] = funcao_criadora
            else:
                self.__class__.funcoes_telas.insert(index, funcao_criadora)

    def atualiza_tela(self, stack):
        index = stack.currentIndex()
        funcao_criadora = self.__class__.funcoes_telas[index]
        self.sobrescrever_tela(stack, funcao_criadora, index)

    @staticmethod
    def tela_carregando_com_spinner(mensagem="Carregando...", gif_path="spinner.gif"):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner animado
        spinner = QLabel()
        movie = QMovie(Utils.caminho_imagem(gif_path))
        spinner.setMovie(movie)
        movie.start()

        # Mensagem opcional
        texto = QLabel(f"<span style='font-size: 20px'>{mensagem}</span>")
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(spinner)
        layout.addWidget(texto)

        return tela

    @staticmethod
    def tela_carregando(mensagem="Carregando..."):
        tela = QWidget()
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"<span style='font-size: 24px'>{mensagem}</span>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        return tela

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
        
        pixmap = QPixmap(
            Utils.caminho_imagem(
                f"uploads/{self.imagens[self.index]}"
            )
        )
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