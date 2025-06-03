import socket
import threading
import logging
import Pyro5.api
import Pyro5.errors
from Estruturas.mensagem import Mensagem
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Estruturas.banco_de_respostas import BancoDeRespostas
from Operacoes import server_operation as op
from queue import Queue, Empty
from Operacoes import callback as cb
from Operacoes import imagem as img

# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
class FilaDeMensagensV2(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self._respostas = BancoDeRespostas
        self._respostas.start()
        self.dadosTemp = DadosTemporariosConfirmacao()
        self.bancoURI = None

    # Com o middleware, por hora, enfileiro o tipo de requisição, os dados que o cliente passou
    # e o ID dessa requisição. Não considerei imagens ainda.
    # TODO: Criar uma estrutura equivalente à Mensagem para conter tudo o que uma requisição precisar
    def enfileira(self, requisicao, dados, id):
        self._fila.put((requisicao, dados, id))

    def desenfileira(self):
        try:
            return self._fila.get()
        except Empty:
            return None
    
    # Já o funcionamento da fila muda drasticamente. Não precisamos mais de decisores pois não há uma mensagem a ser
    # analisada e processada. O enviaAoBanco já faz tudo já que comunicação entre os processos é mais "direta".
    # TODO: Implementar a estratégia antipooling do Banco de Respostas aqui também.
    def run(self):
        while True:
            try:
                self.dadosTemp.limpar_expirados()
                requisicao, dados, id = self.desenfileira()
            except ValueError:
                print("[Fila de Mensagens] Erro: tupla mal formada na fila.")
                continue

            if requisicao and dados and id:
                self.fazRequisicaoAoBanco(requisicao, dados, id)

            else:
                print("[Fila de Mensagens] Erro ao obter requisição, dados ou id.")

    # O enviaAoBanco, agora, invoca um método do banco de dados. 
    # Achei o nome fazRequisicao mais coerente pro funcionamento de agora.
    # Falando no "funcionamento de agora", ainda não elaborei como fazer quando há imagens na conversa.  ¬.¬
    def fazRequisicaoAoBanco(self, requisicao, dados, id):
        print("[Fila de Mensagens] Fazendo uma requisição ao Banco de Dados.")

        try:
            if self.bancoURI is None:
                self.conectaBanco()

            # Aqui chamo a função do banco correspondente usando Pyro5.
            # Imagino que vou ter que fazer uma função aqui que decide a invocação certa
            # com base na requisição.
            #TODO: Comunicação com o Banco usando Pyro5
            respostaBanco = None

            # Depois de receber a resposta, guarda ela e avisa o servidor.
            # Aí o cliente ligado à essa requisição específica encontra a resposta.
            self._respostas.guardarResposta(id, respostaBanco)

        except (Pyro5.errors.CommunicationError, Pyro5.errors.ConnectionClosedError) as e:
            print(f"[Fila de Mensagens] Conexão perdida ou erro na comunicação: {e}. Reconectando...")
            self.bancoURI = None
            self.conectaBanco()

    def conectaBanco(self):
        print("[Fila de Mensagens] Conectando ao Banco de Dados via Pyro5...")
        self.bancoURI = Pyro5.api.Proxy("PROXYNAME:Caldeirao.database")

    def esperaRespostaDoBancoDeRespostas(self, id):
        return self._respostas.esperaResposta(id)
    
    def registraRequisicao(self, id):
        self._respostas.criaRequisicao(id)