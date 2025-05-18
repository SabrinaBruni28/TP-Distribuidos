.PHONY: cliente

criar_ambiente:
	python3 -m venv .venv

ativar_ambiente:
	source .venv/bin/activate

desativar_ambiente:
	deactivate

instalar_bibliotecas:
	pip install -r Cliente/requirements.txt -r ServidorAp/requirements.txt -r ServidorBD/requirements.txt
	python3 -m pip install --upgrade pip

cliente:
	$(MAKE) --no-print-directory -C Cliente cliente $(if $(IP),IP=$(IP)) $(if $(PORTA),PORTA=$(PORTA))

servidorAp:
	$(MAKE) --no-print-directory -C ServidorAp cliente

servidorBD:
	$(MAKE) --no-print-directory -C ServidorBD cliente
