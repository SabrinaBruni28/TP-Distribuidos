# Definindo valores padrão
IP ?= "127.0.0.1"
PORTA ?= 9090
HOST ?= "127.0.0.1"

criar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	@pip freeze > requirements.txt

instalar_bibliotecas:
	@pip install -r requirements.txt
	@python3 -m pip install --upgrade pip

servidorBD:
	@echo "Iniciando processo servidor banco de dados"
	@echo "IP: $(IP)"
	@echo "PORTA: $(PORTA)"
	@echo "HOST: $(HOST)"
	@PYTHONDONTWRITEBYTECODE=1 python3 servidor_bd.py "$(IP)" "$(PORTA)" "$(HOST)"