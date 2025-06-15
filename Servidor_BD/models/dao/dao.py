import os
import sys
import sqlite3
from models.persistivel import Persistivel

class DAO():
    def __init__(self, nome_tabelas: list, nome_colunas: list):
        self.db_path = './db/caldeirao.db'
        self.nome_tabelas = nome_tabelas
        self.nome_colunas = nome_colunas
        self.chaves_estrangeiras = [coluna for coluna in nome_colunas if coluna[:3] == 'id_']

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
            sql = f'''INSERT INTO {self.nome_tabelas[0]}
            ({', '.join(persistivel.keys())})
            VALUES ({', '.join(['?'] * len(persistivel.values()))})
            RETURNING id_{self.nome_tabelas[0]};'''
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
                persistivel[f'id_{self.nome_tabelas[0]}'] = obj.id
            print(persistivel, bool(persistivel))
            logic = ' '+logic+' '
            sql = f'''SELECT * FROM {' NATURAL JOIN '.join(self.nome_tabelas)}
            {' WHERE ' if persistivel else ''}
            {logic.join([f'{column} = ?' for column in persistivel.keys()])};'''
            print(sql, end='\n\n')
            cursor.execute(sql, tuple(persistivel.values()) )
            return cursor.fetchall()

    def update(self, obj: Persistivel):
        with self._connect() as conn:
            cursor = conn.cursor()
            persistivel = obj.to_dict_bd(self.nome_colunas)

            sql = f'''UPDATE {self.nome_tabelas[0]} SET
            {', '.join([f'{column} = ?' for column in persistivel.keys()])}
            WHERE id_{self.nome_tabelas[0]} = ?
            RETURNING *;'''
            print(sql, end='\n\n')
            cursor.execute(sql, list(persistivel.values())+[obj.id])
            persistivel = cursor.fetchone()
            conn.commit()
            return persistivel
    
    def delete(self, id_obj: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = f'DELETE FROM {self.nome_tabelas[0]} WHERE id_{self.nome_tabelas[0]} = ?;'
            print(sql, end='\n\n')
            cursor.execute(sql, (id_obj,))
            conn.commit()
            return True
    
    def forget(self, obj: Persistivel):
        with self._connect() as conn:
            cursor = conn.cursor()
            persistivel = obj.to_dict_bd(self.nome_colunas)

            sql = f'''UPDATE {self.nome_tabelas[0]} SET
            {', '.join([f'{fk} = NULL' for fk in self.chaves_estrangeiras])}
            WHERE id_{self.nome_tabelas[0]} = ?
            RETURNING id_{self.nome_tabelas[0]}, {', '.join(self.nome_colunas)};'''
            print(sql, end='\n\n')
            cursor.execute(sql, [obj.id])
            persistivel = cursor.fetchone()
            conn.commit()
            return persistivel