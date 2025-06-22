import base64
import sys, os
CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(CAMINHO_BASE)

img_path = 'db/img'

def seExisteImagem(pasta: str, nomeImagem: str):
    caminho_imagem = os.path.join(CAMINHO_BASE, img_path, pasta, nomeImagem)
    return os.path.exists(caminho_imagem)

def obterImagem(pasta: str, nomeImagem: str):
    print(f'[ImageUtils][Obter] - Obtendo {nomeImagem} ...')
    caminho_imagem = os.path.join(CAMINHO_BASE, img_path, pasta, nomeImagem)
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, 'rb') as f:
            print(f'[ImageUtils][Obter] - Retornando {nomeImagem} ...')
            data = f.read()
        return base64.b64encode(data).decode('utf-8')
    else:
        print(f'[ImageUtils][Obter] - {nomeImagem} não encontrado!')
        return False

def salvarImagem(pasta: str, nomeImagem: str, imagem):
    print(f'[ImageUtils][Salvar] - Salvando {nomeImagem} ...')
    caminho_imagem = os.path.join(CAMINHO_BASE, img_path, pasta, nomeImagem)
    with open(caminho_imagem, 'wb') as f:
        f.write( base64.b64decode(imagem.encode('utf-8')))
    print(f'[ImageUtils][Salvar] - {nomeImagem} salvo!')

def apagarImagem(pasta: str, nomeImagem: str):
    print(f'[ImageUtils][Apagar] - Apagando {nomeImagem} ...')
    caminho_imagem = os.path.join(CAMINHO_BASE, img_path, pasta, nomeImagem)
    if os.path.exists(caminho_imagem):
        os.remove(caminho_imagem)
        print(f'[ImageUtils][Apagar] - {nomeImagem} removido!')
        return True
    else:
        print(f'[ImageUtils][Apagar] - {nomeImagem} não encontrado!')
        return False