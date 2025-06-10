import socket
import threading
import logging
import json
import Pyro5.api
import Pyro5.errors
from Estruturas.mensagem import Mensagem
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Estruturas.banco_de_respostas import BancoDeRespostas
from Operacoes import server_operation as op
from Operacoes import thread_email as correio
from queue import Queue, Empty
from Operacoes import callback as cb
from Operacoes import imagem as img


# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
# TODO: Mudar o nome para Fila de Requisições
class FilaDeMensagensV2(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self._respostas = BancoDeRespostas()
        self.dadosTemp = DadosTemporariosConfirmacao()
        self.bancoURI = None

    # Com o middleware, por hora, enfileiro o tipo de requisição, os dados que o cliente passou
    # e o ID dessa requisição. Não considerei imagens ainda.
    # TODO: Criar uma estrutura equivalente à Mensagem para conter tudo o que uma requisição precisar
    def enfileira(self, requisicao, dados, id, imagens=True):
        self._fila.put((requisicao, dados, id, imagens))

    def desenfileira(self):
        try:
            return self._fila.get(timeout=60)
        except Empty:
            return None
    
    # Já o funcionamento da fila muda drasticamente. Não precisamos mais de decisores pois não há uma mensagem a ser
    # analisada e processada. O enviaAoBanco já faz tudo já que comunicação entre os processos é mais "direta".
    # TODO: Implementar a estratégia antipooling do Banco de Respostas aqui também.
    def run(self):
        while True:
            self.dadosTemp.limpar_expirados()
            requisicao_dados = self.desenfileira()

            if requisicao_dados is None:
                continue  # Nada na fila, mas já limpamos os expirados

            try:
                requisicao, dados, id, imagens = requisicao_dados
            except ValueError:
                print("[Fila de Mensagens] Erro: tupla mal formada na fila.")
                continue

            if requisicao and dados and id:
                self.fazRequisicaoAoBanco(requisicao, dados, id, imagens)
            else:
                print("[Fila de Mensagens] Erro ao obter requisição, dados ou id.")


    # O enviaAoBanco, agora, invoca um método do banco de dados. 
    # Achei o nome fazRequisicao mais coerente pro funcionamento de agora.
    # Falando no "funcionamento de agora", ainda não elaborei como fazer quando há imagens na conversa.  ¬.¬
    def fazRequisicaoAoBanco(self, requisicao, dados, id, imagens):
        print("[Fila de Mensagens] Fazendo uma requisição ao Banco de Dados.")

        try:
            if self.bancoURI is None:
                self.conectaBanco()

            # TODO: Mudar esse comentário
            # Aqui chamo a função do banco correspondente usando Pyro5.
            # Imagino que vou ter que fazer uma função aqui que decide a invocação certa
            # com base na requisição.
            respostaBanco = self._decisorFila(requisicao, dados, id, imagens)

            # Depois de receber a resposta, guarda ela e avisa o servidor.
            # Aí o cliente ligado à essa requisição específica encontra a resposta.
            self._respostas.guardarResposta(id, respostaBanco)

        # Caso a conexão com o banco de dados seja perdida, tenta reconectar e reenviar a requisição.
        except (Pyro5.errors.CommunicationError, Pyro5.errors.ConnectionClosedError) as e:
            print(f"[Fila de Mensagens] Conexão perdida ou erro na comunicação: {e}. Reconectando...")
            self.bancoURI = None
            self.conectaBanco()
            self.fazRequisicaoAoBanco(requisicao, dados, id, imagens)

    def _decisorFila(self, requisicao, dados, id, imagens):
        match requisicao:
            case "login":
                return self._login(dados, id)
            
            case "cadastramento":
                return self._cadastramento(dados, id)
            
            case "codigo":
                return self._codigo(dados, id)
            
            case "visualizar_anuncios":
                return self._visualizarAnuncios(id)
            
            case "visualizar_anuncio":
                return self._visualizarAnuncio(dados, id)
            
            case "visualizar_produto":
                return self._visualizarProduto(dados, id)
            
            case "visualizar_loja":
                return self._visualizarLoja(dados, id)
            
            case "visualizar_minha_loja":
                return self._visualizarMinhaLoja(dados, id)
            
            case "visualizar_minhas_lojas":
                return self._visualizarMinhasLojas(dados, id)
            
            case "visualizar_meus_enderecos":
                return self._visualizarMeusEnderecos(dados, id)
            
            case "visualizar_pedido":
                return self._visualizarPedido(dados, id)
            
            case "visualizar_meus_pedidos":
                return self._visualizarMeusPedidos(dados, id)
            
            case "editar_anuncio":
                return self._editarAnuncio(dados, id)
            
            case "editar_produto":
                return self._editarProduto(dados, id)
            
            case "editar_loja":
                return self._editarLoja(dados, imagens, id)
            
            case "editar_endereco":
                return self._editarEndereco(dados, id)
            
            case "editar_usuario":
                return self._editarUsuario(dados, id)
            
            case "criar_anuncio":
                return self._criarAnuncio(dados, id)
            
            case "criar_produtos":
                return self._criarProdutos(dados, id)
            
            case "criar_loja":
                return self._criarLoja(dados, id)
            
            case "criar_pedido":
                return self._criarPedido(dados, id)
            
            case "criar_endereco":
                return self._criarEndereco(dados, id)
            
            case "criar_imagem":
                return self._criarImagem(dados, id)
            
            case "excluir_anuncio":
                return self._excluirAnuncio(dados, id)
            
            case "excluir_produto":
                return self._excluirProduto(dados, id)
            
            case "excluir_loja":
                return self._excluirLoja(dados, id)
            
            case "excluir_endereco":
                return self._excluirEndereco(dados, id)
            
            case "excluir_imagem":
                return self._excluirImagem(dados, id)
            
            case "confirmar_pedido":
                return self._confirmarPedido(dados, id)
            
            case "cancelar_pedido":
                return self._cancelarPedido(dados, id)
            
            case _:
                pass


    def _login(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Login] Chamando função de login do Banco de Dados.")
            return banco.loginUsuario(dados)
            
    def _cadastramento(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Cadastramento] Chamando função de conferir usuário do Banco de Dados.")
            respostaBanco = banco.confereUsuario(dados)

            if (respostaBanco is True):
                print("[Fila de Mensagens][Cadastramento] ")
                emailCliente = dados.get("email")
                print(f"[Fila de Mensagens][Cadastramento] Email: {emailCliente}")

                email = correio.ThreadEmail("confirmacao cadastro", emailCliente)
                email.start()

                codigoConfirmacao = str(email.codigo)
                print(f"[Fila de Mensagens][Cadastramento] Código de confirmação enviado: {codigoConfirmacao}")

                self.dadosTemp.armazenar(id, codigoConfirmacao, dados)

                print("[Fila de Mensagens][Cadastramento] Esperando confirmação de email do cliente...")
                return id
            
            elif (isinstance(respostaBanco, list)):
                return respostaBanco
            
    def _codigo(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Cadastramento][Código] Chamando função de criar usuário do Banco de Dados.")
            return banco.criarUsuario(dados)

    def _visualizarAnuncios(self, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Todos os Anúncios] Chamando função de visualizar todos os anúncios do Banco de Dados.")
            return banco.retornarAnuncios()

    def _visualizarAnuncio(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Anúncio] Chamando função de visualizar anúncio do Banco de Dados.")
            return banco.retornarAnuncio(dados)

    def _visualizarProduto(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarProduto(dados)

    def _visualizarLoja(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarLoja(dados)

    def  _visualizarMinhaLoja(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMinhaLoja(dados)

    def _visualizarMinhasLojas(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMinhasLojas(dados)

    def _visualizarMeusEnderecos(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeusEnderecos(dados)

    def _visualizarPedido(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeuPedido(dados)

    def _visualizarMeusPedidos(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeusPedidos(dados)

    def _editarAnuncio(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Anúncio] Chamando função de editar anúncio do Banco de Dados.")
            return banco.editarAnuncio(dados)

    def _editarProduto(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Produto] Chamando função de editar produto do Banco de Dados.")
            return banco.editarProduto(dados)

    def _editarLoja(self, dados, imagem, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Loja] Chamando função de editar loja do Banco de Dados.")
            return banco.editarLoja(dados, imagem)

    def _editarEndereco(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Anúncio] Chamando função de editar anúncio do Banco de Dados.")
            return banco.editarEndereco(dados)

    def _editarUsuario(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Usuário] Chamando função de editar usuário do Banco de Dados.")
            return banco.editarUsuario(dados)

    def _criarAnuncio(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Anúncio] Chamando função de criar anúncio do Banco de Dados.")
            return banco.editarUsuario(dados)

    def _criarProdutos(self, dados, imagens, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Produto] Chamando função de criar produto do Banco de Dados.")
            return banco.editarUsuario(dados, imagens)

    def _criarLoja(self, dados, imagens, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Loja] Chamando função de criar loja do Banco de Dados.")
            return banco.editarUsuario(dados, imagens)

    def _criarPedido(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Pedido] Chamando função de criar pedido do Banco de Dados.")
            return banco.editarUsuario(dados)

    def _criarEndereco(self, dados, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Endereço] Chamando função de criar endereço do Banco de Dados.")
            return banco.editarUsuario(dados)

    def _criarImagem(self, dados, imagem, id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Imagem] Chamando função de criar imagem do Banco de Dados.")
            return banco.editarUsuario(dados, imagem)

    def _excluirAnuncio(self, dados, id):
        pass
    def _excluirProduto(self, dados, id):
        pass
    def _excluirLoja(self, dados, id):
        pass
    def _excluirEndereco(self, dados, id):
        pass
    def _excluirImagem(self, dados, id):
        pass
    def _confirmarPedido(self, dados, id):
        pass
    def _cancelarPedido(self, dados, id):
        pass

    def conectaBanco(self):
        print("[Fila de Mensagens] Conectando ao Banco de Dados via Pyro5...")
        ns = Pyro5.api.locate_ns(host='192.168.1.4', port=5000)
        print("[Fila de Mensagens] Tentando fazer o lookup.")
        self.bancoURI = ns.lookup("Caldeirao:servicos.banqueiro")
        print(f"[Fila de Mensagens] URI do Banco de Dados: {self.bancoURI}")

    def esperarRespostaDoBancoDeRespostas(self, id):
        return self._respostas.esperaResposta(id)
    
    def registraRequisicao(self, id):
        self._respostas.criaRequisicao(id)