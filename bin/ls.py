#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1 | -C] [-X] [TOP]

show the files and dirs inside a dir

positional arguments:
  TOP     where to start looking (default: '.')

optional arguments:
  --help  show this help message and exit
  -1      show one name per line
  -C      show columns of names (default: True)
  -X      sort by ext (default: by name)

quirks:
  squeezes columns to left, with just two blanks between columns, like Linux
  Mac shows columns of equal width

examples:
  ls.py --help  # show this help message and exit
  ls -1  # name each file or dir inside the current dir
"""

# TODO:  -a  do not drop names starting with '.'
# TODO:  -f  do not sort, and infer '-a'


import argparse
import os
import pathlib
import sys

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

    group_1C = parser.add_mutually_exclusive_group()
    group_1C.add_argument(
        "-1", dest="one", action="count", help="show one name per line"
    )
    group_1C.add_argument(
        "-C", action="count", help="show columns of names (default: True)"
    )

    parser.add_argument("-X", action="count", help="sort by ext (default: by name)")

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    return args


def shell_to_py(argv):

    args = parse_ls_args(argv)
    if args.help:
        return ""

    # Read this sourcefile

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:
        module_py = incoming.read()

    # Write the first sourcelines

    if not args.one:
        py1 = "ls_C($TOP)"
    else:
        py1 = "ls_1($TOP)"
        if args.top is None:
            py1 = "ls_1_here()"

    # Form enough more sourcelines, but keep only the chosen options

    py2 = _scraps_.py_pick_lines(py=py1, module_py=module_py)
    assert py2 != py1, py1

    py3 = _scraps_.py_pick_lines(py=py2, module_py=module_py)
    # ( this 'py3' edit sometimes unneeded )

    py4 = _scraps_.py_dedent_args(py=py3, args=args, argnames="X".split())
    assert py4 != py3, py3

    py5 = _scraps_.py_add_imports(py=py4, module_py=module_py)
    assert py5 != py4, py4

    # Emit an implicit $TOP if called with an implicit $TOP

    py6 = py5
    line = "def ls_1_here():"
    if line in py5:
        py6 = _scraps_.py_dedent(py5, line, truthy=True)
        py6 = py6.replace("(top)", "()")
        py6 = py6.replace("import os\n\n\n\n", "import os\n\n\n")
        py6 = py6.replace("\n\n\nls_1_here()", "")
        # TODO: less custom styling

    # Inject strings, last of all

    top = "." if (args.top is None) else args.top
    py7 = py6.replace("$TOP", _scraps_.as_py_value(top))
    # ( this 'py7' edit sometimes unneeded )

    return py7


def ls_1(top, args):

    if args.X:
        names = os.listdir(top)  # dirs and files inside
        names.sort(key=lambda _: (pathlib.Path(_).suffix, _))

    if not args.X:
        names = sorted(os.listdir(top))  # dirs and files inside
    for name in names:
        if not name.startswith("."):  # if not hidden
            print(name)


def ls_1_here(args):
    # FIXME: wrong for not os.path.isdir(top)

    if not args.X:
        names = sorted(os.listdir())  # dirs and files inside
    if args.X:
        names = os.listdir()  # dirs and files inside
        names.sort(key=lambda _: (pathlib.Path(_).suffix, _))
    for name in names:
        if not name.startswith("."):  # if not hidden
            print(name)


def ls_C(top, args):
    # FIXME: wrong for not os.path.isdir(top)

    if not args.X:
        names = sorted(os.listdir(top))  # dirs and files inside
    if args.X:
        names = os.listdir(top)  # dirs and files inside
        names.sort(key=lambda _: (pathlib.Path(_).suffix, _))
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
