# shell2py/Makefile


SHELL := /bin/bash -euo pipefail


D=bin
F=bin/shell2py.py
V=shell2py


# define:  make
default: py black flake8
	:
	:
	: press Control+C if you meant:  make secretly
	:
	rm -fr .dotfile .dotdir/ dir/ dir.tgz file p.py
	time make secretly 2>&1 |sed 's,  *$$,,' >make.log
	git diff make.log


# run like default 'make', but stop at first fault, allow breakpoints, etc
secretly: py black flake8 go gitadds banner
	rm -fr .dotfile .dotdir/ dir/ dir.tgz file p.py
	rm -fr bin/__pycache__/


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
	pip install --upgrade flake8  # includes:  pip install --upgrade mccabe
	pip install --upgrade flake8-import-order
	pip freeze |wc -l  # often 13


# show which Shell is running beneath this Makefile
sh:
	:
	:
	ps $$$$ |cat -


# screen out Python SyntaxError's
py:
	:
	:
	echo 'for P in bin/*.py; do echo |python3 -m pdb $$P; done' |bash


# correct misleading placements of blanks, quotes, commas, parentheses, and such
black:
	:
	:
	~/.venvs/pips/bin/black $D/*.py


# fail loudly asap after edited code starts misleading reviewers
flake8:
	:
	:
	~/.venvs/pips/bin/flake8 --max-line-length=999 --max-complexity 10 --ignore=E203,W503 $D/*.py
# --ignore=E203  # Black '[ : ]' rules over Flake8 E203 whitespace before ':'
# --ignore=W503  # 2017 Pep 8 and Black over Flake8 W503 line break before binary op


# call to test each piece of this Shell2Py package
go: go_shell2py go_ls go_echo go_find go_grep go_less go_tac go_tar
	:
	:


# test parts of Shell2Py that don't say in Python what you said in Bash
go_shell2py:
	:
	:
	$V || echo "+ exit $$?"
	:
	$V help || echo "+ exit $$?"
	:
	$V -h
	:
	$V --help


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


# test how Find shows a Top Dir of Dirs, and the Files and Dirs it contains
go_find: .dotdir-and-dir
	:
	rm -fr file
	:
	$V find -maxdepth 1 -type d
	bin/find.py -maxdepth 1 -type d |grep i
	:
	$V find -name '.?*'
	bin/find.py -name '.?*' >file
	head -4 file
	:
	$V find -name '.?*' -prune -o -print
	bin/find.py -name '.?*' -prune -o -print >file
	head -10 file
	:
	$V find -type d
	bin/find.py -type d >file
	head -10 file
	:
	$V find -name '.?*' -prune -o -type d -print
	bin/find.py -name '.?*' -prune -o -type d -print >file
	head -10 file
	:
	rm -fr file
	:


.dotdir-and-dir:
	:
	:
	rm -fr dotdir/ dir/
	:
	mkdir -p .dotdir/
	touch .dotdir/.dotdir-dotchild
	touch .dotdir/dotdir-child
	mkdir -p dir/
	touch dir/.dir-dotchild
	touch dir/dir-child


# demo Python freaking over 'signal.SIGPIPE' not caught between 'exec' and 'print'
sigpipe:
	:
	: macOS Terminal =>
	:
	:   'BrokenPipeError: [Errno 32] Broken pipe'
	:   'Exception ignored in: <_io.TextIOWrapper'
	:       "name='<stdout>' mode='w' encoding='utf-8'>'"
	:   'make: *** [sigpipe] Error 120'
	:   'zsh: exit 2     make xyz'
	:
	python3 -c 'import signal; print(int(signal.SIGPIPE))'  # 13 == 141 - 128
	(find ~ |head -3) || echo "+ exit $$?"  # + exit 141
	(bin/find.py ~ |head -3) || echo "+ exit $$?"  # + exit 120


# test how Grep picks out Lines of Bytes of Stdin that match a Python Reg Ex
go_grep:
	:
	:
	rm -fr file
	:
	$V grep.py -anw 'def|jkl|pqr'
	:
	echo -n 'abc@def ghi@jklmno@pqr stu@vwx' |tr '@' '\n' >file && hexdump -C file
	cat file |grep.py -anw 'def|jkl|pqr'
	cat file |grep.py -aw 'def|jkl|pqr'
	cat file |grep.py -a 'def|jkl|pqr'
	(cat file |grep.py 'def|jkl|pqr') || echo "+ exit $$?"
	:
	rm -fr file


# test how Less Py layers thinly over Shell
go_less:
	:
	:
	$V less -FIXR
	:
	ls |less.py -FIXR  # hangs at screens of less than 6 lines


# test how Ls shows the Files and Dirs inside a Dir
go_ls:
	:
	:
	$V ls || echo "+ exit $$?"
	:
	$V ls --help
	:
	$V ls -1 |cat -n |expand |sed 's,  *$$,,'
	bin/ls.py -1



# test how Tac shows the lines of a file, but in reverse order
go_tac:
	:
	:
	$V tac -
	bash -c 'echo A; echo B; echo C; echo -n Z' |bin/tac.py -
	:


# test how Tar walks and how Tar picks
go_tar: go_tar_walk go_tar_pick
	:
	:
	rm -fr dir/ dir.tgz p.py



dir.tgz:
	:
	:
	rm -fr dir/ dir.tgz
	:
	mkdir -p dir/a/b/c dir/p/q/r
	echo hello >dir/a/b/d
	echo goodbye > dir/a/b/e
	bin/tar.py czf dir.tgz dir/


# test how Tar walks the Files and Dirs found inside a Top Dir compressed as Tgz
go_tar_walk: dir.tgz

	:
	:
	$V tar tvf dir.tgz
	bin/tar.py tvf dir.tgz |sed 's,202.-..-.. ..:..,2021-09-11 11:30,'
	:
	$V tar xvkf dir.tgz
	rm -fr dir/
	bin/tar.py xvkf dir.tgz
	bin/tar.py xvkf dir.tgz || echo "+ exit $$?"
	:
	$V tar xvf dir.tgz
	bin/tar.py xvf dir.tgz
	:
	:
	$V tar tf dir.tgz
	bin/tar.py tf dir.tgz
	:
	$V tar xkf dir.tgz
	rm -fr dir/
	bin/tar.py xkf dir.tgz
	bin/tar.py xkf dir.tgz || echo "+ exit $$?"
	:
	$V tar xf dir.tgz
	bin/tar.py xf dir.tgz


# test how Tar picks out some Dirs and Files
go_tar_pick: dir.tgz
	:
	:
	rm -fr p.py
	:
	$V tar tf dir.tgz dir/a
	bin/tar.py tf dir.tgz dir/a
	:
	$V tar tf dir.tgz dir dir/a// dir >p.py
	tail -2 p.py
	bin/tar.py tf dir.tgz dir dir/a/b/d/// dir
	:
	$V tar xf dir.tgz -O 'dir/a/*/?' >p.py
	tail -2 p.py
	bin/tar.py xf dir.tgz -O 'dir/a/*/?'


# mention files wrongly added by accident, and Py files wrongly Not added by accident
gitadds:
	:
	:
	git ls-files
	git status --short --ignored |grep -v '^ M ' |(grep '[.]py$$' || :)


# say where the 'make.log' of default 'make' came from
banner:
	:
	:
	: copied by: git clone https://github.com/pelavarre/shell2py.git


# copied by: git clone https://github.com/pelavarre/shell2py.git
