import inspect

class ValidationUtils:
    def criar_dict_de_atributos(obj, atributos: list):
        return {attr: getattr(obj, attr, None) for attr in atributos}



