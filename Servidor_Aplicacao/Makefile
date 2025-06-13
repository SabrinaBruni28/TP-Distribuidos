ccriar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip

name_server:
	@echo "Iniciando Name Server"
	@python3 name_server.py $(if $(IP),$(IP),) $(if $(PORTA),$(PORTA),)

servidorAP:
	@echo "Iniciando processo servidor"
	@python3 servidor.py $(if $(IP),$(IP),) $(if $(PORTA),$(PORTA),)