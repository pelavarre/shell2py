#!/usr/bin/env python3

"""
usage: shell2py.py [-h] [WORD [WORD ...]]

translate the words, to python from bash

positional arguments:
  WORD        a word of bash

optional arguments:
  -h, --help  show this help message and exit

examples:
  shell2py -h  # show this help message and exit
  shell2py ls -1  # name each file or dir inside the current dir
"""

import sys

import ls

import _scraps_

argv = sys.argv[1:]
py = _scraps_.shell_to_py(ls, argv=argv)
print(py)


# copied by: git clone https://github.com/pelavarre/shell2py.git
