import socket
import json
from Operacoes import thread_email as correio
from Estruturas.mensagem import Mensagem
from Operacoes import server_operation as op

# Callback da requisição de Login. O servidor deve retornar dois tipos de resposta ao cliente nesse caso:
# ok | dados do cliente     -> Em caso do login ser confirmado no banco de dados.
# erro | dados incorretos   -> Em caso dos dados de login não terem sido encontrados no banco de dados.
def loginCallback(respostaBD, socket_cliente):
    resposta = [ws.strip() for ws in respostaBD.split('|')]
    
    if resposta[0] == "ok":
        mensagemAoCliente = Mensagem.produtorMensagem(f"ok | {resposta[1]}")
        print("[Servidor] Confirmando login do cliente...")

    else:
        mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta[1]}")
        print("[Servidor] Reportando erro de login ao cliente...")


    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def cadastramentoCallback(resposta_banco, socket_cliente, socket_servidor, fila):
        resposta = [ws.strip() for ws in resposta_banco.split('|')]
        dados = json.loads(resposta[1])
        dadosJson = (dados)

        signupHandler(dadosJson, resposta, socket_cliente, fila)

def signupHandler(dadosJson, resposta, cliente: socket.socket, fila):
        if resposta[0] == "ok":
            emailCliente = dadosJson.get("email")
            print(f"[SignupHandler] Email: {emailCliente}")
            email = correio.ThreadEmail("confirmacao cadastro", emailCliente)            
            email.start()

            codigoConfirmacao = str(email.codigo)

            fila.dadosTemp.armazenar(cliente, codigoConfirmacao, dadosJson)

            mensagemAoCliente = Mensagem.produtorMensagem(f"email_confirmacao")
            print("[Servidor] Esperando confirmação de email do cliente...")

        else:
            mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta[1]}")
            print("[Servidor] Reportando erro de cadastro...")

        op.enviaMensagem(cliente, mensagemAoCliente)

def visualizarTodosAnunciosCallback(resposta_banco, socket_cliente, socket_banco):
    quantidadeAnuncios = int(resposta_banco[1])
    anuncios = []

    for i in range(quantidadeAnuncios):
        try:
            mensagemNovoAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
            mensagemImagemNovoAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)

            dicioAnuncioImg = {
                "anuncio": mensagemNovoAnuncio,
                "imagem": mensagemImagemNovoAnuncio
                }

            anuncios.append(dicioAnuncioImg)
        
        except Exception as e:
             print(f"[Servidor][Visualizar] Problema ao ler anuncio do servidor: {e}")
             break
        
    enviaSequenciaAnuncios(socket_cliente, anuncios)
        
def enviaSequenciaAnuncios(socket_cliente, anuncios):
    for anuncio in anuncios:
        mensagemAnuncio = Mensagem.produtorMensagem(anuncio.get("anuncio"))
        mensagemImagem = Mensagem.produtorMensagem(anuncio.get("imagem"))
        op.enviaMensagem(socket_cliente, mensagemAnuncio)
        op.enviaMensagem(socket_cliente, mensagemImagem)

def visualizarAnuncioCallback(resposta_banco, socket_cliente, socket_banco):
    imagens = []
    mensagemQuantidadeImg = 0

    try:
        retornoQuantidade = Mensagem.receptorMensagemETamanho(socket_banco)
        quantidadeImagens = int(retornoQuantidade.camposMensagem[1])
        mensagemQuantidadeImg = quantidadeImagens

        for i in range(mensagemQuantidadeImg):
            try:
                novaImagemAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
                imagens.append(novaImagemAnuncio.stringMensagem)

            except Exception as e:
                print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
                break

    except Exception:
         return
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    mensagemQuantidadeImgAoCliente = Mensagem.produtorMensagem(str(len(imagens)))
    op.enviaMensagem(socket_cliente, mensagemQuantidadeImgAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def enviaSequencialmenteImagens(socket_cliente, imagens):
     for imagem in imagens:
        mensagemImagem = Mensagem.produtorMensagem(imagem)
        op.enviaMensagem(socket_cliente, mensagemImagem)

def visualizarProdutoCallback(resposta_banco, socket_cliente, socket_banco):
    imagens = []
    mensagemQuantidadeImg = 0

    try:
        retornoQuantidade = Mensagem.receptorMensagemETamanho(socket_banco)
        quantidadeImagens = int(retornoQuantidade.camposMensagem[1])
        mensagemQuantidadeImg = quantidadeImagens

        for i in range(mensagemQuantidadeImg):
            try:
                novaImagemAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
                imagens.append(novaImagemAnuncio.stringMensagem)

            except Exception as e:
                print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
                break

    except Exception:
         return
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    mensagemQuantidadeImgAoCliente = Mensagem.produtorMensagem(str(len(imagens)))
    op.enviaMensagem(socket_cliente, mensagemQuantidadeImgAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def visualizarPedidoCallback(resposta_banco, socket_cliente, socket_banco):
    imagens = []
    mensagemQuantidadeImg = 0

    try:
        retornoQuantidade = Mensagem.receptorMensagemETamanho(socket_banco)
        quantidadeImagens = int(retornoQuantidade.camposMensagem[1])
        mensagemQuantidadeImg = quantidadeImagens

        for i in range(mensagemQuantidadeImg):
            try:
                novaImagemAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
                imagens.append(novaImagemAnuncio.stringMensagem)

            except Exception as e:
                print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
                break

    except Exception:
         return
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"pedido | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    mensagemQuantidadeImgAoCliente = Mensagem.produtorMensagem(str(len(imagens)))
    op.enviaMensagem(socket_cliente, mensagemQuantidadeImgAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def visualizarLojaCallback(resposta_banco, socket_cliente, socket_banco):
    imagens = []
    mensagemQuantidadeImg = 0

    try:
        retornoQuantidade = Mensagem.receptorMensagemETamanho(socket_banco)
        quantidadeImagens = int(retornoQuantidade.camposMensagem[1])
        mensagemQuantidadeImg = quantidadeImagens

        for i in range(mensagemQuantidadeImg):
            try:
                novaImagemAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
                imagens.append(novaImagemAnuncio.stringMensagem)

            except Exception as e:
                print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
                break

    except Exception:
         return
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    mensagemQuantidadeImgAoCliente = Mensagem.produtorMensagem(str(len(imagens)))
    op.enviaMensagem(socket_cliente, mensagemQuantidadeImgAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def visualizarLojaUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    imagens = []
    mensagemQuantidadeImg = 0

    try:
        retornoQuantidade = Mensagem.receptorMensagemETamanho(socket_banco)
        quantidadeImagens = int(retornoQuantidade.camposMensagem[1])
        mensagemQuantidadeImg = quantidadeImagens

        for i in range(mensagemQuantidadeImg):
            try:
                novaImagemAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)
                imagens.append(novaImagemAnuncio.stringMensagem)

            except Exception as e:
                print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
                break

    except Exception:
         return
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"minha_loja | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    mensagemQuantidadeImgAoCliente = Mensagem.produtorMensagem(str(len(imagens)))
    op.enviaMensagem(socket_cliente, mensagemQuantidadeImgAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def visualizarListaLojasUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    lojas = []
    quantidadeLojas = int(resposta_banco[1])

    for i in range(quantidadeLojas):
        try:
            mensagemLoja = Mensagem.produtorMensagem(socket_banco)
            mensagemImagemLoja = Mensagem.produtorMensagem(socket_banco)

            dicio = {
                "loja": mensagemLoja.stringMensagem,
                "imagem": mensagemImagemLoja.stringMensagem
            }

            lojas.append(dicio)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler loja: {e}")
            break

    mensagemAoCliente = Mensagem.produtorMensagem(f"minhas_lojas | {str(len(lojas))}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequenciaLojas(socket_cliente, lojas)

def enviaSequenciaLojas(socket_cliente, lojas):
    for loja in lojas:
        mensagemLoja = Mensagem.produtorMensagem(loja.get("loja"))
        mensagemImagem = Mensagem.produtorMensagem(loja.get("imagem"))
        op.enviaMensagem(socket_cliente, mensagemLoja)
        op.enviaMensagem(socket_cliente, mensagemImagem)

def visualizarEnderecosUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    enderecos = []
    quantidadeEnderecos = int(resposta_banco[1])

    for i in range(quantidadeEnderecos):
        try:
            mensagemEndereco = Mensagem.produtorMensagem(socket_banco)
            enderecos.append(mensagemEndereco.stringMensagem)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler endereço: {e}")
            break

    mensagemAoCliente = Mensagem.produtorMensagem(f"meus_enderecos | {str(len(enderecos))}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequenciaEnderecos(socket_cliente, enderecos)

def enviaSequenciaEnderecos(socket_cliente, enderecos):
    for endereco in enderecos:
        mensagemEndereco = Mensagem.produtorMensagem(endereco)
        op.enviaMensagem(socket_cliente, mensagemEndereco)

def visualizarListaPedidosUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    pedidos = []
    quantidadePedidos = int(resposta_banco[1])

    for i in range(quantidadePedidos):
        try:
            mensagemPedido = Mensagem.produtorMensagem(socket_banco)
            pedidos.append(mensagemPedido.stringMensagem)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler pedido: {e}")
            break

    mensagemAoCliente = Mensagem.produtorMensagem(f"meus_pedidos | {str(len(pedidos))}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequenciaPedidos(socket_cliente, pedidos)

def enviaSequenciaPedidos(socket_cliente, pedidos):
    for pedido in pedidos:
        mensagemPedido = Mensagem.produtorMensagem(pedido)
        op.enviaMensagem(socket_cliente, mensagemPedido)

def editarAnuncioCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def editarProdutoCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def editarLojaCallback(resposta, socket_cliente, imagem: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    mensagemImagem = Mensagem.produtorMensagem(f"{imagem[0]}")
    op.enviaMensagem(socket_cliente, mensagemImagem)

def editarEnderecoCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def editarUsuarioCallback(resposta, socket_cliente):
    if resposta[0] == "ok":
        mensagemAoCliente = Mensagem.produtorMensagem(f"usuario | {resposta[1]}")

    else:
        mensagemAoCliente = Mensagem.produtorMensagem(f"erro | campos com problema")

    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def criarProdutoCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"pedido | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def criarLojaCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def criarImagemCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"imagem | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)

def criarAnuncioCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def criarPedidoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"pedido | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def criarEnderecoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def excluirAnuncioCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def excluirProdutoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def excluirLojaCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def excluirEnderecoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def excluirImagemCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"imagem | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def pedidoConfirmadoCallback(socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"ok | confirmado")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def pedidoCanceladoCallback(socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"ok | cancelado")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)