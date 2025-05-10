import sys, os
# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.validation_utils import ValidationUtils as vu
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
   QWidget, QLabel, QLineEdit, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
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
