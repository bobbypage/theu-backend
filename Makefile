venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv ||  python3 -m venv venv
	venv/bin/pip3 install -Ur requirements.txt
	touch venv/bin/activate

install: venv
	@echo "Installed!"

run: venv
	FLASK_APP=server.py venv/bin/flask run
