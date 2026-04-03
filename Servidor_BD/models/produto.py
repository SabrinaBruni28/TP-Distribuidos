from models.persistivel import Persistivel

class Produto(Persistivel):
    def __init__(self, id = 0, nome = '', descricao = '', imagens = [], loja = None):
        # Atributos próprios
        self.id = id
        self.nome = nome
        self.descricao = descricao

        # Atributos estrangeiros
        self.imagens = imagens
        self.loja = loja
        self.id_loja = loja.id if loja else 0

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'imagens': self.imagens,
            'loja': self.loja.to_dict_personalisado() if self.loja else '',
        }
    
    def to_dict_personalisado(self):
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'imagens': self.imagens,
            'loja': {"id": f"{self.loja.id if self.loja else ''}"},
        }
    
    def to_dict_bd(self, nome_colunas):
        obj_bd = {}
        atributos_bd = ('id_loja', 'nome', 'descricao')
        for attr, nome_coluna in zip(atributos_bd, nome_colunas):
            valor = getattr(self, attr, None)
            if valor:
                obj_bd[nome_coluna] = valor
        return obj_bd
    
    def clone_zerado(self):
        return Produto()

    @classmethod
    def from_dict(cls, dados) -> 'Produto':
        from models.loja import Loja
        print(type(dados), dados)
        id = dados.get('id', 0)
        nome = dados.get('nome', '')
        descricao = dados.get('descricao', '')
        imagens = dados.get('imagens', [])
        print('here')
        loja = Loja.from_dict(dados['loja']) if 'loja' in dados else None

        return cls(id, nome, descricao, imagens, loja)
    

    def __str__(self):
        return f'Produto(id={self.id}, nome={self.nome}, descricao={self.descricao}, imagens={self.imagens}, loja={self.loja.__str__()})'