.venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

run:
	. .venv/bin/activate && DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chinese_lesson python3 server.py

play:
	python3 play.py $(file) $(if $(out),-o $(out))
