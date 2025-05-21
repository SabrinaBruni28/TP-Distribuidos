from models.dao.dao import DAO
from models.usuario import Usuario_Identificado

class DAOUsuario(DAO):
    def __init__(self):
        super().__init__(
            ['usuario'],
            ["cpf_usuario", "nome_usuario", "email_usuario", "senha_usuario"])
    
    def _from_tuple(self, tupla = (0, "", "", "", "")):
        return Usuario_Identificado(
            id = tupla[0],
            cpf = tupla[1],
            nome = tupla[2],
            email = tupla[3],
            senha = tupla[4])

    def insert(self, obj: Usuario_Identificado):
        return super().insert(obj)

    def select(self, obj: Usuario_Identificado, logic = 'OR'):
        return [self._from_tuple(tupla) for tupla in super().select(obj, logic)]
    
    def update(self, obj: Usuario_Identificado):
        return self._from_tuple(super().update(obj))

    def delete(self, id_obj: int):
        print('Operação inválida: Usuário não é capaz de se apagar')
        return ''
    
    def zerar(self, obj: Usuario_Identificado):
        pass

