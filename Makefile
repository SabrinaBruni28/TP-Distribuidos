.PHONY: cliente, servidorAp, servidorBD

criar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip

cliente:
	@$(MAKE) --no-print-directory -C Cliente cliente $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))

servidorAp:
	@$(MAKE) --no-print-directory -C Servidor_Aplicacao servidorAp

servidorBD:
	@$(MAKE) --no-print-directory -C Servidor_BD servidorBD
