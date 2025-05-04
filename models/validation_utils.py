import json

class ValidationUtils:
    @staticmethod
    def objeto_para_json(objeto):
        """
        Converte uma instância de classe para uma string JSON.
        """
        return json.dumps(objeto.__dict__, indent=4, ensure_ascii=False)

    @staticmethod
    def json_para_objeto(json_texto, classe):
        """
        Converte um JSON (em string) para uma instância da classe fornecida.
        A classe deve aceitar os atributos como argumentos no construtor.
        """
        dados = json.loads(json_texto)
        return classe(**dados)
