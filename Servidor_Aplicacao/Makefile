ccriar_ambiente:
	python3 -m venv .venv

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip

servidorAp:
	@echo "Iniciando processo servidor"
	@python3 servidor.py