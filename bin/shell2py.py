#!/usr/bin/env python3

"""
usage: shell2py.py [-h] VERB [WORD [WORD ...]]

translate the words, to python from bash

positional arguments:
  VERB        the first word of a shell line, being the program to run
  WORD        another word of a shell line, being an arg of the program to run

optional arguments:
  -h, --help  show this help message and exit

examples:
  shell2py -h  # show this help message and exit
  shell2py ls -1  # name each file or dir inside the current dir
"""

import sys

import _scraps_

import echo

import find

import ls


_ = (echo, find, ls)

# TODO: import just what the args need


# Offer the "--help" there, and also at "-h"

argv = sys.argv[1:]

if argv:
    arg = argv[0]
    helping = "--help".startswith(arg) and (len(arg) >= len("--h"))
    h_ing = arg == "-h"
    if helping or h_ing:
        print(__doc__.strip())
        sys.exit(0)


# Require VERB

if not argv:
    usage = __doc__.strip().splitlines()[0]
    sys.stderr.write(usage + "\n")
    sys.stderr.write("shell2py.py: error: the following arguments are required: VERB\n")
    sys.exit(2)


# Translate one line of Shell

verb = arg
if verb.startswith("bin/") and verb.endswith(".py"):
    verb = verb[len("bin/") :][: -len(".py")]  # such as "find" from "bin/find.py"

module = sys.modules[verb]
py = _scraps_.shell_to_py(module, argv=argv)
print(py)


# copied by: git clone https://github.com/pelavarre/shell2py.git
