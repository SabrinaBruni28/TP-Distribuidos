import re
from pybrcode.pix import generate_simple_pix
import base64

class ValidationUtils:
    @staticmethod
    def check_cpf(cpf: str) -> bool:
        """Verifica se um CPF é válido"""
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

        if salvar_svg:
            pix.imageToPath(destDir="../", filename=nome_arquivo, svg=True)

        if salvar_png:
            pix.imageToPath(destDir="../", filename=nome_arquivo, svg=False)

        return {
            "payload": str(pix),
            "base64_png": pix.toBase64(),
            "svg_string": pix.toSVG()
        }

    @staticmethod
    def strings_equal(str1: str, str2: str, case_sensitive: bool = True) -> bool:
        """Compara se duas strings são iguais, com opção de ignorar caixa"""
        if not case_sensitive:
            return str1.lower() == str2.lower()
        return str1 == str2

if __name__ == "__main__":
    # Testando a validação de CPF
    cpf = ""
    print(f"CPF {cpf} é válido? {ValidationUtils.check_cpf(cpf)}")

    # Testando a geração de código Pix
    dados = ValidationUtils.gerar_qrcode_pix(
        nome="",
        chave="",
        cidade="Florestal",
        valor=12.50,
        descricao="Pagamento do almoço",
        pagamento_multiplo=False,
        nome_arquivo="qrcode_sabrina",
        salvar_png = True,
        salvar_svg = False
    )

    print("Payload Pix:")
    print(dados["payload"])

    # Testando comparação de strings
    str1 = "Hello"
    str2 = "hello"
    print(f"As strings '{str1}' e '{str2}' são iguais? {ValidationUtils.strings_equal(str1, str2, case_sensitive=False)}")