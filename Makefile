.PHONY: cliente, servidorAp, servidorBD, nameServer

criar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	@. .venv/bin/activate && pip install -r Cliente/requirements.txt -r Servidor_Aplicacao/requirements.txt -r Servidor_BD/requirements.txt
	@. .venv/bin/activate && python3 -m pip install --upgrade pip

cliente:
	@. .venv/bin/activate && $(MAKE) --no-print-directory -C Cliente cliente $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))

servidorAP:
	@. .venv/bin/activate && $(MAKE) --no-print-directory -C Servidor_Aplicacao servidorAP $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA)) $(if $(HOST),HOST=$(HOST))

servidorBD:
	@. .venv/bin/activate && $(MAKE) --no-print-directory -C Servidor_BD servidorBD $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA)) $(if $(HOST),HOST=$(HOST))

nameServer:
	@. .venv/bin/activate && $(MAKE) --no-print-directory -C Servidor_Aplicacao nameServer $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))
