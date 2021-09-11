#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1]

show the files and dirs inside a dir

optional arguments:
  --help  show this help message and exit
  -1      print one filename or dirname per line

quirks:
  you must choose '-1' or '-l', because default 'ls' style needs 'os.get_terminal_size'

examples:
  ls.py --help  # show this help message and exit
  ls -1  # name each file or dir inside the current dir
"""

import sys
import textwrap

import _scraps_


def main(argv=None):
    as_argv = sys.argv if (argv is None) else argv
    _scraps_.exec_shell_to_py(name=__name__, argv=as_argv)


def parse_ls_args(argv):

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__, drop_help=True)
    parser.add_argument(
        "--help", action="count", help="show this help message and exit"
    )
    parser.add_argument(
        "-1", action="count", help="print one filename or dirname per line"
    )
    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    return args


def shell_to_py(argv):

    args = parse_ls_args(argv)
    if args.help:
        return ""

    args_1 = vars(args)["1"]
    if args_1:
        py = ls_1()
        return py


def ls_1():
    py = textwrap.dedent(
        """

        import os

        filenames = sorted(os.listdir())
        for filename in filenames:
            if not filename.startswith("."):  # if not hidden
                print(filename)

        """
    ).strip()
    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
