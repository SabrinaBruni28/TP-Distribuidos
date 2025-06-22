from models.dao.dao import DAO
from models.endereco import Endereco

class DAOEndereco(DAO):
    def __init__(self,
            nome_tabelas: list = ['endereco'],
            nome_colunas: list = ['id_usuario', 'rua_endereco', 'numero_endereco', 'bairro_endereco', 'cidade_endereco', 'estado_endereco', 'complemento_endereco']):
        
        super().__init__(nome_tabelas, nome_colunas)
    
    def _from_tuple(self, tupla = (0, 0, '', '', '', '', '', '')):
        return Endereco(
            id = tupla[0],
            id_usuario = tupla[1],
            rua = tupla[2],
            numero = tupla[3],
            bairro = tupla[4],
            cidade = tupla[5],
            estado = tupla[6],
            complemento = tupla[7])

    def insert(self, obj: Endereco):
        return super().insert(obj)

    def select(self, obj: Endereco, logic = 'OR'):
        return [self._from_tuple(tupla) for tupla in super().select(obj, logic)]

    def update(self, obj: Endereco):
        return self._from_tuple(super().update(obj))

    def delete(self, obj: Endereco):
        return super().delete(obj)
    
    def forget(self, obj: Endereco):
        return self._from_tuple(super().forget(obj))