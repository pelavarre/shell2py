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

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_dig_py)


def parse_dig_args(argv):

    _scraps_.parse_left_help_args(argv, doc=__doc__)


def argv__to_dig_py(argv):
    """Write the Python for a Dig ArgV, else print some Help and quit"""

    parse_dig_args(argv)

    altv = list(argv)
    altv[0] = "dig"

    py = _scraps_.argv__to_shline_py(altv)

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
