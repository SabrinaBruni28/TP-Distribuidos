import json
import socket
import threading
import logging
import sys, os

# Adiciona o diretório raiz ao sys.path
CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(CAMINHO_BASE)
from banqueiro import Banqueiro
from models.usuario import Usuario_Identificado
from models.endereco import Endereco
from models.loja import Loja
from models.produto import Produto
from models.anuncio import Anuncio
from models.pedido import Pedido
from models.imagem_produto import Imagem_Produto

logging.basicConfig(level=logging.INFO, format='%(message)s')
espacito = 100
img_path = 'db/img'

class Mensagem():
    def __init__(self, string_ou_imagem):
        self.codigoMensagem = self._empacota(string_ou_imagem)
        self.stringMensagem = self._stringifica(string_ou_imagem)
        self.camposMensagem = self._divideString()
        self.tamanho = len(self.camposMensagem)

    def _divideString(self):
        return [ws.strip() for ws in self.stringMensagem.split('|')]
    
    def _empacota(self, string_ou_imagem):
        if isinstance(string_ou_imagem, str):
            string_ou_imagem = string_ou_imagem.encode('utf-8')
        return string_ou_imagem
    
    def _stringifica(self, string_ou_imagem):
        if isinstance(string_ou_imagem, bytes):
            string_ou_imagem = string_ou_imagem.decode(errors='ignore')
        return string_ou_imagem
    
    def __str__(self):
        return f'Mensagem(string = {self.stringMensagem})'

class UnixSocketServer:
    def __init__(self, host='0.0.0.0', port=6000):
        self.banqueiro = Banqueiro()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f'Banco de Dados ouvindo em {self.host}:{self.port}\n')

    def start(self):
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f'Conexão aceita de {addr}'.center(espacito, '='))
                threading.Thread(target=self.handle_server, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print('Encerrando servidor...')
        finally:
            self.server_socket.close()

    def handle_server(self, client_socket):
        try:
            import time
            while True:

                respostas = []
                continua_recebendo = []

                try:
                    tamanho = self.receive_size(client_socket)
                    print(f"[Handle Server] Tamanho: {tamanho}")
                    requisicao = self.receive_data(client_socket, tamanho)
                    print(f"[Handle Server] Requisição: {str(requisicao.decode())}\n")
                except Exception as e:
                    print(f"Erro ao receber dados: {e}")
                    break

                if requisicao:
                    mensagem_principal = Mensagem(requisicao)
                    print(f'Recebido ({tamanho} bytes):', mensagem_principal.stringMensagem, end='\n\n')

                    continua_recebendo, respostas = self.decisor(mensagem_principal)
                    print(f"respostas: {respostas}")
                    print(f"continua_recebendo: {continua_recebendo}")
                    for caminho_imagem in continua_recebendo:
                        caminho_imagem = os.path.join(CAMINHO_BASE, img_path, caminho_imagem)
                        print(caminho_imagem)
                        salvo, imagem = self.receive_image(client_socket, image_path = caminho_imagem)
                        print('Imagem salva? ->', salvo)
                        if salvo:
                            respostas.append(Mensagem(imagem))
                    print('Mensagens a enviar: ', len(respostas))
                    for i in range(len(respostas)):
                        self.send(client_socket, respostas[i].codigoMensagem)
                        time.sleep(0.01)  # Pequeno delay para evitar congestionamento do buffer

                    print()
                    print(espacito*'-')
                    # Limpa variáveis para liberar memória
                    respostas.clear()
                    continua_recebendo.clear()
                else:
                    print('Cliente desconectado'.center(espacito, '='))
                    break
        except Exception as e:
            import traceback
            print('Erro com cliente:', e)
            traceback.print_exc()
        finally:
            client_socket.close()
    
    def decisor(self, requisicao: Mensagem):
        respostas = [Mensagem('erro | falha desconhecida')]
        continua_recebendo = []
        obj = None
        msg = ''
        match requisicao.camposMensagem[0]:

            case 'login':
                usuarioLogando = Usuario_Identificado.from_dict(json.loads(requisicao.camposMensagem[1]))
                if usuario := self.banqueiro.encontrar(usuarioLogando):
                    respostas = [Mensagem('ok | ' + json.dumps(usuario.to_dict()))]
                else:
                    respostas = [Mensagem('erro | dados_incorretos')]
            
            case 'confere':
                match requisicao.camposMensagem[1]:
                    case 'usuario':
                        usuarioConferindo = Usuario_Identificado.from_dict(json.loads(requisicao.camposMensagem[2]))
                        msg, validacao = self.banqueiro.conferir(usuarioConferindo, ['cpf', 'email'])
                        respostas = [Mensagem(f'{msg} | {validacao}')]
                    case _:
                        print('Erro na mensagem: Segundo cabeçalho não reconhecido!')
            
            case 'criar':
                match requisicao.camposMensagem[1]:
                    case 'usuario':
                        msg = 'ok'
                        obj = Usuario_Identificado.from_dict(json.loads(requisicao.camposMensagem[2]))
                    case 'endereco':
                        msg = 'endereco'
                        obj = Endereco.from_dict(json.loads(requisicao.camposMensagem[3]))
                        obj.id_usuario = int(requisicao.camposMensagem[2])
                    case 'loja':
                        msg = 'loja'
                        loja = Loja.from_dict(json.loads(requisicao.camposMensagem[3]))
                        loja.id_usuario = int(requisicao.camposMensagem[2])
                        loja.id = self.banqueiro.criar(loja)
                        print(loja)
                        respostas = [Mensagem(f"{msg} | {json.dumps(loja.to_dict())}")]
                        print(loja.imagem, bool(loja.imagem))
                        if loja.imagem:
                            continua_recebendo = [f'loja/{loja.id}.jpg']
                    case 'produto':
                        msg = 'produto'
                        produto_dict = json.loads(requisicao.camposMensagem[2])
                        print(produto_dict)
                        produto = Produto.from_dict(produto_dict)
                        print(produto)
                        produto.id = self.banqueiro.criar(produto)
                        imagens_renomeado = []
                        for imagem in produto.imagens:
                            imagem = f'{self.banqueiro.criar(Imagem_Produto(id_produto = produto.id))}_{produto.id}.jpg'
                            imagens_renomeado.append(imagem)
                            continua_recebendo = [f'produto/{imagem}']
                            continua_recebendo.extend([f'produto/{imagem}'])

                        produto.imagens = imagens_renomeado
                        respostas = [Mensagem(f"{msg} | {json.dumps(produto.to_dict())}")]
                    case 'anuncio':
                        msg = 'anuncio'
                        obj = Anuncio.from_dict(json.loads(requisicao.camposMensagem[2]))
                    case 'pedido':
                        msg = 'pedido'
                        obj = Pedido.from_dict(json.loads(requisicao.camposMensagem[3]))
                        obj.endereco.id_usuario = int(requisicao.camposMensagem[2])
                    case 'imagem':
                        msg = 'imagem'
                        imagem_produto = Imagem_Produto(
                            id_produto = int(requisicao.camposMensagem[2]))
                        imagem_produto.id = self.banqueiro.criar(imagem_produto)
                        respostas = [Mensagem(f"{msg} | {imagem_produto.caminho()}")]
                        continua_recebendo = [f'produto/{imagem_produto.caminho()}']
                    case _:
                        print('Erro na mensagem: Segundo cabeçalho não reconhecido!')
                if msg and obj is not None:
                    obj.id = self.banqueiro.criar(obj)
                    respostas = [Mensagem(f"{msg} | {json.dumps(obj.to_dict())}")]
                    
            case 'retornar':
                cabecalho2 = requisicao.camposMensagem[1]
                match cabecalho2:
                    case 'anuncios':
                        anuncios = self.banqueiro.buscar(Anuncio())
                        respostas = [Mensagem(f'anuncios | {len(anuncios)}')]
                        for anuncio in anuncios:
                            respostas.append(Mensagem(json.dumps(anuncio.to_dict())))
                        print("Resposta:", respostas)
                    case 'anuncio':
                        if anuncio := self.banqueiro.encontrar(Produto(id = int(requisicao.camposMensagem[2]))):
                            if isinstance(anuncio, Anuncio):
                                if anuncio.produto:
                                    if produto := self.banqueiro.encontrar(Produto(id = anuncio.produto.id)):
                                        if isinstance(produto, Produto):
                                            for imagem_produto in self.banqueiro.buscar(Imagem_Produto(id_produto = produto.id)):
                                                produto.imagens.append(imagem_produto.caminho())
                                            anuncio.produto = produto
                                            respostas = [Mensagem(f'{cabecalho2} | {json.dumps(anuncio.to_dict())}')]
                                            for imagem in produto.imagens:
                                                respostas.append(Mensagem(self.read_image(os.path.join(CAMINHO_BASE, img_path, f'produto/{imagem}'))))
                                        else:
                                            print('Erro fatal: Produto não é do tipo Produto!')
                                    else:
                                        print('Erro fatal: Anuncio sem produto!')
                                else:
                                    print('Erro fatal: Anuncio sem produto!')
                            else:
                                print('Erro fatal: Anuncio não é do tipo Anuncio!')
                        else:
                            print('Erro fatal: Anuncio não encontrado!')
                    case 'produto':
                        if produto := self.banqueiro.encontrar(Produto(id = int(requisicao.camposMensagem[2]))):
                            if isinstance(produto, Produto):
                                print(produto)
                                for imagem_produto in self.banqueiro.buscar(Imagem_Produto(id_produto = produto.id)):
                                    print(imagem_produto)
                                    produto.imagens.append(imagem_produto.caminho())
                                respostas = [Mensagem(f'{cabecalho2} | {json.dumps(produto.to_dict())}')]
                                for imagem in produto.imagens:
                                    respostas.append(Mensagem(self.read_image(os.path.join(CAMINHO_BASE, img_path, f'produto/{imagem}'))))
                            else:
                                print('Erro fatal: Produto não é do tipo Produto!')
                        else:
                            print('Erro fatal: Produto não encontrado!')
                    case 'loja':
                        if loja := self.banqueiro.retornarLoja(Loja(id = int(requisicao.camposMensagem[2]))):
                            caminho_imagem = os.path.join(CAMINHO_BASE, img_path, f'loja/{loja.id}.jpg')
                            if os.path.exists(caminho_imagem):
                                loja.imagem = f'{loja.id}.jpg'
                            for produto in loja.produtos:
                                produto.imagens = []
                                for imagem_produto in self.banqueiro.buscar(Imagem_Produto(id_produto = produto.id)):
                                    produto.imagens.append(imagem_produto.caminho())
                            respostas = [Mensagem(f'{cabecalho2} | {json.dumps(loja.to_dict())}')]
                            if loja.imagem:
                                imagem = self.read_image(os.path.join(CAMINHO_BASE, img_path, f'loja/{loja.id}.jpg'))
                                respostas.append(Mensagem(imagem))
                            print('debugging:', loja.produtos)
                            for produto in loja.produtos:
                                imagem = self.read_image(os.path.join(CAMINHO_BASE, img_path, f'produto/{produto.imagens[0]}'))
                                respostas.append(Mensagem(imagem))
                        else:
                            print('Erro fatal: Loja não encontrada!')
                    case 'pedido':
                        pass
                    case 'minha_loja':
                        if minha_loja := self.banqueiro.retornarLoja(Loja(id = int(requisicao.camposMensagem[2])), minha = True):
                            caminho_imagem = os.path.join(CAMINHO_BASE, img_path, f'loja/{minha_loja.id}.jpg')
                            if os.path.exists(caminho_imagem):
                                minha_loja.imagem = f'{minha_loja.id}.jpg'
                            for produto in minha_loja.produtos:
                                produto.imagens = []
                                for imagem_produto in self.banqueiro.buscar(Imagem_Produto(id_produto = produto.id)):
                                    produto.imagens.append(imagem_produto.caminho())
                            respostas = [Mensagem(f'{cabecalho2} | {json.dumps(minha_loja.to_dict())}')]
                            #Não precisava:
                            #if minha_loja.imagem:
                            #    imagem = self.read_image(os.path.join(CAMINHO_BASE, img_path, f'loja/{minha_loja.id}.jpg'))
                            #    respostas.append(Mensagem(imagem))
                            for produto in minha_loja.produtos:
                                if produto.imagens:
                                    imagem = self.read_image(os.path.join(CAMINHO_BASE, img_path, f'produto/{produto.imagens[0]}'))
                                    respostas.append(Mensagem(imagem))
                        else:
                            print('Erro fatal: Loja não encontrada!')
                    case 'minhas_lojas':
                        minhas_lojas = self.banqueiro.buscar(Loja(id_usuario = int(requisicao.camposMensagem[2])))
                        respostas = [Mensagem(f'{cabecalho2} | {len(minhas_lojas)}')]
                        for loja in minhas_lojas:
                            caminho_imagem = os.path.join(CAMINHO_BASE, img_path, f'loja/{loja.id}.jpg')
                            if os.path.exists(caminho_imagem):
                                loja.imagem = f'{loja.id}.jpg'
                            respostas.append(Mensagem(f'{cabecalho2} | {json.dumps(loja.to_dict_personalisado())}'))
                            if loja.imagem:
                                imagem = self.read_image(os.path.join(CAMINHO_BASE, img_path, f'loja/{loja.id}.jpg'))
                                respostas.append(Mensagem(imagem))
                    case 'meus_enderecos':
                        meus_enderecos = self.banqueiro.buscar(Endereco(id_usuario = int(requisicao.camposMensagem[2])))
                        respostas = [Mensagem(f'{cabecalho2} | {len(meus_enderecos)}')]
                        for endereco in meus_enderecos:
                            respostas.append(Mensagem(f'{cabecalho2} | {json.dumps(endereco.to_dict())}'))
                    case 'meus_pedidos':
                        respostas = [Mensagem(f'{cabecalho2} | {2}')]
                    case _:
                        print('Erro na mensagem: Segundo cabeçalho não reconhecido!')
                #else:

            case "editar":
                match requisicao.camposMensagem[1]:
                    case 'usuario':
                        usuarioConferindo = Usuario_Identificado.from_dict(json.loads(requisicao.camposMensagem[2]))
                        msg, validacao = self.banqueiro.conferir(usuarioConferindo, ['cpf', 'email'])
                        print('Validação do usuário:', msg, validacao)
                        if msg == 'erro':
                            respostas = [Mensagem(f'{msg} | {validacao}')]
                        else:
                            obj = usuarioConferindo
                    case 'endereco':
                        msg = 'endereco'
                        obj = Endereco.from_dict(json.loads(requisicao.camposMensagem[2]))
                    case 'loja':
                        msg = 'loja'
                        loja_dict = json.loads(requisicao.camposMensagem[2])
                        ### Edição Breno
                        print(f"[Banco] Loja dict: {loja_dict}")
                        if 'imagem' in loja_dict:
                            print(f"[If imagem in loja_dict]")
                            if loja_dict['imagem']:
                                print(f"[If loja_dict[Imagem]]")
                                loja_dict['imagem'] = f'{loja_dict["id"]}.jpg'
                                continua_recebendo = [f'loja/{loja_dict["imagem"]}']
                            else:
                                print(f"[Else]")
                                self.remove_image(os.path.join(CAMINHO_BASE, img_path, f'loja/{loja_dict["id"]}.jpg'))
                        if 'nome' in loja_dict:
                            print(f"[If nome in loja_dict]")
                            obj = Loja.from_dict(loja_dict)
                            print("[Banco] Loja from dict: {obj}")
                        else:
                            print(f"[Big Bad Else]")
                            loja = self.banqueiro.retornarLoja(Loja.from_dict(loja_dict), minha = True)
                            loja.imagem = loja_dict.get('imagem', '')
                            respostas = [Mensagem(f'{msg} | {json.dumps(loja.to_dict())}')]
                    case 'produto':
                        obj = Produto.from_dict(json.loads(requisicao.camposMensagem[2]))
                        msg = 'produto'
                    case 'anuncio':
                        obj = Anuncio.from_dict(json.loads(requisicao.camposMensagem[2]))
                        msg = 'anuncio'
                    case 'pedido':
                        obj = Pedido.from_dict(json.loads(requisicao.camposMensagem[2]))
                        msg = 'pedido'
                    case _:
                        print('Erro na mensagem: Segundo cabeçalho não reconhecido!')

                if msg and obj is not None:
                    print(obj)
                    obj = self.banqueiro.editar(obj)
                    respostas = [Mensagem(f"{msg} | {json.dumps(obj.to_dict())}")]

            case "excluir":
                match requisicao.camposMensagem[1]:
                    case 'usuario':
                        obj = Usuario_Identificado(id = int(requisicao.camposMensagem[2]))
                    case 'endereco':
                        obj = Endereco(id = int(requisicao.camposMensagem[2]))
                    case 'loja':
                        obj = self.banqueiro.retornarLoja(Loja(id = int(requisicao.camposMensagem[2])))
                        self.remove_image(os.path.join(CAMINHO_BASE, img_path, f'loja/{obj.id}.jpg'))
                        for produto in obj.produtos:
                            self.decisor(Mensagem('excluir | produto | {produto.id}'))
                    case 'produto':
                        produto = Produto(id = int(requisicao.camposMensagem[2]))
                        for anuncio in self.banqueiro.buscar(Anuncio(produto = produto)):
                            self.decisor(Mensagem('excluir | anuncio | {anuncio.id}'))
                        imagens_a_remover, ans = self.banqueiro.excluirProduto(produto)
                        for imagem in imagens_a_remover:
                            self.remove_image(os.path.join(CAMINHO_BASE, img_path, f'produto/{imagem}'))
                    case 'anuncio':
                        obj = Anuncio(id = int(requisicao.camposMensagem[2]))
                    case 'pedido':
                        obj = Pedido(id = int(requisicao.camposMensagem[2]))
                    case 'imagem':
                        obj = Imagem_Produto(id = int(requisicao.camposMensagem[2]))
                    case _:
                        print('Erro na mensagem: Segundo cabeçalho não reconhecido!')
                if obj is not None:
                    ans = self.banqueiro.excluir(obj)
                    respostas = [Mensagem(f'{requisicao.camposMensagem[1]} | {ans}')]

            case _:
                print('Erro na mensagem: Primeiro cabeçalho não reconhecido!')
            
        return (continua_recebendo, respostas)

    def send_size(self, soquete, tamanho: int):
        soquete.sendall(tamanho.to_bytes(8, 'big'))

    def receive_size(self, soquete):
        tamanho_bytes = soquete.recv(8)
        if not tamanho_bytes:
            raise ConnectionError("Cliente desconectado ao ler tamanho")
        return int.from_bytes(tamanho_bytes, 'big')

    def receive_data(self, soquete, tamanho):
        data = b''
        while len(data) < tamanho:
            chunk = soquete.recv(min(4096, tamanho - len(data)))
            if not chunk:
                break
            data += chunk
        return data
    
    def receive_image(self, soquete, buffer_size=4096, image_path=''):
        salvo = False
        data = b''
        if not soquete:
            print('Soquete inválido em recieve_image()!')
            return (salvo, data)
        try:
            tamanho_total = self.receive_size(soquete)
            with open(image_path, 'wb') as f:
                while len(data) < tamanho_total:
                    chunk = soquete.recv(buffer_size)
                    if not chunk:
                        break
                    data += chunk
                    diferenca = tamanho_total - len(data)
                    if diferenca < buffer_size:
                        buffer_size = diferenca
                f.write(data)
                print("Imagem salva:", image_path)
                salvo = True
        except FileNotFoundError:
            print(f'Arquivo "{image_path}" não encontrado.')
        except PermissionError:
            print(f'Sem permissão para escrever imagem "{image_path}".')
        except Exception as e:
            print(f'Erro ao receber imagem: {e}')
        finally:
            return (salvo, data)
    
    def read_image(self, image_path: str):
        data = b''
        try:
            with open(image_path, 'rb') as f:
                data = f.read()
                tamanho = len(data)
            print("Lê Imagem:", image_path)
        except FileNotFoundError:
            print(f"Arquivo '{image_path}' não encontrado.")
        except PermissionError:
            print(f"Sem permissão para ler '{image_path}'.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
        finally:
            return data
    
    def remove_image(self, image_path: str):
        try:
            os.remove(image_path)
            print(f"Arquivo '{image_path}' apagado com sucesso.")
        except FileNotFoundError:
            print(f"Arquivo '{image_path}' não encontrado.")
        except PermissionError:
            print(f"Sem permissão para apagar '{image_path}'.")
        except Exception as e:
            print(f'Erro ao apagar o arquivo: {e}')

    
    def send(self, soquete, data: bytes):
        if not soquete:
            return False
        tamanho = len(data)
        self.send_size(soquete, tamanho)
        soquete.sendall(data)
        print(f'Enviando {tamanho} bytes: ', data[:150], '...')

server = UnixSocketServer(host='192.168.1.15')
server.start()
