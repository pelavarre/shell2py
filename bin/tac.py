#!/usr/bin/env python3

"""
usage: tac.py [-h] [FILE ...]

show the lines of some files, but in reverse order, last line first

positional arguments:
  FILE        a file to copy out (default: stdin)

optional arguments:
  -h, --help  show this help message and exit

quirks:
  Mac has no Tac, and Linux Tac does not prompt for Stdin
  reserves the filename '-' to mean Stdin

examples:
  tac.py --help  # show this help message and exit
  (echo A; echo B; echo C; echo -n Z) |tac -  # echo ZC; echo B; echo A
"""

import sys
import textwrap

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_tac_py)


def parse_tac_args(argv):

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

    parser.add_argument(
        "files", metavar="FILE", nargs="*", help="a file to copy out (default: stdin)"
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    return args


def argv__to_tac_py(argv):
    """Write the Python for a Tac ArgV, else print some Help and quit"""

    args = parse_tac_args(argv)
    module_py = _scraps_.module_name__readlines(__name__)

    files = args.files if args.files else "-".split()
    files = list(("/dev/stdin" if (_ == "-") else _) for _ in files)

    # Write the Top Level Tac Python

    py1 = textwrap.dedent(
        """
        files = $FILES
        for file in files:
            tac_file(file)
        """
    ).strip()

    # Form enough more sourcelines

    py2 = py1
    py2 = _scraps_.py_pick_lines(py=py2, module_py=module_py)
    assert py2 != py1, py1

    py3 = py2
    py3 = _scraps_.py_add_imports(py=py3, module_py=module_py)
    assert py3 != py2, py2

    # Inject strings, last of all

    py4 = py3
    py4 = py4.replace("$FILES", _scraps_.as_py_value(files))
    assert py4 != py3, py3

    return py4


def tac_file(file):

    with open(file) as reading:
        isatty = reading.isatty()

        if isatty:
            sys.stderr.write("Press ⌃D EOF to quit\n")

        lines = reading.readlines()

    if isatty:
        sys.stderr.write("\n")

    for line in lines[::-1]:
        sys.stdout.write(line)


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
