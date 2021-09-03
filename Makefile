D=bin
F=bin/shell2py.py
V=shell2py


default:
	clear
	make banner py black flake8 go 2>&1 |sed 's,  *$$,,' |tee make.log


secretly:
	clear
	make banner py black flake8 go


banner:
	:
	:
	: copied from https://github.com/pelavarre/shell2py/blob/main/make.log


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
	echo 'for P in bin/*.py; do echo | python3 -m pdb $$P; done' |bash


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


go: go_shell2py go_ls go_echo go_find
	:
	:


go_shell2py:
	:
	:
	$V || echo "+ exit $$?"
	:
	$V -h
	:
	$V --help


go_ls:
	:
	:
	$V ls || echo "+ exit $$?"
	:
	$V ls --help
	:
	$V ls -1 |cat -n |expand |sed 's,  *$$,,'
	bin/ls.py -1


go_echo:
	:
	:
	$V echo 'Hello, Echo World!'
	bin/echo.py 'Hello, Echo World!'
	:
	$V echo --v 'Hello,' 'Echo World!'
	bin/echo.py --v 'Hello,' 'Echo World!'
	:
	$V echo -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ⎋ ⇥ ⋮'
	bin/echo.py -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ⎋ ⇥ ⋮' |hexdump -C


go_find:
	:
	:
	$V find -maxdepth 1 -type d
	bin/find.py -maxdepth 1 -type d |grep i
	:
	$V find -name '.?*'
	bin/find.py -name '.?*' |head -3
	:
	$V find -name '.?*' -prune -o -print
	bin/find.py -name '.?*' -prune -o -print |head -3
	:
	$V find -type d
	bin/find.py -type d |head -3
	:
	$V find -type d -name '.?*' -prune -o -print
	bin/find.py -type d -name '.?*' -prune -o -print |head -3
	:
