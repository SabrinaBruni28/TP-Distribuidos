import threading
import Pyro5.api
import Pyro5.errors
from Estruturas.requisicao import Requisicao
from Estruturas.dados_confirmacao import DadosTemporariosConfirmacao
from Estruturas.banco_de_respostas import BancoDeRespostas
from Operacoes import thread_email as correio
from queue import Queue, Empty

# A Fila de Mensagens, estrutura da comunicação do nosso sistema.
# A comunicação do sistema é efetivamente híbrida
# A fila é usada na comunicação com o servidor de banco de dados
# A comunicação entre cliente e servidor ainda é direta
class FilaDeRequisicoes(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._fila = Queue()
        self._respostas = BancoDeRespostas()
        self.dadosTemp = DadosTemporariosConfirmacao()
        self.bancoURI = None

    def enfileira(self, requisicao: Requisicao):
        """ Essa função coloca a requisição montada pelo servidor na fila para ser enviada ao Banco de Dados.
            A estrutura de requisição já carrega todas as informações de uma requisição.
        """
        self._fila.put((requisicao))

    def desenfileira(self):
        """ A função de desenfileiramento de Queue trava a thread até que algo apareça na lista para ser desenfileirado.
        Por isso, temos um timeout de um minuto para a Fila de Requisição destravar, no caso de mais nenhum cliente
        enviar nenhuma outra requisição, e a estrutura limpar os dados de cadastramento de algum cliente.
        """
        try:
            return self._fila.get(timeout=60)
        except Empty:
            return None
    

    # TODO: Implementar a estratégia antipooling do Banco de Respostas aqui também.
    def run(self):
        """ A fila está sempre rodando em segundo plano, em uma thread diferente. Ela fica enviando as requisições do
        servidor para o Banco de Dados na ordem de chegada da fila.

            Além de ficar desenfileirando as requisições, a fila também limpa os dados de cadastramento de um cliente
        que não enviou o código de confirmação dentro do prazo de 3 minutos.
        """

        while True:
            self.dadosTemp.limpar_expirados()
            requisicaoServidor = self.desenfileira()

            if requisicaoServidor is None:
                continue  # Nada na fila, mas já limpamos os expirados

            try:
                requisicao = requisicaoServidor
            except ValueError:
                print("[Fila de Mensagens] Erro: tupla mal formada na fila.")
                continue

            if requisicao:
                self.fazRequisicaoAoBanco(requisicao)
            else:
                print("[Fila de Mensagens] Erro ao obter requisição, dados ou id.")


    # O enviaAoBanco, agora, invoca um metodo do banco de dados.
    # Achei o nome fazRequisicao mais coerente pro funcionamento de agora.
    def fazRequisicaoAoBanco(self, requisicao: Requisicao):
        """ Essa é a função responsável por fazer uma requisição ao Banco de Dados.
            Ela conecta ao Banco, caso a URI do Banco de Dados não tenha sido atribuída ainda ou a conexão tenha sido perdida.
            Depois, ela vê que tipo de chamada deve fazer ao Banco.
            Por fim, com a resposta do Banco de Dados em mãos, ela guarda a resposta no Banco de Respostas para o servidor.
        """
        print("[Fila de Mensagens] Fazendo uma requisição ao Banco de Dados.")

        try:
            if self.bancoURI is None:
                self.conectaBanco()

            # Aqui eu chamo um decisor que decide qual metodo do banco de dados eu vou invocar com base
            # no tipo de requisição.
            respostaBanco = self._decisorFila(requisicao)

            # Depois de receber a resposta, guarda ela e avisa o servidor.
            # Aí o cliente ligado à essa requisição específica encontra a resposta.
            self._respostas.guardarResposta(requisicao.idRequisicao, respostaBanco)

        # Caso a conexão com o banco de dados seja perdida, tenta reconectar e reenviar a requisição.
        except (Pyro5.errors.CommunicationError, Pyro5.errors.ConnectionClosedError) as e:
            print(f"[Fila de Mensagens] Conexão perdida ou erro na comunicação: {e}. Reconectando...")
            self.bancoURI = None
            try:
                self.conectaBanco()
                # Aqui eu chamo um decisor que decide qual metodo do banco de dados eu vou invocar com base
                # no tipo de requisição.
                respostaBanco = self._decisorFila(requisicao)

                # Depois de receber a resposta, guarda ela e avisa o servidor.
                # Aí o cliente ligado à essa requisição específica encontra a resposta.
                self._respostas.guardarResposta(requisicao.idRequisicao, respostaBanco)

            except Pyro5.errors.CommunicationError as e:
                print(f"[Fila de Mensagens] Banco de Dados fechado.")
                return

    def _decisorFila(self, requisicao: Requisicao):
        """ Essa função da Fila de Requisições decide o tipo de chamada que faz ao Banco a partir do tipo. """
        match str(requisicao.tipoRequisicao):
            case "login":
                return self._login(requisicao)
            
            case "cadastramento":
                return self._cadastramento(requisicao)
            
            case "codigo":
                return self._codigo(requisicao)
            
            case "visualizar_anuncios":
                return self._visualizarAnuncios(requisicao)
            
            case "visualizar_anuncio":
                return self._visualizarAnuncio(requisicao)
            
            case "visualizar_produto":
                return self._visualizarProduto(requisicao)
            
            case "visualizar_loja":
                return self._visualizarLoja(requisicao)
            
            case "visualizar_minha_loja":
                return self._visualizarMinhaLoja(requisicao)
            
            case "visualizar_minhas_lojas":
                return self._visualizarMinhasLojas(requisicao)
            
            case "visualizar_meus_enderecos":
                return self._visualizarMeusEnderecos(requisicao)
            
            case "visualizar_pedido":
                return self._visualizarPedido(requisicao)
            
            case "visualizar_meus_pedidos":
                return self._visualizarMeusPedidos(requisicao)
            
            case "editar_anuncio":
                return self._editarAnuncio(requisicao)
            
            case "editar_produto":
                return self._editarProduto(requisicao)
            
            case "editar_loja":
                return self._editarLoja(requisicao)

            case "editar_endereco":
                return self._editarEndereco(requisicao)

            case "editar_usuario":
                return self._editarUsuario(requisicao)

            case "criar_anuncio":
                return self._criarAnuncio(requisicao)

            case "criar_produto":
                return self._criarProdutos(requisicao)

            case "criar_loja":
                return self._criarLoja(requisicao)

            case "criar_pedido":
                return self._criarPedido(requisicao)

            case "criar_endereco":
                return self._criarEndereco(requisicao)

            case "criar_imagem":
                return self._criarImagem(requisicao)

            case "excluir_anuncio":
                return self._excluirAnuncio(requisicao)

            case "excluir_produto":
                return self._excluirProduto(requisicao)

            case "excluir_loja":
                return self._excluirLoja(requisicao)

            case "excluir_endereco":
                return self._excluirEndereco(requisicao)

            case "excluir_imagem":
                return self._excluirImagem(requisicao)

            case "confirmar_pedido":
                return self._confirmarPedido(requisicao)

            case "cancelar_pedido":
                return self._cancelarPedido(requisicao)

            case "imagens_produto":
                return self._pegarImagemProduto(requisicao)

            case "imagens_loja":
                return self._pegarImagemLoja(requisicao)

            case "imagens_pedido":
                return self._pegarImagemPedido(requisicao)

            case _:
                print(f"[Fila de Mensagens] Requisição do Servidor mal formada.")
                return False


    def _login(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Login][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de login do Banco de Dados.")
            return banco.loginUsuario(requisicao.dadosRequisicao)

    def _cadastramento(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de conferir usuário do Banco de Dados.")
            respostaBanco = banco.confereUsuario(requisicao.dadosRequisicao)

            if respostaBanco is True:
                print(f"[Fila de Mensagens][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando email de confirmação para o cliente.")
                emailCliente = requisicao.dadosRequisicao.get("email")
                nomeCliente = requisicao.dadosRequisicao.get("nome")

                print(f"[Fila de Mensagens][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Email: {emailCliente}")

                email = correio.ThreadEmail("confirmacao cadastro", emailCliente, nomeCliente)
                email.start()

                codigoConfirmacao = str(email.codigo)
                print(f"[Fila de Mensagens][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Código de confirmação enviado: {codigoConfirmacao}")

                self.dadosTemp.armazenar(requisicao.idRequisicao, codigoConfirmacao, requisicao.dadosRequisicao)

                print(f"[Fila de Mensagens][Cadastramento][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Esperando confirmação de email do cliente...")
                return requisicao.idRequisicao

            elif (isinstance(respostaBanco, list)):
                return respostaBanco

            else:
                return False

    def _codigo(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Cadastramento][Código][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar usuário do Banco de Dados.")
            return banco.criarUsuario(requisicao.dadosRequisicao)

    def _visualizarAnuncios(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Todos os Anúncios][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar todos os anúncios do Banco de Dados.")
            return banco.retornarAnuncios()

    def _visualizarAnuncio(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar anúncio do Banco de Dados.")
            return banco.retornarAnuncio(requisicao.dadosRequisicao)

    def _visualizarProduto(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar produto do Banco de Dados.")
            return banco.retornarProduto(requisicao.dadosRequisicao)

    def _visualizarLoja(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar loja do Banco de Dados.")
            return banco.retornarLoja(requisicao.dadosRequisicao)

    def  _visualizarMinhaLoja(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Minha Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar loja do usuário do Banco de Dados.")
            return banco.retornarMinhaLoja(requisicao.dadosRequisicao)

    def _visualizarMinhasLojas(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Minhas Lojas][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar lojas do usuário do Banco de Dados.")
            return banco.retornarMinhasLojas(requisicao.dadosRequisicao)

    def _visualizarMeusEnderecos(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Meus Endereços][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar endereços do usuário do Banco de Dados.")
            return banco.retornarMeusEnderecos(requisicao.dadosRequisicao)

    def _visualizarPedido(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar pedido do Banco de Dados.")
            return banco.retornarPedido(requisicao.dadosRequisicao)

    def _visualizarMeusPedidos(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Visualizar][Meus pedidos][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de visualizar pedidos do usuário do Banco de Dados.")
            return banco.retornarMeusPedidos(requisicao.dadosRequisicao)

    def _editarAnuncio(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Editar][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de editar anúncio do Banco de Dados.")
            return banco.editarAnuncio(requisicao.dadosRequisicao)

    def _editarProduto(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Editar][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de editar produto do Banco de Dados.")
            return banco.editarProduto(requisicao.dadosRequisicao)

    def _editarLoja(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Editar][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de editar loja do Banco de Dados.")
            return banco.editarLoja(requisicao.dadosRequisicao, requisicao.imagens)

    def _editarEndereco(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Editar][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de editar endereço do Banco de Dados.")
            return banco.editarEndereco(requisicao.dadosRequisicao)

    def _editarUsuario(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Editar][Usuário][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de editar usuário do Banco de Dados.")
            return banco.editarUsuario(requisicao.dadosRequisicao)

    def _criarAnuncio(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar anúncio do Banco de Dados.")
            return banco.criarAnuncio(requisicao.dadosRequisicao)

    def _criarProdutos(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar produto do Banco de Dados.")
            return banco.criarProduto(requisicao.dadosRequisicao, requisicao.imagens)

    def _criarLoja(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar loja do Banco de Dados.")
            return banco.criarLoja(requisicao.idAssociado, requisicao.dadosRequisicao, requisicao.imagens)

    def _criarPedido(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar pedido do Banco de Dados.")

            respostaBanco = banco.criarPedido(requisicao.dadosRequisicao)

            idPedido = respostaBanco.get("id")

            vendedor = banco.retornarVendedorPedido(idPedido)

            emailVendedor = vendedor.get("email")
            nomeVendedor = vendedor.get("nome")

            print(f"[Fila de Mensagens][Criar][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando email confirmando que o pedido do cliente foi realizado.")
            email = correio.ThreadEmail("pedido realizado", emailVendedor, nomeVendedor)
            email.start()

            print(f"[Fila de Mensagens][Criar][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar produto do Banco de Dados.")
            return respostaBanco

    def _criarEndereco(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar endereço do Banco de Dados.")
            return banco.criarEndereco(requisicao.idAssociado, requisicao.dadosRequisicao)

    def _criarImagem(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Criar][Imagem][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de criar imagem do Banco de Dados.")
            return banco.criarImagemProduto(requisicao.dadosRequisicao, requisicao.imagens)

    def _excluirAnuncio(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Excluir][Anúncio][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de excluir anúncio do Banco de Dados.")
            return banco.excluirAnuncio(requisicao.dadosRequisicao)

    def _excluirProduto(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Excluir][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de excluir produto do Banco de Dados.")
            return banco.excluirProduto(requisicao.dadosRequisicao)

    def _excluirLoja(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Excluir][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de excluir loja do Banco de Dados.")
            return banco.excluirLoja(requisicao.dadosRequisicao)

    def _excluirEndereco(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Excluir][Endereço][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de excluir endereço do Banco de Dados.")
            return banco.excluirEndereco(requisicao.dadosRequisicao)

    def _excluirImagem(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Excluir][Imagem][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de excluir anúncio do Banco de Dados.")
            return banco.excluirImagemProduto(requisicao.dadosRequisicao)



    def _pegarImagemProduto(self, requisicao: Requisicao):
        """
        Essa função pede uma imagem do banco de dados enviando o nome dela na requisição.
        Requisição:
            ID: <id da requisicao>
            TIPO: 'imagem_produto'
            DADOS: <nome da imagem>
            IMAGENS: None
            ID ASSOCIADO: None
        """

        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Imagem][Produto][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de retornar imagem de um produto do Banco de Dados.")
            return banco.retornarImagem("produto", requisicao.dadosRequisicao)

    def _pegarImagemLoja(self, requisicao: Requisicao):
        """
        Essa função pede uma imagem do banco de dados enviando o nome dela na requisição.
        Requisição:
            ID: <id da requisicao>
            TIPO: 'imagem_loja'
            DADOS: <nome da imagem>
            IMAGENS: None
            ID ASSOCIADO: None
        """

        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Imagem][Loja][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de retornar imagem de uma loja do Banco de Dados.")
            return banco.retornarImagem("loja", requisicao.dadosRequisicao)

    def _pegarImagemPedido(self, requisicao: Requisicao):
        """
        Essa função pede uma imagem do banco de dados enviando o nome dela na requisição.
        Requisição:
            ID: <id da requisicao>
            TIPO: 'imagem_loja'
            DADOS: <nome da imagem>
            IMAGENS: None
            ID ASSOCIADO: None
        """

        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print(f"[Fila de Mensagens][Imagem][Pedido][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Chamando função de retornar imagem de um pedido do Banco de Dados.")
            return banco.retornarImagem("produto", requisicao.dadosRequisicao)

    def _confirmarPedido(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Pedido][Confirmar] Chamando função de confirmar pedido do Banco de Dados.")
            resposta = banco.confirmarPedido(requisicao.dadosRequisicao)

            if resposta is (True or "ok"):
                usuario = banco.retornarCompradorPedido(requisicao.dadosRequisicao)

                emailUsuario = usuario.get("email")
                nomeUsuario = usuario.get("nome")

                print(f"[Fila de Mensagens][Pedido][Confirmar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando email confirmando que o pedido do cliente foi confirmado.")
                email = correio.ThreadEmail("confirmacao pedido", emailUsuario, nomeUsuario)
                email.start()

            return resposta


    def _cancelarPedido(self, requisicao: Requisicao):
        with Pyro5.api.Proxy(self.bancoURI) as banco:
            print("[Fila de Mensagens][Pedido][Cancelar] Chamando função de cancelar pedido do Banco de Dados.")
            usuario = banco.retornarCompradorPedido(requisicao.dadosRequisicao)
            resposta = banco.cancelarPedido(requisicao.dadosRequisicao)

            if resposta is (True or "ok"):
                emailUsuario = usuario.get("email")
                nomeUsuario = usuario.get("nome")

                print(f"[Fila de Mensagens][Pedido][Confirmar][ID: {requisicao.idRequisicao[:3]}...{requisicao.idRequisicao[-3:]}] Enviando email confirmando que o pedido do cliente foi cancelado.")
                email = correio.ThreadEmail("cancelamento pedido", emailUsuario, nomeUsuario)
                email.start()

            return resposta

    def conectaBanco(self):
        print("[Fila de Mensagens] Conectando ao Banco de Dados via Pyro5...")
        ns = Pyro5.api.locate_ns(host='192.168.1.17', port=5000)
        print("[Fila de Mensagens] Tentando fazer o lookup.")
        self.bancoURI = ns.lookup("Caldeirao:servicos.banqueiro")
        print(f"[Fila de Mensagens] URI do Banco de Dados: {self.bancoURI}")

    def esperarRespostaDoBancoDeRespostas(self, requisicao: Requisicao):
        return self._respostas.esperaResposta(requisicao.idRequisicao)
    
    def registraRequisicao(self, requisicao: Requisicao):
        self._respostas.criaRequisicao(requisicao.idRequisicao)