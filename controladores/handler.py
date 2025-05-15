import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.loja import Loja
from models.anuncio import Anuncio
from models.produto import Produto
from models.usuario import Usuario_Identificado
from models.endereco import Endereco
from interface.forms import Formulario
from interface.widgets import WidgetHelper, ViewHelper, CaixaConfirmacao
from interface.thread import Threads
from models.pedido import Pedido
from controladores.aplicacao import ClienteAplicacao

from PyQt6.QtWidgets import (
   QDialog
)

class InterfaceHandler:
    def __init__(self, parent, stack):
        self.parent = parent
        self.stack = stack
        self.aplicacao = ClienteAplicacao()

    def visualizar(self, tela, funcao, *args, **kwargs):
        def ao_visualizar(resposta):
                if not resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Ocorreu um erro inesperado"
                    )
                    ViewHelper.set_tela(self.stack, -2)
        # Executa:
        Threads.executar_tela(
            tela=lambda: tela,
            acao=ao_visualizar,
            requisicao=lambda: self.aplicacao.chamar(funcao, *args, **kwargs)
        ) 

    def confirmar_codigo(self, formulario: Formulario):
        erro = formulario.validar_tipos({"Código": int})
        if erro:
            formulario.exibir_erros()
        else:
            valores = formulario.obter_valores()
            def ao_confirmar_codigo(resposta):
                if resposta[0]:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=20, paddingV=20,
                        mensagem="Cadastro realizado com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -4)

                elif resposta[1] == "codigo_invalido":
                    formulario.definir_erros_especificos({"Código": "Código de confirmação inválido"})
                    formulario.exibir_erros()

                elif resposta[1] == "limite_excedido":
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Limite de tentativas excedido!"
                    )
                    ViewHelper.set_tela(self.stack, -2)
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.email_confirmacao(valores),
                acao=ao_confirmar_codigo
            )

    def cadastrar(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {
                "Nome": str, "CPF": str, 
                "Email": str, "Senha": str
            }
        )
        if erro:
            formulario.exibir_erros()
        else:
            usuario = Usuario_Identificado(formulario.obter_valores())
            def ao_cadastrar(resposta):
                if isinstance(resposta, dict):
                    capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                    formulario.definir_erros_especificos(capitalizado)
                    formulario.exibir_erros()

                elif resposta:
                    ViewHelper.abrir_tela(self.stack, self.parent.tela_codigo_confirmacao)

                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Erro ao realizar cadastramento!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.cadastrar(usuario),
                acao=ao_cadastrar
            )

    def login(self, formulario: Formulario):
        erro = formulario.validar_tipos({"Email": str, "Senha": str})
        if erro:
            formulario.exibir_erros()
        else:
            usuario = Usuario_Identificado(formulario.obter_valores())
            def ao_login(resposta):
                if isinstance(resposta, dict):
                    capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                    formulario.definir_erros_especificos(capitalizado)
                    formulario.exibir_erros()

                elif resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Login realizado com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -2)

                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent,
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Erro ao realizar login!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.login(usuario),
                acao=ao_login
            )

    def criar_pedido(self, pedido: Pedido, anuncio: Anuncio):   
        def ao_criar_pedido(resposta):
            if resposta:
                anuncio.subtrair_quantidade(pedido.quantidade)
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#4CAF50",
                    largura=400, altura=50, paddingH=50, paddingV=50,
                    mensagem="Pedido Criado com Sucesso!"
                )
                ViewHelper.set_tela(self.stack,-3)
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent, 
                    backcolor="#f44336",
                    largura=400, altura=50, paddingH=50, paddingV=50,
                    mensagem="Erro ao criar pedido!"
                )
        # Executa:
        Threads.executar_mensagem(
            stack=self.stack,
            requisicao=lambda: self.aplicacao.criar_pedido(pedido),
            acao=ao_criar_pedido
        )
    
    def criar_loja(self, formulario: Formulario):
        erro = formulario.validar_tipos({"Nome": str})
        if erro:
            formulario.exibir_erros()
        else:
            loja = Loja.from_dict(formulario.obter_valores())  
            def ao_criar_loja(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Loja Criada com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack,-2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=50, paddingV=50,
                        mensagem="Erro ao criar loja!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.criar_loja(loja),
                acao=ao_criar_loja
            )          

    def criar_endereco(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            endereco = Endereco.from_dict(formulario.obter_valores())  
            def ao_criar_endereco(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Endereço Criado com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Erro ao criar endereço!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.criar_endereco(endereco),
                acao=ao_criar_endereco
            )

    def criar_produto(self, formulario: Formulario, loja: Loja):
        erro = formulario.validar_tipos(
            {"Nome": str, "Descrição": str, "Imagens": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            produto = Produto.from_dict(formulario.obter_valores())
            produto.loja = loja  
            def ao_criar_produto(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Produto Criado com Sucesso!"
                    )
                    ViewHelper.set_tela(-2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Erro ao criar produto!"
                    )

            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.criar_produto(produto),
                acao=ao_criar_produto
            )

    def criar_anuncio(self, formulario: Formulario, produto: Produto):
        erro = formulario.validar_tipos(
            {
                "Preço": float, "Quantidade Disponível": int, 
                "Chave Pix": str, "Pausado": bool
            }
        )
        if erro:
            formulario.exibir_erros()
        else:
            anuncio = Anuncio.from_dict(formulario.obter_valores())
            anuncio.produto = produto
            def ao_criar_anuncio(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Anúncio Criado com Sucesso!"
                    )
                    ViewHelper.set_tela(-3)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50, paddingH=50, paddingV=50,
                        mensagem="Erro ao criar anúncio!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.criar_anuncio(anuncio),
                acao=ao_criar_anuncio
            )

    def editar_produto(self, formulario: Formulario, produto: Produto):
        erro = formulario.validar_tipos(
            {"Nome": str, "Descrição": str, "Imagens": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Nome": produto.nome, 
                    "Descrição": produto.descricao, 
                    "Imagens": produto.imagens
                }
            )
            if valores_alterados:
                def ao_editar_produto(resposta):
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Produto Editado com Sucesso!"
                        )
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Erro ao editar produto!"
                        )
                # Executa:
                Threads.executar_mensagem(
                    stack=self.stack,
                    requisicao=lambda: self.aplicacao.editar_produto(produto, valores_alterados),
                    acao=ao_editar_produto
                )
                
            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#FFC107", fontcolor="#000000",
                    largura=400, altura=50, paddingH=50, paddingV=50,
                    mensagem="Nenhuma alteração realizada"
                )

    def editar_loja(self, formulario: Formulario, loja: Loja):
        erro =  formulario.validar_tipos({ "Nome": str})

        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Nome": loja.nome, "Imagem": loja.imagem
                }
            )
            if valores_alterados:
                def ao_editar_loja(resposta):
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Loja Editada com Sucesso!"
                        )
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Erro ao editar loja!"
                        )
                # Executa:
                Threads.executar_mensagem(
                    stack=self.stack,
                    requisicao=lambda: self.aplicacao.editar_loja(loja, valores_alterados),
                    acao=ao_editar_loja
                )

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#FFC107", fontcolor="#000000",
                    largura=400, altura=50, paddingH=50, paddingV=50,
                    mensagem="Nenhuma alteração realizada"
                )

    def editar_endereco(self, formulario: Formulario, endereco: Endereco):
        erro = formulario.validar_tipos(
            {"Rua": str, "N°": int, "Bairro": str, "Cidade": str, "Estado": str, "Complemento": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Rua": endereco.rua, "N°": endereco.numero, 
                    "Bairro": endereco.bairro, "Cidade": endereco.cidade, 
                    "Estado": endereco.estado, "Complemento": endereco.complemento
                }
            )
            if valores_alterados:
                def ao_editar_endereco(resposta):
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Endereço Editado com Sucesso!"
                        )
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Erro ao editar endereço!"
                        )
                # Executa:
                Threads.executar_mensagem(
                    stack=self.stack,
                    requisicao=lambda: self.aplicacao.editar_endereco(endereco, valores_alterados),
                    acao=ao_editar_endereco
                )

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#FFC107", fontcolor="#000000",
                    largura=400, altura=50,paddingH=50, paddingV=50,
                    mensagem="Nenhuma alteração realizada"
                )
    
    def editar_perfil(self, formulario: Formulario):
        erro = formulario.validar_tipos(
            {"Nome": str, "CPF": str, "Email": str, "Senha": str}
        )
        if erro:
            formulario.exibir_erros()
        else:
            usuario = self.aplicacao.usuario
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Nome": usuario.nome, "CPF": usuario.cpf, 
                    "Email": usuario.email, "Senha": "*"*len(usuario.senha),
                }
            )
            if valores_alterados:
                def ao_editar_perfil(resposta):
                    if isinstance(resposta, dict):
                        capitalizado = {chave.capitalize(): valor for chave, valor in resposta.items()}
                        formulario.definir_erros_especificos(capitalizado)
                        formulario.exibir_erros()
                    
                    elif resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Perfil Editado com Sucesso!"
                        )
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Erro ao editar perfil!"
                        )
                # Executa:
                Threads.executar_mensagem(
                    stack=self.stack,
                    requisicao=lambda: self.aplicacao.editar_usuario(valores_alterados),
                    acao=ao_editar_perfil
                )

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#FFC107", fontcolor="#000000",
                    largura=400, altura=50,paddingH=50, paddingV=50,
                    mensagem="Nenhuma alteração realizada"
                )
    
    def editar_anuncio(self, formulario: Formulario, anuncio: Anuncio):
        erro =  formulario.validar_tipos(
            {
                "Preço": float, "Quantidade Disponível": int, 
                "Chave Pix": str, "Pausado": bool
            }
        )
        if erro:
            formulario.exibir_erros()
        else:
            valores_alterados = formulario.obter_valores_alterados(
                {
                    "Preço": anuncio.preco, 
                    "Quantidade Disponível": anuncio.quantidade_disponivel, 
                    "Chave Pix": anuncio.chave_pix, 
                    "Pausado": anuncio.pausado
                }
            )
            if valores_alterados:
                def ao_editar_anuncio(resposta):
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Anúncio Editado com Sucesso!"
                        )
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=50, paddingV=50,
                            mensagem="Erro ao editar anúncio!"
                        )
                # Executa:
                Threads.executar_mensagem(
                    stack=self.stack,
                    requisicao=lambda: self.aplicacao.editar_anuncio(anuncio, valores_alterados),
                    acao=ao_editar_anuncio
                )

            else:
                WidgetHelper.mostrar_alerta_temporario(
                    parent_widget=self.parent,
                    backcolor="#FFC107", fontcolor="#000000",
                    largura=400, altura=50, paddingH=50, paddingV=50,
                    mensagem="Nenhuma alteração realizada"
                )

    def excluir_loja(self, loja: Loja):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar excluir loja",
            mensagem=f"Você tem certeza que deseja excluir loja {loja.nome}?",
            largura=420
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_loja(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=920, paddingV=920,
                        mensagem="Loja Excluída com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -3)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=920, paddingV=920,
                        mensagem="Erro ao excluir loja!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.excluir_loja(loja),
                acao=ao_excluir_loja
            )

        else:
            dialogo.close()

    def excluir_produto(self, produto: Produto):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar excluir produto",
            mensagem=f"Você tem certeza que deseja excluir produto {produto.nome}?",
            largura=420
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_produto(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=920, paddingV=100,
                        mensagem="Produto Excluído com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=920, paddingV=100,
                        mensagem="Erro ao excluir produto!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.excluir_produto(produto),
                acao=ao_excluir_produto
            )

        else:
            dialogo.close()

    def excluir_anuncio(self, anuncio: Anuncio):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar excluir anúncio",
            mensagem=f"Você tem certeza que deseja excluir esse anúncio?",
            largura=420
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_anuncio(resposta):
                if resposta:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#4CAF50",
                        largura=400, altura=50,paddingH=920, paddingV=100,
                        mensagem="Anúncio Excluído com Sucesso!"
                    )
                    ViewHelper.set_tela(self.stack, -2)
                else:
                    WidgetHelper.mostrar_alerta_temporario(
                        parent_widget=self.parent, 
                        backcolor="#f44336",
                        largura=400, altura=50,paddingH=920, paddingV=100,
                        mensagem="Erro ao excluir anúncio!"
                    )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.excluir_anuncio(anuncio),
                acao=ao_excluir_anuncio
            )

        else:
            dialogo.close()

    def excluir_endereco(self, endereco: Endereco):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar excluir endereço",
            mensagem=f"Você tem certeza que deseja excluir esse endereço?",
            largura=420
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_excluir_endereco(resposta):
                if resposta:
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent,
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingH=920, paddingV=100,
                            mensagem="Endereço Excluído com Sucesso!"
                        )
                        ViewHelper.set_tela(self.stack, -2)
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingH=920, paddingV=100,
                            mensagem="Erro ao excluir endereço!"
                        )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.excluir_endereco(endereco),
                acao=ao_excluir_endereco
            )

        else:
            dialogo.close()  

    def cancelar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar cancelamento", 
            mensagem=f"Você tem certeza que deseja cancelar pedido {pedido.id}?",
            largura=500
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_cancelar_pedido(resposta):
                if resposta:
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingV=100, paddingH=950,
                            mensagem="Pedido Cancelado com Sucesso!"
                        )
                        ViewHelper.set_tela(self.stack, -2)
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingV=100, paddingH=950,
                            mensagem="Erro ao cancelar pedido!"
                        )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.cancelar_pedido(pedido, pedido.produto.loja),
                acao=ao_cancelar_pedido
            )

        else:
            dialogo.close()

    def confirmar_pedido(self, pedido: Pedido):
        dialogo = CaixaConfirmacao(
            self, titulo="Confirmar", 
            mensagem=f"Você tem certeza que deseja confirmar pedido {pedido.id}?",
            largura=500
        )
        escolha = dialogo.exec()

        if escolha == QDialog.DialogCode.Accepted:
            def ao_confirmar_pedido(resposta):
                if resposta:
                    if resposta:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#4CAF50",
                            largura=400, altura=50,paddingV=100, paddingH=50,
                            mensagem="Pedido Confirmado com Sucesso!"
                        )
                        ViewHelper.set_tela(self.stack, -2)
                    else:
                        WidgetHelper.mostrar_alerta_temporario(
                            parent_widget=self.parent, 
                            backcolor="#f44336",
                            largura=400, altura=50,paddingV=100, paddingH=50,
                            mensagem="Erro ao confirmar pedido!"
                        )
            # Executa:
            Threads.executar_mensagem(
                stack=self.stack,
                requisicao=lambda: self.aplicacao.confirmar_pedido(pedido, pedido.produto.loja),
                acao=ao_confirmar_pedido
            )

        else:
            dialogo.close()