import sys, os
CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(CAMINHO_BASE)

from pybrcode.pix import generate_simple_pix
import re

class Utils:
    @staticmethod
    def cria_pasta(path):
        nova_pasta = os.path.join(CAMINHO_BASE, path)
        os.makedirs(nova_pasta, exist_ok=True)

    @staticmethod
    def caminho_imagem(path):
        return os.path.join(CAMINHO_BASE, path)

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
    def excluir_arquivos_pasta(caminho_pasta):
        for arquivo in os.listdir(caminho_pasta):
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)