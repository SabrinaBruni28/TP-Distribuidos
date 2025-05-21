from models.dao.dao import DAO
from models.endereco import Endereco

class DAOEndereco(DAO):
    def __init__(self):
        super().__init__(
            ['endereco'],
            ["id_usuario", "rua_endereco", "numero_endereco", "bairro_endereco", "cidade_endereco", "estado_endereco", "complemento_endereco"]
            )
    
    def _from_tuple(self, tupla = (0, 0, "", "", "", "", "", "")):
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

    def delete(self, id_obj: int):
        return super().delete(id_obj)
    
    def zerar(self, obj: Endereco):
        return self._from_tuple(super().zerar(obj, ['id_usuario']))