# define the name of the virtual environment directory
VENV := .venv

# default target, when make executed without arguments
all: venv run

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

run:
	./$(VENV)/bin/python main.py --filter "Middle UX-designer"

clean:
	find . | grep -E "(/__pycache__$|\.pyc$|\.pyo)" | xargs rm -rf

clean_all:
	rm -rf $(VENV)
	find . | grep -E "(/__pycache__$|\.pyc$|\.pyo)" | xargs rm -rf

.PHONY: all venv run clean