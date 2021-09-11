#!/usr/bin/env python3

"""
usage: tac.py [-h] [FILE [FILE ...]]

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
  (echo A; echo B; echo C; echo -n Z) |tac  # echo ZC; echo B; echo A
"""

import sys
import textwrap

import _scraps_


def main(argv=None):
    as_argv = sys.argv if (argv is None) else argv
    _scraps_.exec_shell_to_py(name=__name__, argv=as_argv)


def parse_tac_args(argv):

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

    parser.add_argument(
        "files", metavar="FILE", nargs="*", help="a file to copy out (default: stdin)"
    )

    got_usage = parser.format_usage()
    assert got_usage == "usage: tac.py [-h] [FILE ...]\n", got_usage
    parser.usage = "tac.py [-h] [FILE [FILE ...]]"

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    return args


def shell_to_py(argv):

    args = parse_tac_args(argv)

    files = args.files if args.files else "-".split()
    files = list(("/dev/stdin" if (_ == "-") else _) for _ in files)

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:  # read this sourcefile
        module_py = incoming.read()

    # Write the first sourcelines

    py1 = textwrap.dedent(
        """
        files = $files
        for file in files:
            tac_file(file)
        """
    ).strip()

    py2 = py1.replace("$files", _scraps_.as_py_value(files))

    py3 = _scraps_.py_pick_lines(py=py2, module_py=module_py)

    return py3


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
