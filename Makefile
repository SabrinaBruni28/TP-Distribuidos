install:
	sudo apt install libxcb-cursor0

salvar_bibliotecas:
	pip freeze > requirements.txt

install_bibliotecas:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip