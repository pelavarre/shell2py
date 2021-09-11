# shell2py/Makefile


SHELL := /bin/bash -euo pipefail


D=bin
F=bin/shell2py.py
V=shell2py


# define:  make
default:
	:
	:
	: press Control+C if you meant:  make secretly
	:
	make secretly 2>&1 |sed 's,  *$$,,' >make.log
	git diff make.log


# run like default 'make', but stop at first fault, allow breakpoints, etc
secretly: py black flake8 go gitadds banner


# invite people to delete the 'exit 3' line and come edit this code with us
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


# show which Shell is running beneath this Makefile
sh:
	:
	:
	ps $$$$ | cat -


# screen out Python SyntaxError's
py:
	:
	:
	echo 'for P in bin/*.py; do echo | python3 -m pdb $$P; done' |bash


# correct misleading placements of blanks, quotes, commas, parentheses, and such
black:
	:
	:
	~/.venvs/pips/bin/black $D/*.py


# fail loudly asap after edited code starts misleading reviewers
flake8:
	:
	:
	~/.venvs/pips/bin/flake8 --max-line-length=999 --ignore=E203,W503 $D/*.py
# --ignore=E203  # Black '[ : ]' rules over Flake8 E203 whitespace before ':'
# --ignore=W503  # 2017 Pep 8 and Black over Flake8 W503 line break before binary op


# call to test each piece of this Shell2Py package
go: go_shell2py go_ls go_echo go_find go_tac go_tar
	:
	:


# test parts of Shell2Py that don't say in Python what you said in Bash
go_shell2py:
	:
	:
	$V || echo "+ exit $$?"
	:
	$V -h
	:
	$V --help


# test how Ls shows the files and dirs inside a dir
go_ls:
	:
	:
	$V ls || echo "+ exit $$?"
	:
	$V ls --help
	:
	$V ls -1 |cat -n |expand |sed 's,  *$$,,'
	bin/ls.py -1


# test how Echo sees your Shell split apart the chars you're typing
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


# test how Find shows a top dir of dirs, and the files and dirs it contains
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


# test how Tac shows the lines of a file, but in reverse order
go_tac:
	:
	:
	$V tac
	bash -c 'echo A; echo B; echo C; echo -n Z' |bin/tac.py
	:


# test how Tar walks the files and dirs found inside a top dir compressed as Tgz
go_tar:
	:
	:
	rm -fr dir/ dir.tgz
	mkdir -p dir/a/b/c dir/p/q/r
	echo hello >dir/a/b/d
	echo goodbye > dir/a/b/e
	tar czf dir.tgz dir/
	:
	$V tar tvf dir.tgz
	bin/tar.py tvf dir.tgz |sed 's,202.-..-.. ..:..,2021-09-11 11:30,'
	:
	$V tar xvkf dir.tgz
	rm -fr dir/
	bin/tar.py xvkf dir.tgz
	bin/tar.py xvkf dir.tgz || echo "+ exit $$?"
	bin/tar.py xvf dir.tgz
	rm -fr dir/ dir.tgz
	:
	: TODO: test 'tar tf' and 'tar xf' without 'v'


# mention files wrongly added by accident, and Py files wrongly Not added by accident
gitadds:
	:
	:
	git ls-files
	git status --short --ignored |(grep '[.]py$$' || :)


# say where the 'make.log' of default 'make' came from
banner:
	:
	:
	: copied by: git clone https://github.com/pelavarre/shell2py.git


# copied by: git clone https://github.com/pelavarre/shell2py.git
