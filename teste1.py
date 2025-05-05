from models.validation_utils import ValidationUtils as vu
from models.loja import Loja
from models.produto import Produto
from models.anuncio import Anuncio

anuncio = Anuncio(
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
    )

print(anuncio.to_dict())

print(vu.criar_dict_de_atributos(
    anuncio, 
    ["preco", "quantidade_disponivel", "pausado"]
))
