import socket
import json
from Operacoes import thread_email as correio
from Estruturas.mensagem import Mensagem
from Operacoes import server_operation as op

# Callback da requisição de Login. O servidor deve retornar dois tipos de resposta ao cliente nesse caso:
# ok | dados do cliente     -> Em caso do login ser confirmado no banco de dados.
# erro | dados incorretos   -> Em caso dos dados de login não terem sido encontrados no banco de dados.
def loginCallback(respostaBD, socket_cliente):
    resposta = respostaBD.camposMensagem
    if resposta[0] == "ok":
        mensagemAoCliente = Mensagem.produtorMensagem(f"ok | {resposta[1]}")
        print("[Servidor][Login] LOGIN REALIZADO COM SUCESSO!\n")

    else:
        mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta[1]}")
        print("[Servidor] Reportando erro de login ao cliente...")


    op.enviaMensagem(socket_cliente, mensagemAoCliente)

def cadastramentoCallback(resposta_banco: Mensagem, socket_cliente, fila, mensagem):
        resposta = resposta_banco.camposMensagem
        print(f"[CadastramentoCallback] Resposta[0]: {resposta[0]}")
        print(f"[CadastramentoCallback] Resposta[1]: {resposta[1]}")
        
        cadastramentoCallbackDecisor(resposta, socket_cliente, fila, mensagem)

def cadastramentoCallbackDecisor(resposta_banco, socket_cliente, fila, mensagem_servidor: Mensagem):
    if resposta_banco[0] == "erro":
        print("[Servidor][CadastramentoCallback] Erro no cadastramento.")
        mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta_banco[1]}")
        op.enviaMensagem(socket_cliente, mensagemAoCliente)
        return

    if resposta_banco[0] == "ok":
        dadosJson = json.loads(mensagem_servidor.camposMensagem[2])
        signupHandler(dadosJson, resposta_banco, socket_cliente, fila)

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
            mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {json.dumps(dadosJson)}")
            print("[Servidor][Cadastramento] Reportando erro de cadastro...")

        op.enviaMensagem(cliente, mensagemAoCliente)

def visualizarTodosAnunciosCallback(resposta_banco, socket_cliente, socket_banco):
    # resposta_banco tem [anuncios | quantidade]
    quantidadeAnuncios = int(resposta_banco[1])
    print(f"[Servidor] {quantidadeAnuncios}")
    anuncios = []

    for i in range(quantidadeAnuncios):
        try:
            mensagemNovoAnuncio = Mensagem.receptorMensagemETamanho(socket_banco)

            #print(f"[Servidor][Vizualizar Todos Anúncios] Anúncio: {mensagemNovoAnuncio.stringMensagem}\n")

            #mensagemImagemNovoAnuncio, path = op.receive_image()
            mensagemImagemNovoAnuncio = Mensagem.receptorImagem(socket_banco)

            #print(f"[Servidor][Vizualizar blá blá blá] imagem{mensagemImagemNovoAnuncio.stringMensagem}")

            dicioAnuncioImg = {
                "anuncio": mensagemNovoAnuncio,
                "imagem": mensagemImagemNovoAnuncio
                }

            anuncios.append(dicioAnuncioImg)
        
        except Exception as e:
             print(f"[Servidor][Visualizar] Problema ao ler anuncio do servidor: {e}")
             break
        
    quantidadeCliente = Mensagem.produtorMensagem(f"{str(quantidadeAnuncios)}")
    print(f"[Servidor][Visualizar Todos Anúncios] Quantidade definitiva: {quantidadeCliente.stringMensagem}")

    byteQ = quantidadeAnuncios.to_bytes(8, 'big')
    socket_cliente.sendall(byteQ)
        
    enviaSequenciaAnuncios(socket_cliente, anuncios)
    print("[Servidor][Visualizar] ANÚNCIOS RETORNADOS COM SUCESSO!\n")
        
def enviaSequenciaAnuncios(socket_cliente, anuncios):
    for anuncio in anuncios:
        mensagemAnuncio = Mensagem.produtorMensagem(f'anuncios | {(anuncio.get("anuncio")).stringMensagem}')
        op.enviaMensagem(socket_cliente, mensagemAnuncio)
        op.enviaImagem(socket_cliente, anuncio.get("imagem"))

def visualizarAnuncioCallback(resposta_banco: list, socket_cliente, socket_banco):
    anuncio = json.loads(resposta_banco[1])
    produtoAnuncio = anuncio.get("produto")
    imagensAnuncio = produtoAnuncio.get("imagens")

    imagens = []

    quantidadeImagensAnuncio = len(imagensAnuncio)


    for i in range(quantidadeImagensAnuncio):
        try:
            novaImagemAnuncio = Mensagem.receptorImagem(socket_banco)
            imagens.append(novaImagemAnuncio)
        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
            break
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    byteQ = quantidadeImagensAnuncio.to_bytes(8, 'big')
    socket_cliente.sendall(byteQ)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Visualizar] ANÚNCIO RETORNADO COM SUCESSO!\n")

def enviaSequencialmenteImagens(socket_cliente, imagens):
    if imagens == None or len(imagens) <= 0:
         return


    for imagem in imagens:
        op.enviaImagem(socket_cliente, imagem)

def visualizarProdutoCallback(resposta_banco: list, socket_cliente, socket_banco):
    produto = json.loads(resposta_banco[1])
    imagensProduto = produto.get("imagens")

    imagens = []

    quantidadeImagensProduto = len(imagensProduto)


    for i in range(quantidadeImagensProduto):
        try:
            novaImagemProduto = Mensagem.receptorImagem(socket_banco)
            imagens.append(novaImagemProduto)
        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
            break
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Visualizar] PRODUTO RETORNADO COM SUCESSO!\n")

def visualizarPedidoCallback(resposta_banco, socket_cliente, socket_banco):
    pedido = json.loads(resposta_banco[1])
    produtoPedido = pedido.get("produto")
    imagensPedido = produtoPedido.get("imagens")

    imagens = []

    quantidadeImagensPedido = len(imagensPedido)


    for i in range(quantidadeImagensPedido):
        try:
            novaImagemPedido = Mensagem.receptorImagem(socket_banco)
            imagens.append(novaImagemPedido)
        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
            break
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"pedido | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Visualizar] PEDIDO RETORNADO COM SUCESSO!\n")

def visualizarLojaCallback(resposta_banco, socket_cliente, socket_banco):
    loja = json.loads(resposta_banco[1])
    produtoLoja = loja.get("produtos")

    imagens = []

    quantidadeImagensLoja = len(produtoLoja)

    if (len(loja.get("imagem"))) > 0:
        quantidadeImagensLoja = len(produtoLoja) + 1

    for i in range(quantidadeImagensLoja):
        try:
            novaImagem = Mensagem.receptorImagem(socket_banco)
            imagens.append(novaImagem)
        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
            break
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Visualizar] LOJA RETORNADA COM SUCESSO!\n")

def visualizarLojaUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    loja = json.loads(resposta_banco[1])
    produtoLoja = loja.get("produtos")

    imagens = []

    quantidadeImagensLoja = len(produtoLoja)


    for i in range(quantidadeImagensLoja):
        try:
            novaImagem = Mensagem.receptorImagem(socket_banco)
            imagens.append(novaImagem)
        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler imagem: {e}")
            break
    
    mensagemAoCliente = Mensagem.produtorMensagem(f"minha_loja | {resposta_banco[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Visualizar] LOJA DO USUÁRIO RETORNADA COM SUCESSO!\n")

def visualizarListaLojasUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    lojas = []
    quantidadeLojas = int(resposta_banco[1])

    for i in range(quantidadeLojas):
        try:
            mensagemLoja = Mensagem.receptorMensagemETamanho(socket_banco)
            print(f"[Servidor][Visualizar] Mensagem: {mensagemLoja.stringMensagem}")

            mensagemLojaObj = json.loads(mensagemLoja.camposMensagem[1])


            if (mensagemLojaObj.get("imagem") == "" ):
                mensagemImagemLoja = Mensagem.produtorMensagem('')
                print(f"[Servidor][Visualizar] Mensagem: {mensagemImagemLoja.tamanho}")
            else:
                mensagemImagemLoja = Mensagem.receptorImagem(socket_banco)

            dicio = {
                "loja": mensagemLoja,
                "imagem": mensagemImagemLoja
            }

            lojas.append(dicio)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler loja: {e}")
            break

    #mensagemAoCliente = Mensagem.produtorMensagem(f"{str(len(lojas))}")
    #op.enviaMensagem(socket_cliente, mensagemAoCliente)

    byteQ = quantidadeLojas.to_bytes(8, 'big')
    socket_cliente.sendall(byteQ)

    enviaSequenciaLojas(socket_cliente, lojas)
    print("[Servidor][Visualizar] LOJAS RETORNADAS COM SUCESSO!\n")

def enviaSequenciaLojas(socket_cliente, lojas):
    for loja in lojas:
        #mensagemLoja = Mensagem.produtorMensagem(f"{(loja.get("loja"))}")
        #mensagemImagem = Mensagem.produtorMensagem(loja.get("imagem"))
        op.enviaMensagem(socket_cliente, loja.get("loja"))


        if (loja.get("imagem")).stringMensagem != '':
            print("[E N V I A S E Q U E N C I A]")
            op.enviaImagem(socket_cliente, loja.get("imagem"))

def visualizarEnderecosUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    enderecos = []
    quantidadeEnderecos = int(resposta_banco[1])

    for i in range(quantidadeEnderecos):
        try:
            mensagemEndereco = Mensagem.receptorMensagemETamanho(socket_banco)
            enderecos.append(mensagemEndereco)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler endereço: {e}")
            break

    #mensagemAoCliente = Mensagem.produtorMensagem(f"{str(len(enderecos))}")
    #op.enviaMensagem(socket_cliente, mensagemAoCliente)

    byteQ = quantidadeEnderecos.to_bytes(8, 'big')
    socket_cliente.sendall(byteQ)

    enviaSequenciaEnderecos(socket_cliente, enderecos)
    print("[Servidor][Visualizar] ENDEREÇOS RETORNADOS COM SUCESSO!\n")

def enviaSequenciaEnderecos(socket_cliente, enderecos):
    for endereco in enderecos:
        #mensagemEndereco = Mensagem.produtorMensagem(f"{endereco}")
        op.enviaMensagem(socket_cliente, endereco)

def visualizarListaPedidosUsuarioCallback(resposta_banco, socket_cliente, socket_banco):
    pedidos = []
    quantidadePedidos = int(resposta_banco[1])

    for i in range(quantidadePedidos):
        try:

            mensagemPedido = Mensagem.receptorMensagemETamanho(socket_banco)
            pedidos.append(mensagemPedido)

        except Exception as e:
            print(f"[Servidor][Visualizar] Problema ao ler pedido: {e}")
            break

    #mensagemAoCliente = Mensagem.produtorMensagem(f"meus_pedidos | {str(len(pedidos))}")
    #op.enviaMensagem(socket_cliente, mensagemAoCliente)

    byteQ = quantidadePedidos.to_bytes(8, 'big')
    socket_cliente.sendall(byteQ)

    enviaSequenciaPedidos(socket_cliente, pedidos)
    print("[Servidor][Visualizar] PEDIDOS RETORNADOS COM SUCESSO!\n")

def enviaSequenciaPedidos(socket_cliente, pedidos):
    for pedido in pedidos:
        #mensagemPedido = Mensagem.produtorMensagem(f"{pedido}")
        op.enviaMensagem(socket_cliente, pedido)

def editarAnuncioCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Editar] ANÚNCIO EDITADO COM SUCESSO!\n")

def editarProdutoCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Editar] PRODUTO EDITADO COM SUCESSO!\n")

def editarLojaCallback(resposta, socket_cliente, imagem):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    
    if imagem != None:
        op.enviaImagem(socket_cliente, imagem[0])
    
    print("[Servidor][Editar] LOJA EDITADA COM SUCESSO!\n")

def editarEnderecoCallback(resposta, socket_cliente):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Editar] ENDEREÇO EDITADO COM SUCESSO!\n")

def editarUsuarioCallback(resposta, socket_cliente):
    if resposta[0] == "ok":
        mensagemAoCliente = Mensagem.produtorMensagem(f"usuario | {resposta[1]}")

    else:
        mensagemAoCliente = Mensagem.produtorMensagem(f"erro | {resposta[1]}")

    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Editar] USUÁRIO EDITADO COM SUCESSO!\n")

def criarProdutoCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Criar] PRODUTO CRIADO COM SUCESSO!\n")

def criarLojaCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Criar] LOJA CRIADA COM SUCESSO!\n")

def criarImagemCallback(resposta, socket_cliente: socket.socket, imagens: list):
    mensagemAoCliente = Mensagem.produtorMensagem(f"imagem | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)

    enviaSequencialmenteImagens(socket_cliente, imagens)
    print("[Servidor][Criar] IMAGEM CRIADA COM SUCESSO!\n")

def criarAnuncioCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Criar] ANÚNCIO CRIADO COM SUCESSO!\n")

def criarPedidoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"pedido | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Criar] PEDIDO CRIADO COM SUCESSO!\n")

def criarEnderecoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Criar] ENDEREÇO CRIADO COM SUCESSO!\n")

def excluirAnuncioCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"anuncio | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Excluir] ANÚNCIO COM SUCESSO!\n")

def excluirProdutoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"produto | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Excluir] PRODUTO EXCLUÍDO COM SUCESSO!\n")

def excluirLojaCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"loja | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Excluir] LOJA EXCLUÍDA COM SUCESSO!\n")

def excluirEnderecoCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"endereco | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Excluir] ENDEREÇO EXCLUÍDO COM SUCESSO!\n")

def excluirImagemCallback(resposta, socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"imagem | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Excluir] IMAGEM EXCLUÍDA COM SUCESSO!\n")

def pedidoConfirmadoCallback(socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"ok | confirmado")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Pedido] PEDIDO CONFIRMADO COM SUCESSO!\n")

def pedidoCanceladoCallback(socket_cliente: socket.socket):
    mensagemAoCliente = Mensagem.produtorMensagem(f"ok | cancelado")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Pedido] PEDIDO CANCELADO COM SUCESSO!\n")

def codigoCallback(resposta_banco: Mensagem, socket_cliente: socket.socket):
    resposta = resposta_banco.camposMensagem
    mensagemAoCliente = Mensagem.produtorMensagem(f"ok | {resposta[1]}")
    op.enviaMensagem(socket_cliente, mensagemAoCliente)
    print("[Servidor][Cadastramento] CADASTRAMENTO FEITO COM SUCESSO!\n")
        