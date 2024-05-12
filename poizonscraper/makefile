.PHONY: virtualenv

VENV = venv

# Run a local web server
server: $(VENV)
	. $(VENV)/bin/activate; python main.py

run:
	python main.py

docker-bashin:
	docker run -p 5001:5001 -it --entrypoint /bin/bash docker.io/library/patty