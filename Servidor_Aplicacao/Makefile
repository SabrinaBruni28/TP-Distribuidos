.PHONY: criar_ambiente instalar_bibliotecas salvar_bibliotecas run name_server servidorAP

VENV=.venv
PYTHON=$(VENV)\Scripts\python.exe
PIP=$(VENV)\Scripts\pip.exe

criar_ambiente:
	@if not exist $(VENV) (\
		python -m venv $(VENV) \
	)

instalar_bibliotecas: criar_ambiente
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

salvar_bibliotecas:
	$(PIP) freeze > requirements.txt

name_server: instalar_bibliotecas
	@echo "Iniciando Name Server"
	$(PYTHON) name_server.py $(IP) $(PORTA)

servidorAP: instalar_bibliotecas
	@echo "Iniciando processo servidor"
	$(PYTHON) servidor.py $(IP) $(PORTA)
