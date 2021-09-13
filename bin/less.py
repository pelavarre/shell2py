#!/usr/bin/env python3

"""
usage: ... |less.py [--help] [-F] [-I] [-X] [-R]

emulate Vim working with a copy of Stdin, but without waiting for Stdin to close

optional arguments:
  --help  show this help message and exit
  -F      just print Stdin and quit, if all the lines fit on screen
  -I      ignore case in searches, a la Vim ':set ignorecase'
  -X      just print the lines as they come, don't first clear the screen
  -R      at exit, leave the last lines seen on the screen, don't restore the screen

quirks:
  accepts lots more options, as sketched by:  man less
  secretly silently takes options from Environ $LESS, such as:  export LESS=-FIXR
  ⌃F ⌃B / etc work the same as Vim for Page Up, Page Down, Search, etc
  -I are the two chars to press to toggle between ignoring case and respecting case

examples:
  less.py --h
  seq 999 |less  # count lines like Environ $LINES does
"""

import argparse
import os
import sys

import _scraps_


def main():

    _scraps_.exec_shell_to_py(name=__name__)


def parse_less_args(argv):

    tty_size = argparse.Namespace(columns=80, lines=24)  # classic Terminal
    try:
        tty_size = os.get_terminal_size()
    except OSError:
        pass  # such as Stdout redirected to file

    try:
        _scraps_.parse_left_help_args(argv, doc=__doc__)
    except SystemExit:
        sys.stdout.flush()
        sys.stderr.write("\n")
        sys.stderr.write(
            "note: LINES={} COLUMNS={} "
            "is the Py guess of Stdout 'stty size' here\n".format(
                tty_size.lines, tty_size.columns
            )
        )

        raise


def shell_to_py(argv):

    parse_less_args(argv)

    altv = list(argv)
    altv[0] = "less"

    py = _scraps_.main_argv_to_py(altv)

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
