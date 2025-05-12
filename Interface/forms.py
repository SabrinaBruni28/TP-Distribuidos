import sys, os
# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from widgets import WidgetHelper
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
            botao_adicionar = WidgetHelper.botao(
                nome="Adicionar",
                largura=100, altura=40, fonte=18
            )
            botao_adicionar.hide()

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

    def ativar_botao_adicionar(self, campo, acao=None):
        botao = self.botoes_adicionar[campo]
        if acao:
            botao.clicked.connect(acao)
        botao.show()

    def adicionar_opcao(self, campo, opcao="Nova opção"):
        combo = self.inputs[campo]
        combo.addItem(opcao)

    def obter_valores(self) -> dict:
        """
        Retorna os valores selecionados nos campos do formulário de opções.
        """
        valores = {}
        for nome, combo in self.inputs.items():
            valores[str(nome).lower()] = combo.currentText()
        return valores

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
        for chave, valor in valores.items():
            if chave in self.inputs:
                if isinstance(valor, bool):
                    texto = "sim" if valor else "não"
                else:
                    texto = str(valor)
                self.inputs[chave].setText(texto)
                self.inputs[chave].setCursorPosition(0)  # <-- move o cursor para o início

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
                if texto.lower() not in ["sim", "não", "nao"]:
                    erro = "Digite 'Sim' ou 'Não'."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                self.erros[nome].setText(str(""))

            if nome.lower() == "email":
                if not WidgetHelper.check_email(texto):
                    erro = "Email inválido."
                    self.erros[nome].setText(str(erro))
                    has_error = True
                    continue
                else:
                    self.erros[nome].setText(str(""))

            elif nome.lower() == "cpf":
                if not WidgetHelper.check_cpf(texto):
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

    def definir_erros_especificos(self, erros: dict):
        """
        Atribui mensagens de erro específicas para os campos.

        :param erros: dicionário no formato {"Nome": "Erro em nome", "Email": "Erro em email", ...}
        """
        for nome, mensagem in erros.items():
            if nome in self.erros:
                self.erros[nome].setText(mensagem)
                self.erros[nome].setVisible(bool(mensagem))

    def obter_valores(self) -> dict:
        """
        Retorna os valores digitados nos campos do formulário.
        """
        valores = {}
        for nome, campo in self.inputs.items():
            valores[str(nome).lower()] = campo.text().strip()
        return valores
    
    def obter_valores_alterados(self, valores_iniciais: dict) -> dict:
        """
        Compara os valores atuais do formulário com os valores iniciais fornecidos e retorna
        um dicionário contendo apenas os campos que foram alterados.
        
        :param valores_iniciais: Dicionário com os valores iniciais, por exemplo:
                                  {"Nome": "Ana", "Email": "ana@email.com"}
        :return: Dicionário contendo os campos alterados, por exemplo:
                 {"Nome": "Maria"}
        """
        valores_alterados = {}
        for nome, entrada in self.inputs.items():
            valor_atual = entrada.text().strip()
            valor_inicial = str(valores_iniciais.get(nome, "")).strip()

            if valor_atual.lower() in ["sim", "não", "nao"]:
                if valor_atual == 'sim':
                    valor_comp = True
                else:
                    valor_comp = False
            else:
                valor_comp = valor_atual

            # Se o valor atual for diferente do inicial, armazene no dicionário
            if valor_comp != valor_inicial:
                valores_alterados[str(nome).lower()] = valor_atual
        
        return valores_alterados
    
    def bloquear_campos(self, nomes_campos: list):
        """
        Torna os campos especificados como não editáveis.
        
        :param nomes_campos: Lista de nomes dos campos (como definidos na criação do formulário)
        """
        for nome_campo in nomes_campos:
            if nome_campo in self.inputs:
                self.inputs[nome_campo].setReadOnly(True) # Impede edição
                self.inputs[nome_campo].setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Impede que o campo receba foco para digitar
            

