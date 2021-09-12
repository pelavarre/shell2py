#!/usr/bin/env python3

"""
usage: dig.py [--help]

pick bits out of DNS, because it's always because DNS

optional arguments:
  --help  show this help message and exit

quirks:
  network folk know the ordinary 'dig' command lines, we could discover them

examples:
  dig.py --h
  dig
"""

import _scraps_


def main():

    _scraps_.exec_shell_to_py(name=__name__)


def parse_dig_args(argv):

    _scraps_.parse_left_help_args(argv, doc=__doc__)


def shell_to_py(argv):

    parse_dig_args(argv)

    altv = list(argv)
    altv[0] = "dig"

    py = _scraps_.main_argv_to_py(altv)

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
