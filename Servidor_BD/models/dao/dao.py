import os
import sys
import sqlite3
from models.persistivel import Persistivel
# Adiciona o diretório raiz ao sys.path
#CAMINHO_BASE_BANCO = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
#sys.path.append(CAMINHO_BASE_BANCO)

class DAO():
    def __init__(self, table_names: list, nome_colunas: list):
        #self.db_path = os.path.join(CAMINHO_BASE_BANCO, 'db/caldeirao.db')
        self.db_path = './db/caldeirao.db'
        self.table_names = table_names
        self.nome_colunas = nome_colunas

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def _from_tuple(self, tupla: tuple):
        pass

    def insert(self, obj: Persistivel):
        with self._connect() as conn:
            cursor = conn.cursor()
            print(obj.to_dict())
            persistivel = obj.to_dict_bd(self.nome_colunas)
            print(persistivel)
            sql = f'''INSERT INTO {self.table_names[0]}
            ({', '.join(persistivel.keys())})
            VALUES ({', '.join(['?'] * len(persistivel.values()))})
            RETURNING id_{self.table_names[0]};'''
            print(sql, end='\n\n')
            cursor.execute(sql, tuple(persistivel.values()))
            id_persistivel = cursor.fetchone()[0]
            conn.commit()
            return id_persistivel

    def select(self, obj: Persistivel, logic = 'OR'):
        with self._connect() as conn:
            cursor = conn.cursor()
            persistivel = obj.to_dict_bd(self.nome_colunas)
            if obj.id:
                persistivel[f'id_{self.table_names[0]}'] = obj.id
            print(persistivel, bool(persistivel))
            logic = ' '+logic+' '
            sql = f'''SELECT * FROM {self.table_names[0]}
            {' WHERE ' if persistivel else ''}
            {logic.join([f'{column} = ?' for column in persistivel.keys()])};'''
            print(sql, end='\n\n')
            cursor.execute(sql, tuple(persistivel.values()) )
            return cursor.fetchall()

    def update(self, obj: Persistivel):
        with self._connect() as conn:
            cursor = conn.cursor()
            persistivel = obj.to_dict_bd(self.nome_colunas)

            sql = f'''UPDATE {self.table_names[0]} SET
            {', '.join([f'{column} = ?' for column in persistivel.keys()])}
            WHERE id_{self.table_names[0]} = ?
            RETURNING id_{self.table_names[0]}, {', '.join(self.nome_colunas)};'''
            print(sql, end='\n\n')
            cursor.execute(sql, list(persistivel.values())+[obj.id])
            persistivel = cursor.fetchone()
            conn.commit()
            return persistivel
    
    def delete(self, id_obj: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = f'DELETE FROM {self.table_names[0]} WHERE id_{self.table_names[0]} = ?;'
            print(sql, end='\n\n')
            cursor.execute(sql, (id_obj,))
            conn.commit()
            return 'ok'