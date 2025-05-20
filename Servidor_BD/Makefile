criar_ambiente:
	python3 -m venv .venv

ativar_ambiente:
	source .venv/bin/activate

desativar_ambiente:
	deactivate

salvar_bibliotecas:
	pip freeze > requirements.txt

instalar_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip

servidorBD:
	@echo "Iniciando processo servidor banco de dados"
	@python3 servidor_bd.py