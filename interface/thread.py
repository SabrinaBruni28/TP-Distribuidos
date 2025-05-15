import sys, os
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from interface.widgets import ViewHelper

CAMINHO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(CAMINHO_BASE)

class WorkerGenerico(QObject):
    terminado = pyqtSignal(object)  # envia resultado

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        resultado = self.func()
        self.terminado.emit(resultado)

class Threads:
    @staticmethod
    def carregar_em_thread(funcao_segundo_plano, quando_terminar=None, tela_loading=None, abrir_tela=None, voltar_tela=None, nova_tela_callback=None, passar_resultado=False):
        thread = QThread()
        worker = WorkerGenerico(funcao_segundo_plano)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        if passar_resultado:
            worker.terminado.connect(lambda resultado: Threads._finalizar_thread(
                thread, worker, quando_terminar, abrir_tela, voltar_tela, nova_tela_callback, resultado
            ))
        else:
            worker.terminado.connect(lambda: Threads._finalizar_thread(
                thread, worker, quando_terminar, abrir_tela, voltar_tela, nova_tela_callback
            ))

        thread.start()
        if abrir_tela and tela_loading:
            abrir_tela(tela_loading)

    @staticmethod
    def _finalizar_thread(thread, worker, quando_terminar=None, abrir_tela=None, voltar_tela=None, nova_tela_callback=None, resultado=None):
        thread.quit()
        thread.wait()
        thread.deleteLater()
        worker.deleteLater()

        if voltar_tela:
            voltar_tela()

        if abrir_tela and nova_tela_callback:
            nova_tela = nova_tela_callback()
            abrir_tela(nova_tela, excluir_anterior=True)

        if quando_terminar:
            if resultado is not None:
                quando_terminar(resultado)
            else:
                quando_terminar()  

    @staticmethod
    def executar_tela(stack, acao, requisicao, tela = None, mensagem="Carregando ..."):
        tela_carregando = ViewHelper.tela_carregando_com_spinner(
            mensagem, gif_path="imagens/spinner.gif"
        )

        Threads.carregar_em_thread(
            funcao_segundo_plano=requisicao,
            tela_loading=tela_carregando,
            abrir_tela=lambda: ViewHelper.abrir_tela(stack),
            nova_tela_callback=tela,
            quando_terminar=acao,
            passar_resultado=True
        )

    @staticmethod
    def executar_mensagem(stack, requisicao, acao, mensagem="Salvando ..."):
        tela_carregando = ViewHelper.tela_carregando_com_spinner(
            mensagem, gif_path="imagens/spinner.gif"
        )

        Threads.carregar_em_thread(
            funcao_segundo_plano=requisicao,
            tela_loading=tela_carregando,
            abrir_tela= lambda: ViewHelper.abrir_tela(stack),
            voltar_tela=lambda: ViewHelper.voltar_tela(stack),
            quando_terminar=acao,
            passar_resultado=True
        )