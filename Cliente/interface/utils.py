import sys, os
CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(CAMINHO_BASE)

from pybrcode.pix import generate_simple_pix
import re, uuid, unicodedata

class Utils:
    @staticmethod
    def cria_pasta(path):
        nova_pasta = os.path.join(CAMINHO_BASE, path)
        os.makedirs(nova_pasta, exist_ok=True)

    @staticmethod
    def caminho_imagem(path):
        return os.path.join(CAMINHO_BASE, path)

    @staticmethod
    def image_to_byte(image_path: str):
        caminho = Utils.caminho_imagem(image_path)
        with open(caminho, 'rb') as f:
            data = f.read()
        return data

    @staticmethod
    def byte_to_image(image_bytes, path='received_image.png'):
        caminho = Utils.caminho_imagem(path)
        with open(caminho, 'wb') as f:
            f.write(image_bytes)
        return path
    
    @staticmethod
    def check_cpf(cpf: str) -> bool:
        """
        Valida um número de CPF (Cadastro de Pessoa Física) com máscara.

        Parâmetros:
        - cpf: string COM máscara (ex: '123.456.789-09')

        Retorna:
        - True se o CPF for válido, False caso contrário.
        """
        # Verifica se o CPF está no formato XXX.XXX.XXX-XX
        if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
            return False

        # Remove pontos e traço para validação
        cpf_numeros = re.sub(r'\D', '', cpf)

        if len(cpf_numeros) != 11 or cpf_numeros == cpf_numeros[0] * 11:
            return False

        def calc_digit(digs):
            s = sum(int(d) * i for d, i in zip(digs, range(len(digs) + 1, 1, -1)))
            r = 11 - s % 11
            return '0' if r > 9 else str(r)

        d1 = calc_digit(cpf_numeros[:9])
        d2 = calc_digit(cpf_numeros[:9] + d1)
        return cpf_numeros.endswith(d1 + d2)
    
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
        nome = nome.strip()[:25]
        cidade = cidade.strip()[:15]
        chave = chave.strip()
        descricao = descricao.strip()[:40]
        valor = float(valor)
        
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
    def validar_chave_pix(chave: str) -> bool:
        chave = chave.strip()

        # CPF: 11 dígitos numéricos
        if re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", chave):
            return True

        # CNPJ: 14 dígitos numéricos
        if re.fullmatch(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", chave):
            return True

        # Email: verificação básica
        if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", chave):
            return True

        # Telefone no formato E.164 (ex: (##) ####-#### / (##) #####-####)
        if re.fullmatch(r"\(\d{2}\) \d{4,5}-\d{4}", chave):
            return True

        # Chave aleatória (UUID v4)
        try:
            uuid_obj = uuid.UUID(chave, version=4)
            return str(uuid_obj) == chave.lower()
        except ValueError:
            pass

        return False

    @staticmethod
    def excluir_arquivos_pasta(caminho_pasta):
        # Caminho absoluto da pasta que você quer limpar
        caminho_pasta = os.path.join(CAMINHO_BASE, caminho_pasta)

        # Remove arquivos
        for arquivo in os.listdir(caminho_pasta):
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)

    @staticmethod
    def normalizar_chave(chave: str) -> str:
        """
        Normaliza a string:
        - Converte para minúsculas
        - Remove acentos
        - Substitui espaços por underscores
        """
        # Remove acentos
        chave_sem_acento = unicodedata.normalize('NFKD', chave)
        chave_sem_acento = ''.join(c for c in chave_sem_acento if not unicodedata.combining(c))

        # Substitui espaços por underscores e converte para minúsculas
        chave_normalizada = re.sub(r"\s+", "_", chave_sem_acento).lower()

        return chave_normalizada
