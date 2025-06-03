import Pyro5.api

print("Iniciando cliente Pyro5...")
# Localiza o Name Server
try:
    ns = Pyro5.api.locate_ns()
    print("Name Server localizado.")
except Pyro5.errors.NamingError:
    print("Name Server não encontrado. Certifique-se de que ele está rodando.")
    exit
    
# Obtém o URI do serviço
try:
    uri = ns.lookup("servicos.servidor")
except Pyro5.errors.NamingError:
    print("Serviço não encontrado no Name Server.")
    exit
    
print(f"Serviço encontrado: {uri}")
# Cria proxy para o serviço

def login():
    with Pyro5.api.Proxy(uri) as servidor:
        respostaServidor = servidor.logar("lol@ufg.com")
        print(f"Resposta do servidor: {respostaServidor}")

def menuInterface():
    print(f"1. Login")

    print(f"Digite a opção escolhida: ")

def menu():
    menuInterface()
    operacao = input()

    match operacao:
        case 1:
            login()

        case _:
            print(f"Operação inválida.")
