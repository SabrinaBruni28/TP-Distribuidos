import sys, os, shutil
# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.loja import Loja
from models.anuncio import Anuncio
from models.produto import Produto
from models.usuario import Usuario_Identificado
from models.cliente import UnixSocketClient
from models.endereco import Endereco
from forms import Formulario, FormularioOpcoes
from widgets import CarrosselImagem, WidgetHelper, CaixaConfirmacao
from models.pedido import Pedido
from main import Main

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import (
   QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QFileDialog,QFormLayout, QSpacerItem, QSizePolicy, QDialog,
   QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QFrame, QStackedWidget, QPushButton, QComboBox, QMessageBox
)

class MarketplaceUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caldeirão")
        self.setGeometry(100, 100, 1000, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main = Main()
        self.main.visualizar_anuncios()
        self.stack.addWidget(self.tela_inicial())

    def closeEvent(self, event):
        dialogo = CaixaConfirmacao(self, titulo="Confirmar saída", mensagem="Você tem certeza que deseja sair?")
        resposta = dialogo.exec()

        if resposta == QDialog.DialogCode.Accepted:
            self.main.socket.close()
            event.accept()
        else:
            event.ignore()

    def voltar_para_lista(self):
        self.abrir_tela(self.tela_anterior)

    def abrir_tela(self, nova_tela):
        self.tela_anterior = self.stack.currentWidget()
        # Remove todas as telas antigas
        while self.stack.count() > 2:
            widget = self.stack.widget(0)
            if widget != self.tela_anterior:
                self.stack.removeWidget(widget)
                widget.deleteLater()  # libera memória corretamente

        # Adiciona a nova tela
        self.stack.addWidget(nova_tela)
        self.stack.setCurrentWidget(nova_tela)

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
        self.atualizar_lista_anuncios(self.main.anuncios)

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
        valores = formularioOp.obter_valores()
        pedido = Pedido(
            produto=anuncio.produto, 
            quantidade=int(valores["quantidade"]),
            preco=anuncio.preco,
            endereco=self.main.usuario.get_endereco(valores["endereço"])
        )
        self.abrir_tela(self.tela_pagamento(anuncio))
        if self.main.criar_pedido(pedido):
            anuncio.subtrair_quantidade(1)


    def criar_loja(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Nome": str}
        )

        if erro:
            formulario.exibir_erros()
        else:
            loja = Loja(formulario.obter_valores())
            resposta = self.main.criar_loja(loja)
            
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=400, altura=50,padding=50,
                    mensagem="Loja Criada com Sucesso!"
                )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=300, altura=50,padding=50,
                    mensagem="Erro ao criar endereço!"
                )

    def criar_endereco(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            endereco = Endereco(formulario.obter_valores())
            resposta = self.main.criar_endereco(endereco)

            if isinstance(resposta, dict):
                capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                formulario.definir_erros_especificos(capitalizado)
                formulario.exibir_erros()
            
            elif resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=400, altura=50,padding=50,
                    mensagem="Endereço Criado com Sucesso!"
                )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=300, altura=50,padding=50,
                    mensagem="Erro ao criar endereço!"
                )

    def editar_loja(self, formulario: Formulario, loja: Loja):
        erro =  formulario.validar_tipos(
            {
                "Nome": str
            }
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Nome": loja.nome, 
                    "Imagem": loja.imagem
                }
            )
            if valores_alterados:
                resposta = self.main.editar_loja(loja, valores_alterados)
                
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,padding=50,
                        mensagem="Loja Editada com Sucesso!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#f44336",
                        largura=300, altura=50,padding=50,
                        mensagem="Erro ao editar loja!"
                    )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#FFC107", fontcolor="#000000",
                        largura=300, altura=50,padding=50,
                        mensagem="Nenhuma alteração realizada"
                    )

    def editar_endereco(self, formulario: Formulario, endereco: Endereco):
        erro = formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Rua": endereco.rua, 
                    "N°": endereco.numero, 
                    "Bairro": endereco.bairro, 
                    "Cidade": endereco.cidade, 
                    "Estado": endereco.estado, 
                    "Complemento": endereco.complemento
                }
            )
            if valores_alterados:
                resposta = self.main.editar_endereco(endereco, valores_alterados)
                
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,padding=50,
                        mensagem="Endereco Editado com Sucesso!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#f44336",
                        largura=300, altura=50,padding=50,
                        mensagem="Erro ao editar dados!"
                    )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#FFC107", fontcolor="#000000",
                        largura=300, altura=50,padding=50,
                        mensagem="Nenhuma alteração realizada"
                    )
    
    def editar_perfil(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Nome": str, "CPF": str, "Email": str, "Senha": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            usuario = self.main.usuario
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Nome": usuario.nome, 
                    "CPF": usuario.cpf, 
                    "Email": usuario.email,
                    "Senha": "*"*len(usuario.senha),
                }
            )
            if valores_alterados:
                resposta = self.main.editar_usuario(valores_alterados)

                if isinstance(resposta, dict):
                    capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                    formulario.definir_erros_especificos(capitalizado)
                    formulario.exibir_erros()
                
                elif resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#4CAF50",
                        largura=300, altura=50,padding=50,
                        mensagem="Perfil Editado com Sucesso!"
                    )
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#f44336",
                        largura=300, altura=50,padding=50,
                        mensagem="Erro ao editar dados!"
                    )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self, 
                        backcolor="#FFC107", fontcolor="#000000",
                        largura=300, altura=50,padding=50,
                        mensagem="Nenhuma alteração realizada"
                    )
                
    def excluir_loja(self, loja: Loja):
        dialogo = CaixaConfirmacao(self, titulo="Confirmar excluir loja", mensagem=f"Você tem certeza que deseja excluir loja {loja.nome}?")
        resposta = dialogo.exec()

        if resposta == QDialog.DialogCode.Accepted:
            resposta = self.main.excluir_loja(loja)
            if resposta:
                 WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=300, altura=50,padding=920,
                    mensagem="Loja Excluída com Sucesso!"
                )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=300, altura=50,padding=920,
                    mensagem="Erro ao excluir loja!"
                )
        else:
            dialogo.close()
    
    def cancelar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(self, titulo="Confirmar cancelamento", mensagem=f"Você tem certeza que deseja cancelar pedido {pedido.id}?")
        resposta = dialogo.exec()

        if resposta == QDialog.DialogCode.Accepted:
            resposta = self.main.cancelar_pedido(pedido, pedido.produto.loja)
            if resposta:
                 WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=400, altura=50,paddingV=400, paddingH=950,
                    mensagem="Pedido Cancelado com Sucesso!"
                )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=300, altura=50,paddingV=400, paddingH=950,
                    mensagem="Erro ao cancelar pedido!"
                )
        else:
            dialogo.close()

    def confirmar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(self, titulo="Confirmar", mensagem=f"Você tem certeza que deseja confirmar pedido {pedido.id}?")
        resposta = dialogo.exec()

        if resposta == QDialog.DialogCode.Accepted:
            resposta = self.main.confirmar_pedido(pedido, pedido.produto.loja)
            if resposta:
                 WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=400, altura=50,paddingV=400, paddingH=50,
                    mensagem="Pedido Confirmado com Sucesso!"
                )
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=300, altura=50,paddingV=400, paddingH=50,
                    mensagem="Erro ao confirmar pedido!"
                )
        else:
            dialogo.close()
    
    def confirmar_codigo(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Código": int}
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores = formulario.obter_valores()
            resposta, mensagem = self.main.email_confirmacao(valores)
            
            if resposta:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#4CAF50",
                    largura=400, altura=50,paddingH=20, paddingV=20,
                    mensagem="Cadastro realizado com Sucesso!"
                )

            elif mensagem == "codigo_invalido":
                formulario.definir_erros_especificos(
                    {
                        "Código": "Código de confirmação inválido"
                    }
                )
                formulario.exibir_erros()

            elif mensagem == "limite_excedido":
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self, 
                    backcolor="#f44336",
                    largura=400, altura=50,padding=50,
                    mensagem="Limite de tentativas excedido!"
                )
                self.abrir_tela(self.tela_cadastro())

    def cadastrar(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {
                "Nome": str, 
                "CPF": str, 
                "Email": str, 
                "Senha": str
            }
        )

        if erro:
            formulario.exibir_erros()
        else:
            usuario = Usuario_Identificado(formulario.obter_valores())
            resposta = self.main.cadastrar(usuario)

            if isinstance(resposta, dict):
                capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                formulario.definir_erros_especificos(capitalizado)
                formulario.exibir_erros()

            elif resposta:
                self.abrir_tela(self.tela_codigo_confirmacao())

    def login(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {
                "Email": str, 
                "Senha": str
            }
        )

        if erro:
            formulario.exibir_erros()
        else:
            usuario = Usuario_Identificado(formulario.obter_valores())
            resposta = self.main.login(usuario)

            if isinstance(resposta, dict):
                capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                formulario.definir_erros_especificos(capitalizado)
                formulario.exibir_erros()

            elif resposta:
                self.abrir_tela(self.tela_inicial())

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

        botao_perfil = WidgetHelper.botao(
            nome="Meu Perfil", 
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao= lambda: self.abrir_tela(self.tela_perfil())
        )

        botao_lojas = WidgetHelper.botao(
            nome="Minhas Lojas", 
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao= lambda: self.abrir_tela(self.tela_minhas_lojas())
        )

        botao_pedidos = WidgetHelper.botao(
            nome="Meus Pedidos", 
            backcolor="", hover="#3a3a3a", border="", pressed='#000000',
            largura=250, altura=100,
            acao= lambda: self.abrir_tela(self.tela_meus_pedidos())
        )
    
        # Adicionando os botões ao layout da barra lateral
        menu_layout.addWidget(botao_perfil, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_lojas, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addWidget(botao_pedidos, alignment=Qt.AlignmentFlag.AlignHCenter)
        menu_layout.addStretch()  # Adiciona um espaçador para empurrar os botões para cima

        return menu_lateral
    
    def criar_barra_superior(self):
        # Barra superior com botões
        barra_superior = QHBoxLayout()

        botao_menu = WidgetHelper.botao(
            nome="≡", fonte=40,
            largura=50, altura=50,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000',
            acao= self.toggle_menu
        )

        botao_login = WidgetHelper.botao(
            nome="Login", fonte=15,
            largura=100, altura=30,
            acao= lambda: self.abrir_tela(self.tela_login())
        )

        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Pesquisar produto...")
        self.input_busca.setFixedWidth(500)
        self.input_busca.setFixedHeight(40)
        self.input_busca.hide()

        self.botao_reset = WidgetHelper.botao(
            nome="❌", fonte=20,
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
            pressed='#000000',
            acao= lambda: self.main.visualizar_anuncios()
        )

        botao_selecionar_arquivo = WidgetHelper.botao(
            nome="Selecionar arquivo", fonte=10,
            largura=100, altura=30,
            backcolor="", hover="#3a3a3a", border="",
            pressed='#000000',
            acao= lambda: WidgetHelper.abrir_dialogo_arquivo(self)
        )

        if self.main.is_identificado():
            barra_superior.addWidget(botao_menu)
        else:
            barra_superior.addWidget(botao_login)

        barra_superior.addWidget(QLabel("<h2>Produtos disponíveis:</h2>"), alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(botao_selecionar_arquivo, alignment=Qt.AlignmentFlag.AlignLeft)
        barra_superior.addWidget(self.botao_reset)
        barra_superior.addWidget(self.input_busca)
        barra_superior.addWidget(btn_pesquisa)
        barra_superior.addWidget(btn_atualizar)

        return barra_superior

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

        botao_adicionar = WidgetHelper.botao(
            nome="+", fonte=80,
            largura=largura_bloco, altura=altura_bloco,
            backcolor='#e0f7fa', fontcolor='#0078d7',
            border='dashed #0078d7',
            hover='#b2ebf2', pressed='#80deea',
            acao=lambda: self.abrir_tela(self.tela_criar_produto())
        )

        index = 0
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
        self.menu_lateral = self.criar_menu_lateral()
        layout_h.addWidget(self.menu_lateral)
        
        # Layout vertical para o conteúdo da tela
        layout_conteudo = QVBoxLayout()

        barra_superior = self.criar_barra_superior()
        layout_conteudo.addLayout(barra_superior)

        tela_lista = self.tela_lista_anuncios(self.main.anuncios)
        layout_conteudo.addWidget(tela_lista)

        # Agora adiciona o conteúdo principal no layout horizontal
        layout_h.addLayout(layout_conteudo)

        return tela

    def tela_detalhes_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_loja = WidgetHelper.botao(
            nome="Loja", fonte=15,
            largura=100,
            acao=lambda: self.abrir_tela(self.tela_detalhes_loja(anuncio.produto.loja))
        )
        layout_horizontal.addWidget(botao_loja, alignment=Qt.AlignmentFlag.AlignRight)

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

        comprar = WidgetHelper.botao(
            nome="Comprar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.abrir_tela(self.tela_comprar(anuncio) if self.main.is_identificado() else self.tela_login())
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
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)

        if loja.imagem:
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_loja = WidgetHelper.botao(
            nome="Loja", fonte=15,
            acao=lambda: self.abrir_tela(self.tela_detalhes_loja(pedido.produto.loja))
        )
        if not confirmar:
            layout_horizontal.addWidget(botao_loja, alignment=Qt.AlignmentFlag.AlignRight)

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

        botao_cancelar = WidgetHelper.botao(
            nome="Cancelar",
            acao=lambda: self.cancelar_pedido(pedido)
        )

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar",
            acao=lambda: self.confirmar_pedido(pedido)
        )

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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

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

        layout_vertical.addWidget(formulario, alignment=Qt.AlignmentFlag.AlignHCenter)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.comprar(anuncio, formulario)
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela
    
    def tela_pagamento(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addLayout(layout_horizontal)
        layout_vertical.addSpacing(10)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Pagamento</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(20)

        dados = WidgetHelper.gerar_qrcode_pix(
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

        botao_copiar = WidgetHelper.botao(
            nome="Copiar texto", fonte=15,
            backcolor="", 
            hover='#D3D3D3', pressed='#000000',
            acao=WidgetHelper.copiar_texto(string)
        )
        layout_vertical.addWidget(botao_copiar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addSpacing(10)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=200, altura=50,
            acao=None
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela
    
    def tela_codigo_confirmacao(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(50)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Código de Confirmação</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Código"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.confirmar_codigo(formulario)
        )
        layout_vertical.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)

        return tela

    def tela_cadastro(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(50)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Cadastramento</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Nome", "CPF", "Email", "Senha"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_cadastrar = WidgetHelper.botao(
            nome="Cadastrar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.cadastrar(formulario)
        )
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_login = WidgetHelper.botao(
            nome="Login",
            acao=lambda: self.abrir_tela(self.tela_login())
        )
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignRight)

        return tela

    def tela_login(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        layout_vertical.addSpacing(50)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Login</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(50)

        formulario = Formulario(campos=["Email", "Senha"], largura=600, altura=50)
        layout_vertical.addWidget(formulario)

        botao_login = WidgetHelper.botao(
            nome="Entrar", fonte=30,
            largura=200, altura=50,
            acao=lambda: self.login(formulario)
        )
        layout_vertical.addWidget(botao_login, alignment=Qt.AlignmentFlag.AlignCenter)

        botao_cadastrar = WidgetHelper.botao(
            nome="Cadastrar",
            acao=lambda: self.abrir_tela(self.tela_cadastro())
        )
        layout_vertical.addWidget(botao_cadastrar, alignment=Qt.AlignmentFlag.AlignRight)

        return tela

    def tela_perfil(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar"
        )
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
        usuario = self.main.usuario
        formulario.preencher_campos(
            {"Nome": usuario.nome, "CPF": usuario.cpf, "Email": usuario.email, "Senha": "*"*len(usuario.senha)}
        )
        botao_editar.clicked.connect(lambda: self.editar_perfil(formulario))
        layout_conteudo.addWidget(formulario)
        layout_conteudo.addStretch()

        botao_endereco = WidgetHelper.botao(
            nome="Meus Endereços",
            largura=180, altura=50,
            acao=lambda: self.abrir_tela(self.tela_meus_enderecos())
        )
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
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
        usuario = self.main.usuario
        quantidade = len(usuario.enderecos)
        formulario = Formulario(
            campos=[f"Endereço{i+1}" for i in range(quantidade)],
            largura=800,
            altura=50
        )
        formulario.preencher_campos(
            {f"Endereço{i+1}": usuario.enderecos[i].__str__() for i in range(quantidade)}
        )
        formulario.bloquear_campos([f"Endereço{i+1}" for i in range(quantidade)])
        layout_horizontal2.addWidget(formulario)

        layout_vertical2 = QVBoxLayout()
       
        botao_editar = []
        for i in range(quantidade):
            endereco = usuario.enderecos[i]
            botao = WidgetHelper.botao(
                nome="Editar",
                acao=lambda: self.abrir_tela(self.tela_meu_endereco(endereco))
            )
            botao_editar.append(botao)
            layout_vertical2.addWidget(botao)

        layout_horizontal2.addLayout(layout_vertical2)
        layout_conteudo.addLayout(layout_horizontal2)

        botao_adicionar = WidgetHelper.botao(
                nome="Adicionar",
                acao=lambda: self.abrir_tela(self.tela_criar_endereco())
            )
        layout_conteudo.addStretch()
        layout_conteudo.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignLeft)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        return tela

    def tela_meu_endereco(self, endereco: Endereco):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar"
        )
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Endereço</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Rua", "N°", "Bairro", "Cidade", "Estado", "Complemento"],
            largura=600,
            altura=50
        )
        formulario.preencher_campos(
            {
                "Rua": endereco.rua, 
                "N°": endereco.numero, 
                "Bairro": endereco.bairro, 
                "Cidade": endereco.cidade, 
                "Estado": endereco.estado, 
                "Complemento": endereco.complemento
            }
        )
        botao_editar.clicked.connect(lambda: self.editar_endereco(formulario, endereco))
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar",
            acao=None
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
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
        botao_confirmar.clicked.connect(lambda: self.criar_endereco(formulario))
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizintal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_adicionar = WidgetHelper.botao(
            nome="Adicionar",
            acao=lambda: self.abrir_tela(self.tela_criar_loja())
        )
        layout_horizintal.addWidget(botao_adicionar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizintal)
        layout_vertical.addSpacing(40)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Minhas Lojas</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        conteudo_scroll = QWidget()
        layout_loja = QVBoxLayout(conteudo_scroll)
        layout_loja.setSpacing(15)

        blocos = self.tela_lista_lojas(self.main.usuario.lojas)
        layout_vertical.addWidget(blocos)
        layout_vertical.addStretch()

        return tela
    
    def tela_minha_loja(self, loja: Loja):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar",
            acao=lambda: self.abrir_tela(self.tela_loja(loja))
        )
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
            largura=220,
        )
        layout_horizontal2.addWidget(botao_pedidos_confirmados)

        botao_pedidos_em_andamento = WidgetHelper.botao(
            nome="Pedidos Em Andamento", fonte=18,
            largura=230
        )
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addLayout(layout_horizontal)

        botao_editar = WidgetHelper.botao(
            nome="Editar"
        )
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
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
        botao_editar.clicked.connect(lambda: self.editar_loja(formulario, loja))
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=lambda: self.excluir_loja(loja)
        )
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela

    def tela_criar_loja(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
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
        botao_confirmar.clicked.connect(lambda: self.criar_loja(formulario))
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar",
            acao=None
        )
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>{produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição", "Imagens"],
            largura=600,
            altura=50
        )

        formulario.preencher_campos( 
            {
                "Nome": produto.nome, 
                "Descrição": produto.descricao, 
                "Imagens": produto.imagens[0]
            }
        )
    
        formulario.validar_tipos(
            {
                "Nome": str, 
                "Descrição": str, 
                "Imagens": str
            }
        )
        layout_conteudo.addWidget(formulario)
        
        # Scroll area com o título e formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(conteudo_scroll)
        layout_vertical.addWidget(scroll_area)

        layout_horizontal_2 = QHBoxLayout()

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=None
        )
        layout_horizontal_2.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_criar = WidgetHelper.botao(
            nome="Criar Anúncio",
            largura=200,
            acao=lambda: self.abrir_tela(self.tela_criar_anuncio(produto))
        )
        layout_horizontal_2.addWidget(botao_criar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal_2)

        return tela
    
    def tela_anuncio(self, anuncio: Anuncio):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_editar = WidgetHelper.botao(
            nome="Editar",
            acao=None
        )
        layout_horizontal.addWidget(botao_editar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Anúncio: {anuncio.produto.nome}</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
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

        botao_excluir = WidgetHelper.botao(
            nome="Excluir",
            acao=None
        )
        layout_vertical.addWidget(botao_excluir, alignment=Qt.AlignmentFlag.AlignLeft)

        return tela
    
    def tela_criar_produto(self):
        tela = QWidget()
        layout_vertical = QVBoxLayout(tela)

        # Topo fixo (fora do scroll): botão voltar e editar
        layout_horizontal = QHBoxLayout()

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar",
            acao=None
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Produto</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_conteudo.addWidget(titulo)
        layout_conteudo.addSpacing(40)

        formulario = Formulario(
            campos=["Nome", "Descrição", "Imagens"],
            largura=600,
            altura=50
        )
    
        formulario.validar_tipos(
            {
                "Nome": str, 
                "Descrição": str, 
                "Imagens": str
            }
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
        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)

        botao_confirmar = WidgetHelper.botao(
            nome="Confirmar",
            acao=self.voltar_para_lista
        )
        layout_horizontal.addWidget(botao_confirmar, alignment=Qt.AlignmentFlag.AlignRight)
        layout_vertical.addLayout(layout_horizontal)

        # CONTEÚDO DO SCROLL
        conteudo_scroll = QWidget()
        layout_conteudo = QVBoxLayout(conteudo_scroll)
        layout_conteudo.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_conteudo.addSpacing(40)

        titulo = QLabel(f"<span style='font-size: 50px; font-weight: bold'>Criar Anúncio</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
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

        botao_voltar = WidgetHelper.botao(
            nome="Voltar",
            acao=self.voltar_para_lista
        )
        layout_vertical.addWidget(botao_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout_vertical.addSpacing(40)

        titulo = QLabel("<span style='font-size: 50px; font-weight: bold'>Meus Pedidos</span>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_vertical.addWidget(titulo)
        layout_vertical.addSpacing(40)

        blocos = self.tela_lista_pedidos(self.main.usuario.pedidos)
        layout_vertical.addWidget(blocos)

        return tela

if __name__ == "__main__":
   app = QApplication(sys.argv)
   window = MarketplaceUI()
   window.show()
   sys.exit(app.exec())
