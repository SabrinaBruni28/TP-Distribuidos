import socket

class DadosTemporariosConfirmacao:
    def __init__(self):
        self._dados = {}  # socket_cliente -> {codigo, dados, tentativas}

    def armazenar(self, socket_cliente, codigo, dados):
        self._dados[socket_cliente] = {
            "codigo": codigo,
            "dados": dados,
            "tentativas": 0
        }

    def verificarCodigo(self, socket_cliente, codigo_recebido):
        if socket_cliente not in self._dados:
            return "erro", "sem_dados"

        info = self._dados[socket_cliente]
        if codigo_recebido == info["codigo"]:
            dados = info["dados"]
            del self._dados[socket_cliente]  # remove após sucesso
            return "ok", dados

        # código incorreto
        info["tentativas"] += 1
        if info["tentativas"] >= 3:
            del self._dados[socket_cliente]
            return "erro", "limite_excedido"
        else:
            return "erro", "codigo_invalido"

    def abortar(self, socket_cliente):
        self._dados.pop(socket_cliente, None)
