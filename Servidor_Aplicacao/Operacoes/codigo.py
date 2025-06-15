from Estruturas.requisicao import Requisicao

class Codigo():
    def __init__(self, fila_requisicoes):
        self.fila = fila_requisicoes

    # O fim da requisição de cadastramento, o envio do código de confirmação pelo cliente
    # contém parte da comunicação envolvendo apenas o cliente e o servidor.
    # Aqui, o cliente envia seu identificador, que foi retornado na requisição de
    # cadastramento, junto ao código de confirmação.
    def codigo(self, idCliente, codigo):
        print("[Servidor][Código] Código recebido.")
        
        # O primeiro passo é verificar se:
        #   - O tempo de enviar o código já expirou
        #   - As três tentativas já foram
        #   - Por fim, se o código está correto
        status, dados = self.fila.dadosTemp.verificarCodigo(idCliente, codigo)

        print(f"[Servidor][Código] Código que o cliente enviou: {codigo}")
        print(f"[Servidor][Código] ID do código: {idCliente}")
        return self.decisorCodigo(status, dados)

    # Com a resposta do verificador de código de confirmação, decidimos a resposta
    # pro cliente.
    def decisorCodigo(self, status, dados):
        # Se a resposta for "ok", significa que o código não expirou e está correto.
        if status == "ok":
            # Então segue o padrão, cria um ID de requisição para o banco de dados,
            print("[Servidor][Código] Código confirmado.")
            requisicao = Requisicao.produzRequisicao("codigo", dados)

            # Registra a requisição,
            self.fila.registraRequisicao(requisicao)

            # Coloca a requisição na fila
            print(f"[Servidor][Código][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando requisição para a fila...")
            self.fila.enfileira(requisicao)

            # Espera e retorna a resposta do banco de dados
            return self.fila.esperarRespostaDoBancoDeRespostas(requisicao)

        # Se houver algum erro, retorna o tipo de erro.
        elif status == "erro":
            print("[Servidor][Código] Código inválido. Retornando ao cliente.")
            return dados

        else:
            return False