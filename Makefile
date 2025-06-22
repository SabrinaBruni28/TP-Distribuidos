.PHONY: cliente, servidorAp, servidorBD, nameServer

criar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r Cliente/requirements.txt -r Servidor_Aplicacao/requirements.txt -r Servidor_BD/requirements.txt
	python3 -m pip install --upgrade pip

cliente:
	@$(MAKE) --no-print-directory -C Cliente cliente $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))

servidorAP:
	@$(MAKE) --no-print-directory -C Servidor_Aplicacao servidorAP $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA)) $(if $(HOST),HOST=$(HOST))

servidorBD:
	@$(MAKE) --no-print-directory -C Servidor_BD servidorBD $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA)) $(if $(HOST),HOST=$(HOST))

nameServer:
	@$(MAKE) --no-print-directory -C Servidor_Aplicacao nameServer $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))
