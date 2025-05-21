# Definindo valores padrão
IP ?= "localhost"
PORTA ?= 5000

criar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip

cliente:
	@echo "Iniciando processo cliente"
	@echo "IP: $(IP)"
	@echo "PORTA: $(PORTA)"
	@python3 interface/interface.py "$(IP)" "$(PORTA)"