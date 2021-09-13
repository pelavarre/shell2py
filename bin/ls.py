#!/usr/bin/env python3

"""
usage: ls.py [--help] [-C] [-1] [TOP]

show the files and dirs inside a dir

positional arguments:
  TOP     where to start looking (default: '.')

optional arguments:
  --help  show this help message and exit
  -C      show columns of names (default: True)
  -1      show one name per line

quirks:
  squeezes columns to left, with just two blanks between columns, like Linux
  doesn't show columns of equal width, like Mac

examples:
  ls.py --help  # show this help message and exit
  ls -1  # name each file or dir inside the current dir
"""

import argparse
import os
import sys
import textwrap

import _scraps_


def main():

    _scraps_.exec_shell_to_py(name=__name__)


def parse_ls_args(argv):

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__, drop_help=True)
    parser.add_argument(
        "--help", action="count", help="show this help message and exit"
    )

    parser.add_argument(
        "top", metavar="TOP", nargs="?", help="where to start looking (default: '.')"
    )

    parser.add_argument(
        "-C", action="count", help="show columns of names (default: True)"
    )
    parser.add_argument("-1", dest="one", action="count", help="show one name per line")

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    return args


def shell_to_py(argv):

    args = parse_ls_args(argv)
    if args.help:
        return ""

    top = "." if (args.top is None) else args.top

    if not args.one:
        py = shell_ls_C_to_py(top)
    else:
        if args.top is None:
            py = shell_ls_1_here_to_py()
        else:
            py = shell_ls_1_to_py(top=args.top)

    return py


def shell_ls_1_here_to_py():

    py = textwrap.dedent(
        """

        import os

        names = sorted(os.listdir())  # dirs and files inside
        for name in names:
            if not name.startswith("."):  # if not hidden
                print(name)

        """
    ).strip()

    return py


def shell_ls_1_to_py(top):

    py = textwrap.dedent(
        """

        import os

        top = $TOP

        names = [top]
        if os.path.isdir(top):
            names = sorted(os.listdir(top))  # dirs and files inside

        for name in names:
            if not name.startswith("."):  # if not hidden
                print(name)

        """
    ).strip()

    py = py.replace("$TOP", _scraps_.as_py_value(top))

    return py


def shell_ls_C_to_py(top):

    # Read this sourcefile

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:
        module_py = incoming.read()

    # Write the first sourcelines

    py1 = textwrap.dedent(
        """
        ls_C($TOP)
        """
    ).strip()

    py2 = py1.replace("$TOP", _scraps_.as_py_value(top))

    # Form enough more sourcelines

    py3 = _scraps_.py_pick_lines(py=py2, module_py=module_py)
    py4 = _scraps_.py_pick_lines(py=py3, module_py=module_py)

    return py4


def ls_C(path):

    names = sorted(os.listdir(path))  # dirs and files
    names = list(_ for _ in names if not _.startswith("."))  # if not hidden

    # note: 'ls -1' runs without struggling to fill a Terminal with 'join_shafts_of'

    tty_size = argparse.Namespace(columns=80, lines=24)  # classic Terminal
    try:
        tty_size = os.get_terminal_size()
    except OSError:
        pass  # such as Stdout redirected to file

    tty_columns = tty_size.columns

    sep = "  "
    chars = join_shafts_of(sep, cells=names, columns=tty_columns)
    print(chars)


def join_shafts_of(sep, cells, columns):
    """Make as many Shafts as fit into the Columns with Sep's between them"""

    strs = list(str(_) for _ in cells)

    # Search for the shortest Matrix Height that fits all the Cells into the Columns

    shafts = list()
    columns_by_x = list()

    len_strs = len(strs)
    for max_y in range(len_strs + 1):
        assert max_y < len_strs

        matrix_height = max_y + 1
        matrix_width = (len_strs + matrix_height - 1) // matrix_height
        assert (matrix_width * matrix_height) >= len_strs

        shafts = list()
        for x in range(matrix_width):
            shaft = strs[(x * matrix_height) :][:matrix_height]
            shaft = (shaft + (matrix_height * [""]))[:matrix_height]
            shafts.append(shaft)

        columns_by_x = list()
        for shaft in shafts:
            shaft_columns = max(len(_) for _ in shaft)
            columns_by_x.append(shaft_columns)

        matrix_columns = sum(columns_by_x)
        matrix_columns += (matrix_width - 1) * len(sep)

        if matrix_columns < columns:

            break

    # Join the Chars

    floors = tuple(zip(*shafts))  # Python 'zip(*' transposes NxN square matrices

    lines = list()
    for (y, floor) in enumerate(floors):
        assert len(floor) == len(columns_by_x)
        line = sep.join(f.ljust(c) for (f, c) in zip(floor, columns_by_x))
        lines.append(line)

    # Succeed

    chars = "\n".join(lines)

    return chars


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
