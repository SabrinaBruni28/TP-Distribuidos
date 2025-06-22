import uuid

# Algumas operações que o servidor usa. Estão aqui separadas para maior universalismo
# e para melhor organização.

def gerarID():
    return str(uuid.uuid4())

def RetornaCorretamenteOuFalse(funcao):
    """
    Esse wraper aqui é equivalente a ficar usando
        try:
            função
        exception:
            return False

    Fiz para a fachada ali ficar mais limpa.
    """
    def wrapper(*args, **kwargs):
        try:
            print("\n================================================= Nova invocação =================================================")
            return funcao(*args, **kwargs)
        except Exception as e:
            print(f"[Servidor] Erro em {funcao.__name__}: {e}")
            return False
    return wrapper