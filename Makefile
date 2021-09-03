D=bin
F=bin/shell2py.py
V=shell2py

default:
	clear
	:
	: copied from https://github.com/pelavarre/shell2py/blob/main/make.log
	:
	make py black flake8 go 2>&1 |tee make.log

setup:
	exit 3

	mkdir -p ~/.venvs
	cd ~/.venvs/
	rm -fr pips/  # casually destructive
	python3 -m venv --prompt PIPS pips

	source pips/bin/activate  # doesn't work inside Makefile's

	which pip
	pip freeze |wc -l  # often 0

	pip install --upgrade pip
	pip install --upgrade wheel
	pip install --upgrade black
	pip install --upgrade flake8
	pip freeze |wc -l  # often 12

py:
	:
	:
	echo | python3 -m pdb $F

black:
	:
	:
	~/.venvs/pips/bin/black $D/*.py

flake8:
	:
	:
	~/.venvs/pips/bin/flake8 --max-line-length=999 --ignore=E203,W503 $D/*.py
# --ignore=E203  # Black '[ : ]' rules over Flake8 E203 whitespace before ':'
# --ignore=W503  # 2017 Pep 8 and Black over Flake8 W503 line break before binary op

go:
	:
	:
	$V ls || :
	:
	:
	$V ls --help
	:
	:
	$V ls -1 |cat -n |expand
	:
	:
	ls -1
	:
	:
