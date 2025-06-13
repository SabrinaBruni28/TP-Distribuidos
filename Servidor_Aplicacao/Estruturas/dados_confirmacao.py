import time

class DadosTemporariosConfirmacao:
    def __init__(self):
        self._dados = {}  # socket_cliente -> {codigo, dados, tentativas}

    def armazenar(self, socket_cliente, codigo, dados):
        self._dados[socket_cliente] = {
            "codigo": codigo,
            "dados": dados,
            "tentativas": 0,
            "timestamp": time.time()
        }

    def verificarCodigo(self, socket_cliente, codigo_recebido):
        if socket_cliente not in self._dados:
            return "erro", "tempo_excedido"

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

    def limpar_expirados(self):
        print(f"[Fila de Mensagens][Dados de Confirmação] Conferindo dados expirados.")
        import time

        agora = time.time()

        expirados = []

        for sock, info in self._dados.items():
            timestamp = info.get("timestamp")

            if timestamp is None:
                # Se timestamp não existe, considera como expirado (ou pule, se preferir)
                expirados.append(sock)
                continue

            # Verifica se passou do tempo limite (180s - 3m)
            if agora - timestamp > 180:
                expirados.append(sock)
                print(f"[Fila de Mensagens][Dados de Confirmação] Dados expirados aqui: {sock}")

        # Remove depois de iterar
        for sock in expirados:
            try:
                del self._dados[sock]
            except KeyError:
                print("[Fila de Mensagens][Dados de Confirmação] Não conseguiu deletar dados expirados.")
