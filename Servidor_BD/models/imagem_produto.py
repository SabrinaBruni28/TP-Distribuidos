from models.persistivel import Persistivel
from models.produto import Produto

class Imagem_Produto(Persistivel):
    def __init__(self, id = 0, id_produto = 0):
        # Atributos próprios
        self.id = id

        # Atributos estrangeiros
        self.id_produto = id_produto

    def to_dict(self):
        return {
            'id': self.id,
            'imagem': self.caminho()
        }
    
    def to_dict_personalisado(self):
        return {
            'imagem': self.caminho()
        }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ['id_produto']
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            print('montando todictbd:', attr, '=' ,valor)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd
    
    def clone_zerado(self):
        return Imagem_Produto()

    def caminho(self):
        return f'{self.id}_{self.id_produto}.jpg'
    
    @classmethod
    def from_dict(cls, dados):
        id = dados.get('id', 0)
        id_produto = int(dados.get('imagem', '').split('_')[2][:-4])
        
        return cls(id, id_produto)
    
    def __str__(self):
        return f'Imagem_Produto(id={self.id}, imagem={self.caminho()})'