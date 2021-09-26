#!/usr/bin/env python3

r"""
usage: grep.py [--help] [-a] [-n] [-w] PYREGEX

pick out Lines of Bytes of Stdin that match a Python Reg Ex

positional arguments:
  PYREGEX  regular expression pattern, in Python syntax, to find in lines of Stdin

optional arguments:
  --help   show this help message and exit
  -a       also pick lines that contain troublesome bytes, such as \0 and \x1B
  -n       print the line number (and a colon) before the line
  -w       pick only lines of reg ex as a whole word, not next to more word chars

quirks:
  searches for Python reg ex such as 'a|b|c', not Shell reg ex such as r'a\|b\|c'
  requires '-a', because i haven't found the spec on which lines Grep drops by default
  doesn't take '-h' as '--h', because Shell Grep defines '-h' and '-H' differently
  began life as a Generalised Regular Expression Parser (GREP)

examples:
  echo -n 'abc$def ghi$jklmno$pqr stu$vwx' |tr '$' '\n' >file && hexdump -C file
  cat file |grep -nw 'def\|jkl\|pqr'
  shell2py grep.py -anw 'def|jkl|pqr'
  cat file |grep.py -anw 'def|jkl|pqr'
"""

import sys
import textwrap

import _scraps_


def main():
    _scraps_.module_name__main(__name__, argv__to_py=argv__to_grep_py)


def parse_grep_args(argv):
    """Convert a Grep Sys ArgV to an Args Namespace, or print some Help and quit"""

    _ = _scraps_.parse_left_help_args(argv, doc=__doc__)  # intercept '--h' w/o PYREGEX

    parser = compile_grep_argdoc()

    args = parser.parse_args(argv[1:])
    if args.help:
        parser.print_help()
        sys.exit(0)

    return args


def compile_grep_argdoc():
    """Convert the Grep Main Doc to an ArgParse Parser"""

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__, drop_help=True)
    parser.add_argument(
        "--help", action="count", help="show this help message and exit"
    )

    parser.add_argument(
        "pyregex",
        metavar="PYREGEX",
        help="regular expression pattern, in Python syntax, to find in lines of Stdin",
    )  # required PYREGEX via default 'nargs=1', unlless '--h' intercepted earlier

    parser.add_argument(
        "-a",
        action="count",
        help=r"also pick lines that contain troublesome bytes, such as \0 and \x1B",
    )
    parser.add_argument(
        "-n",
        action="count",
        help="print the line number (and a colon) before the line",
    )
    parser.add_argument(
        "-w",
        action="count",
        help="pick only lines of reg ex as a whole word, not next to more word chars",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    return parser


def argv__to_grep_py(argv):
    """Write the Python for a Grep ArgV, else print some Help and quit"""

    args = parse_grep_args(argv)

    # Reject more complex translations, but do explain why

    if not args.a:
        sys.stderr.write("grep.py: error: choose argument -a\n")

        sys.exit(2)

    # Translate '-w'

    pyregex = args.pyregex
    if args.w:
        pyregex = r"\b(" + pyregex + r")\b"
    pyregex = pyregex.encode()

    # Form the Python

    if args.n:
        py = grep_an(pyregex)
    else:
        py = grep_a(pyregex)

    return py


def grep_a(pyregex):

    py = textwrap.dedent(
        """
        import os
        import re
        import sys

        def grep(pyregex):

            fd = sys.stdout.fileno()
            while True:
                line = sys.stdin.buffer.readline()
                if not line:

                    break

                if re.search(pyregex, string=line):

                    data = line
                    os.write(fd, data)

        grep($PYREGEX)
        """
    ).strip()

    py = py.replace("$PYREGEX", as_py_binary_regex(pyregex))

    return py


def as_py_binary_regex(pyregex):
    """Repr as rb"..." when easy, else fall back to Python Repr"""

    rep = _scraps_.as_py_value(pyregex)
    if b"\\" in pyregex:
        if not pyregex.endswith(b"\\"):
            if b'"' not in pyregex:
                chars = pyregex.decode()
                rep = 'rb"{}"'.format(chars)

    return rep


def grep_an(pyregex):

    py = textwrap.dedent(
        """
        import os
        import re
        import sys

        def grep(pyregex):

            fd = sys.stdout.fileno()
            lines = 0
            while True:
                line = sys.stdin.buffer.readline()
                if not line:

                    break

                lines += 1
                if re.search(pyregex, string=line):

                    data = str(lines).encode() + b":" + line
                    os.write(fd, data)

        grep($PYREGEX)
        """
    ).strip()

    py = py.replace("$PYREGEX", as_py_binary_regex(pyregex))

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
