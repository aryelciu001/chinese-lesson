run:
	python3 server.py

play:
	python3 play.py $(file) $(if $(out),-o $(out))
