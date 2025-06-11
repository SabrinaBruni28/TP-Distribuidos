import threading
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
    def enfileira(self, requisicao, dados, requisicao_id, imagens=True, outro_id=True):
        self._fila.put((requisicao, dados, requisicao_id, imagens, outro_id))

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
                requisicao, dados, id_requisicao, imagens, outro_id = requisicao_dados
            except ValueError:
                print("[Fila de Mensagens] Erro: tupla mal formada na fila.")
                continue

            if requisicao and dados and id_requisicao:
                self.fazRequisicaoAoBanco(requisicao, dados, id_requisicao, imagens)
            else:
                print("[Fila de Mensagens] Erro ao obter requisição, dados ou id.")


    # O enviaAoBanco, agora, invoca um método do banco de dados. 
    # Achei o nome fazRequisicao mais coerente pro funcionamento de agora.
    # Falando no "funcionamento de agora", ainda não elaborei como fazer quando há imagens na conversa.  ¬.¬
    def fazRequisicaoAoBanco(self, requisicao, dados, num_id, imagens):
        print("[Fila de Mensagens] Fazendo uma requisição ao Banco de Dados.")

        try:
            if self.bancoURI is None:
                self.conectaBanco()

            # TODO: Mudar esse comentário
            # Aqui chamo a função do banco correspondente usando Pyro5.
            # Imagino que vou ter que fazer uma função aqui que decide a invocação certa
            # com base na requisição.
            respostaBanco = self._decisorFila(requisicao, dados, num_id, imagens)

            # Depois de receber a resposta, guarda ela e avisa o servidor.
            # Aí o cliente ligado à essa requisição específica encontra a resposta.
            self._respostas.guardarResposta(num_id, respostaBanco)

        # Caso a conexão com o banco de dados seja perdida, tenta reconectar e reenviar a requisição.
        except (Pyro5.errors.CommunicationError, Pyro5.errors.ConnectionClosedError) as e:
            print(f"[Fila de Mensagens] Conexão perdida ou erro na comunicação: {e}. Reconectando...")
            self.bancoURI = None
            self.conectaBanco()
            self.fazRequisicaoAoBanco(requisicao, dados, num_id, imagens)

    def _decisorFila(self, requisicao, dados, num_id, imagens):
        match str(requisicao):
            case "login":
                return self._login(dados, num_id)
            
            case "cadastramento":
                return self._cadastramento(dados, num_id)
            
            case "codigo":
                return self._codigo(dados, num_id)
            
            case "visualizar_anuncios":
                return self._visualizarAnuncios(num_id)
            
            case "visualizar_anuncio":
                return self._visualizarAnuncio(dados, num_id)
            
            case "visualizar_produto":
                return self._visualizarProduto(dados, num_id)
            
            case "visualizar_loja":
                return self._visualizarLoja(dados, num_id)
            
            case "visualizar_minha_loja":
                return self._visualizarMinhaLoja(dados, num_id)
            
            case "visualizar_minhas_lojas":
                return self._visualizarMinhasLojas(dados, num_id)
            
            case "visualizar_meus_enderecos":
                return self._visualizarMeusEnderecos(dados, num_id)
            
            case "visualizar_pedido":
                return self._visualizarPedido(dados, num_id)
            
            case "visualizar_meus_pedidos":
                return self._visualizarMeusPedidos(dados, num_id)
            
            case "editar_anuncio":
                return self._editarAnuncio(dados, num_id)
            
            case "editar_produto":
                return self._editarProduto(dados, num_id)
            
            case "editar_loja":
                return self._editarLoja(dados, imagens, num_id)
            
            case "editar_endereco":
                return self._editarEndereco(dados, num_id)
            
            case "editar_usuario":
                return self._editarUsuario(dados, num_id)
            
            case "criar_anuncio":
                return self._criarAnuncio(dados, num_id)
            
            case "criar_produtos":
                return self._criarProdutos(dados, imagens, num_id)
            
            case "criar_loja":
                return self._criarLoja(dados, imagens, num_id)
            
            case "criar_pedido":
                return self._criarPedido(dados, num_id)
            
            case "criar_endereco":
                return self._criarEndereco(dados, num_id)
            
            case "criar_imagem":
                return self._criarImagem(dados, imagens, num_id)
            
            case "excluir_anuncio":
                return self._excluirAnuncio(dados, num_id)
            
            case "excluir_produto":
                return self._excluirProduto(dados, num_id)
            
            case "excluir_loja":
                return self._excluirLoja(dados, num_id)
            
            case "excluir_endereco":
                return self._excluirEndereco(dados, num_id)
            
            case "excluir_imagem":
                return self._excluirImagem(dados, num_id)
            
            case "confirmar_pedido":
                return self._confirmarPedido(dados, num_id)
            
            case "cancelar_pedido":
                return self._cancelarPedido(dados, num_id)
            
            case _:
                print(f"[Fila de Mensagens] Requisição do Servidor mal formada.")
                return False


    def _login(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Login] Chamando função de login do Banco de Dados.")
            return banco.loginUsuario(dados)
            
    def _cadastramento(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Cadastramento] Chamando função de conferir usuário do Banco de Dados.")
            respostaBanco = banco.confereUsuario(dados)

            if respostaBanco is True:
                print("[Fila de Mensagens][Cadastramento] ")
                emailCliente = dados.get("email")
                print(f"[Fila de Mensagens][Cadastramento] Email: {emailCliente}")

                email = correio.ThreadEmail("confirmacao cadastro", emailCliente)
                email.start()

                codigoConfirmacao = str(email.codigo)
                print(f"[Fila de Mensagens][Cadastramento] Código de confirmação enviado: {codigoConfirmacao}")

                self.dadosTemp.armazenar(num_id, codigoConfirmacao, dados)

                print("[Fila de Mensagens][Cadastramento] Esperando confirmação de email do cliente...")
                return num_id
            
            elif (isinstance(respostaBanco, list)):
                return respostaBanco

            else:
                return False
            
    def _codigo(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Cadastramento][Código] Chamando função de criar usuário do Banco de Dados.")
            return banco.criarUsuario(dados)

    def _visualizarAnuncios(self, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Todos os Anúncios] Chamando função de visualizar todos os anúncios do Banco de Dados.")
            return banco.retornarAnuncios()

    def _visualizarAnuncio(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Anúncio] Chamando função de visualizar anúncio do Banco de Dados.")
            return banco.retornarAnuncio(dados)

    def _visualizarProduto(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarProduto(dados)

    def _visualizarLoja(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarLoja(dados)

    def  _visualizarMinhaLoja(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMinhaLoja(dados)

    def _visualizarMinhasLojas(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMinhasLojas(dados)

    def _visualizarMeusEnderecos(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeusEnderecos(dados)

    def _visualizarPedido(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeuPedido(dados)

    def _visualizarMeusPedidos(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Visualizar][Produto] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarMeusPedidos(dados)

    def _editarAnuncio(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Anúncio] Chamando função de editar anúncio do Banco de Dados.")
            return banco.editarAnuncio(dados)

    def _editarProduto(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Produto] Chamando função de editar produto do Banco de Dados.")
            return banco.editarProduto(dados)

    def _editarLoja(self, dados, imagem, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Loja] Chamando função de editar loja do Banco de Dados.")
            return banco.editarLoja(dados, imagem)

    def _editarEndereco(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Anúncio] Chamando função de editar anúncio do Banco de Dados.")
            return banco.editarEndereco(dados)

    def _editarUsuario(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Editar][Usuário] Chamando função de editar usuário do Banco de Dados.")
            return banco.editarUsuario(dados)

    def _criarAnuncio(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Anúncio] Chamando função de criar anúncio do Banco de Dados.")
            return banco.criarAnuncio(dados)

    def _criarProdutos(self, dados, imagens, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Produto] Chamando função de criar produto do Banco de Dados.")
            return banco.criarProduto(dados, imagens)

    def _criarLoja(self, dados, imagens, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Loja] Chamando função de criar loja do Banco de Dados.")
            return banco.criarLoja(dados, imagens)

    def _criarPedido(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Pedido] Chamando função de criar pedido do Banco de Dados.")
            return banco.criarPedido(dados)

    def _criarEndereco(self, dados, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Endereço] Chamando função de criar endereço do Banco de Dados.")
            return banco.criarEndereco(dados)

    def _criarImagem(self, dados, imagem, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Criar][Imagem] Chamando função de criar imagem do Banco de Dados.")
            return banco.criarImagem(dados, imagem)

    def _excluirAnuncio(self, id_anuncio, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Excluir][Anúncio] Chamando função de excluir anúncio do Banco de Dados.")
            return banco.excluirAnuncio(id_anuncio)

    def _excluirProduto(self, id_produto, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Excluir][Produto] Chamando função de excluir produto do Banco de Dados.")
            return banco.excluirProduto(id_produto)

    def _excluirLoja(self, id_loja, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Excluir][Loja] Chamando função de excluir loja do Banco de Dados.")
            return banco.excluirLoja(id_loja)

    def _excluirEndereco(self, id_endereco, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Excluir][Endereço] Chamando função de excluir endereço do Banco de Dados.")
            return banco.excluirEndereco(id_endereco)

    def _excluirImagem(self, nome_imagem, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Excluir][Imagem] Chamando função de excluir anúncio do Banco de Dados.")
            return banco.excluirImagem(nome_imagem)

    def _confirmarPedido(self, id_pedido, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Pedido][Confirmar] Chamando função de confirmar pedido do Banco de Dados.")
            return banco.confirmarPedido(id_pedido)

    def _cancelarPedido(self, id_pedido, num_id):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Pedido][Cancelar] Chamando função de cancelar pedido do Banco de Dados.")
            return banco.cancelarPedido(id_pedido)

    def conectaBanco(self):
        print("[Fila de Mensagens] Conectando ao Banco de Dados via Pyro5...")
        ns = Pyro5.api.locate_ns(host='192.168.1.4', port=5000)
        print("[Fila de Mensagens] Tentando fazer o lookup.")
        self.bancoURI = ns.lookup("Caldeirao:servicos.banqueiro")
        print(f"[Fila de Mensagens] URI do Banco de Dados: {self.bancoURI}")

    def esperarRespostaDoBancoDeRespostas(self, num_id):
        return self._respostas.esperaResposta(num_id)
    
    def registraRequisicao(self, num_id):
        self._respostas.criaRequisicao(num_id)