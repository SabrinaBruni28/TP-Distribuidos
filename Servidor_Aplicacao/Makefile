IP ?= "127.0.0.1"
PORTA ?= 9090
HOST ?= "127.0.0.1"

criar_ambiente:
	python3 -m venv .venv

instalar_bibliotecas:
	@python3 -m pip install --upgrade pip
	@pip install -r requirements.txt

salvar_bibliotecas:
	@pip freeze > requirements.txt

nameServer:
	@echo "Iniciando Name Server"
	@python3 name_server.py $(IP) $(PORTA)

servidorAP:
	@echo "Iniciando processo servidor"
	@python3 servidor.py "$(IP)" "$(PORTA)" "$(HOST)"
