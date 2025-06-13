from Operacoes import server_operation as op

class Requisicao:
    def __init__(self,id_requisicao, tipo_requisicao, dados, id_associado = None, imagens = None):
        self.idRequisicao = id_requisicao
        self.tipoRequisicao = tipo_requisicao
        self.dadosRequisicao = dados
        self.imagens = imagens
        self.idAssociado = id_associado

    @staticmethod
    def produzRequisicao(tipo_requisicao, dados, id_associado = None, imagens = None):
        reqID = op.gerarID()

        requisicao = Requisicao(reqID, tipo_requisicao, dados, id_associado, imagens)
        print(f"[Servidor][Requisição] Requisição criada: {requisicao.idRequisicao}.")

        return requisicao