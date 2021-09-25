#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1 | -C] [-X | -f] [-a] [-d] [TOP ...]

show the files and dirs inside some dirs

positional arguments:
  TOP              a file or dir to list (default: '.')

optional arguments:
  --help           show this help message and exit
  -1               show one name per line
  -C               show columns of names (default: True)
  -X               sort by ext (default: by name)
  -f               do not sort
  -a, --all        hide no names (by showing the names that start with the '.' dot)
  -d, --directory  show the names of dirs (not the files and dirs inside)

quirks:
  quits at first top not found, unlike Linux and Mac testing all tops before quitting
  squeezes columns to left, with just two blanks between columns, like Linux
  Mac shows columns of equal width
  writes less code when given just dirs, or just files, or just one top

examples:
  ls.py --help  # show this help message and exit
  ls -1  # name each file or dir inside the current dir
"""


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
        "tops", metavar="TOP", nargs="*", help="a file or dir to list (default: '.')"
    )

    group_1C = parser.add_mutually_exclusive_group()
    group_1C.add_argument(
        "-1", dest="one", action="count", help="show one name per line"
    )
    group_1C.add_argument(
        "-C", action="count", help="show columns of names (default: True)"
    )

    group_Xf = parser.add_mutually_exclusive_group()
    group_Xf.add_argument("-X", action="count", help="sort by ext (default: by name)")
    group_Xf.add_argument("-f", action="count", help="do not sort")

    parser.add_argument(
        "-a",
        "--all",
        action="count",
        help="hide no names (by showing the names that start with the '.' dot)",
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="count",
        help="show the names of dirs (not the files and dirs inside)",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    if not args.one and not args.C:
        args.C = 1

    return args


def shell_to_py(argv):  # noqa C901 too complex  # FIXME

    args = parse_ls_args(argv)
    if args.help:
        return ""

    # Read this sourcefile

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:
        module_py = incoming.read()

    module_py = module_py.replace(":  # noqa C901 too complex\n", ":\n")

    # Fetch example inputs

    tops = args.tops if args.tops else ".".split()
    last_top = tops[-1]

    topdirs = list()
    topfiles = list()

    for top in tops:
        _ = os.stat(top)  # raises OSError if 'top' not found

        if os.path.isdir(top):  # '.isdir' may have changed since 'stat.S_ISDIR'
            topdirs.append(top)
        else:
            topfiles.append(top)

    args.topdirs = topdirs
    args.topfiles = topfiles

    args.len_args_topdirs_gt_1 = len(topdirs) > 1
    args.len_args_topfiles_gt_1 = len(topfiles) > 1

    argnames = sorted(vars(args).keys())

    # Write the first paragraph of source

    assert args.topdirs or args.topfiles, args.tops

    if args.directory:
        py1 = "some_tops_ls($TOPS)"
        calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
        calling_as_if = "def some_tops_ls(tops):"
    if not args.directory:
        if args.topdirs:
            if not args.topfiles:
                if args.len_args_topdirs_gt_1:
                    py1 = "some_tops_ls(topdirs=$TOPS)"
                    calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                    calling_as_if = "def some_tops_ls(tops):"
                if not args.len_args_topdirs_gt_1:
                    if not args.tops:
                        py1 = "one_dir_ls()"
                        calling_to = "def one_dir_ls(top):"
                        calling_as_if = "def one_dir_ls():"
                    else:
                        py1 = "one_dir_ls($TOP)"
                        calling_to = "def one_dir_ls(top):"
                        calling_as_if = calling_to
        if args.topfiles:
            if args.topdirs:
                py1 = "some_tops_ls($TOPFILES, topdirs=$TOPDIRS)"
                calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                calling_as_if = "def some_tops_ls(topfiles, topdirs):"
            if not args.topdirs:
                if args.len_args_topfiles_gt_1:
                    py1 = "some_tops_ls(topfiles=$TOPFILES)"
                    calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                    calling_as_if = "def some_tops_ls(topfiles):"
                if not args.len_args_topfiles_gt_1:
                    py1 = "one_name_ls($TOP)"
                    calling_to = "def one_name_ls(top):"
                    calling_as_if = calling_to

    py1 = _scraps_.py_dedent_args(py=py1, args=args, argnames=argnames)

    # Form enough more sourcelines, but keep only the chosen options

    py2 = py1
    py2 = _scraps_.py_pick_lines(py=py2, module_py=module_py)
    py2 = _scraps_.py_dedent_args(py=py2, args=args, argnames=argnames)

    py3 = py2
    py3 = _scraps_.py_pick_lines(py=py3, module_py=module_py)
    py3 = _scraps_.py_dedent_args(py=py3, args=args, argnames=argnames)

    py4 = py3
    py4 = _scraps_.py_pick_lines(py=py4, module_py=module_py)
    py4 = _scraps_.py_dedent_args(py=py4, args=args, argnames=argnames)

    py5 = py4
    py5 = _scraps_.py_add_imports(py=py5, module_py=module_py)

    # Expand a single call of 'def some_names_print' inline

    py6 = py5

    if (not args.topfiles) or (not args.topfiles):
        py6 = py6.replace(
            "    some_names_print(names=names)\n\n\ndef some_names_print(names):\n", ""
        )

    py6 = py6.replace("def one_dir_ls():\n ", "def one_dir_ls():\n\n ")
    py6 = py6.replace("def one_dir_ls(top):\n ", "def one_dir_ls(top):\n\n ")
    py6 = py6.replace(
        "# Choose an order of names\n ", "# Choose an order of names\n\n "
    )  # TODO: less custom styling

    while "\n\n\n " in py6:
        py6 = py6.replace("\n\n\n ", "\n\n ")

    # Emit an implicit $TOPS if called with an implicit $TOPS

    py7 = py6
    if py1 == "one_dir_ls()":
        if args.C:
            py7 = py7.replace("(top)", "()")
        else:
            line = "def one_dir_ls(top):"
            assert line in py6
            py7 = _scraps_.py_dedent(py6, line, truthy=True)
            py7 = py7.replace("import os\n\n\n\n", "import os\n\n")
            py7 = py7.replace("(top)", "()")
            py7 = py7.replace("os.stat(os.path.join(top, name))", "os.stat(name)")
            py7 = py7.replace("\n\n\none_dir_ls()", "")
            # TODO: less custom styling

    # Inject strings, last of all

    py8 = py7

    py8 = py8.replace("$TOPFILES", _scraps_.as_py_value(topfiles))
    py8 = py8.replace("$TOPDIRS", _scraps_.as_py_value(topdirs))
    py8 = py8.replace("$TOPS", _scraps_.as_py_value(tops))
    py8 = py8.replace("$TOP", _scraps_.as_py_value(last_top))

    py8 = py8.replace(calling_to, calling_as_if)

    return py8

    # # TODO: mark meta-comments differently and drop them
    # # TODO: trace Bash in the DocStrings
    # # TODO: calculate DocStrings by Args


def some_tops_ls(tops, topfiles, topdirs, args):  # noqa C901 too complex

    if args.directory:

        for top in tops:
            _ = os.stat(top)
        some_names_print(names=tops)

    if not args.directory:

        if args.topfiles:

            for topfile in topfiles:
                _ = os.stat(topfile)
            some_names_print(names=topfiles)

        if args.topdirs:

            for (index, topdir) in enumerate(topdirs):
                if args.topfiles:
                    print()
                    print("{}:".format(topdir))
                if not args.topfiles:
                    if args.len_args_topdirs_gt_1:
                        if index:
                            print()
                        print("{}:".format(topdir))

                if args.all:
                    names = list([os.curdir, os.pardir] + os.listdir(topdir))
                if not args.all:
                    names = os.listdir(topdir)
                    names = list(_ for _ in names if not _.startswith("."))

                some_names_print(names=names)


def one_dir_ls(top, args):

    if args.directory:
        _ = os.listdir(top)
        print(top)
    if not args.directory:

        if args.all:
            names = list([os.curdir, os.pardir] + os.listdir(top))
        if not args.all:
            names = os.listdir(top)
            names = list(_ for _ in names if not _.startswith("."))

        some_names_print(names=names)


def some_names_print(names, args):  # noqa C901 too complex

    if not args.C:

        if args.f:
            for name in names:
                print(name)
        if args.X:
            for name in sorted(names, key=lambda _: (pathlib.Path(_).suffix, _)):
                print(name)
        if not args.f:
            if not args.X:
                for name in sorted(names):
                    print(name)

    if args.C:

        # Choose an order of names

        if args.f:
            cells = names
        if args.X:
            cells = sorted(names, key=lambda _: (pathlib.Path(_).suffix, _))
        if not args.f:
            if not args.X:
                cells = sorted(names)

        # Guess the width of the Terminal

        tty_size = argparse.Namespace(columns=80, lines=24)  # classic Terminal
        try:
            tty_size = os.get_terminal_size()
        except OSError:
            pass  # such as Stdout redirected to file

        tty_columns = tty_size.columns

        # Pack names into columns

        chars = pack_cells_in_columns(cells, tty_columns=tty_columns, sep="  ")
        if chars:
            print(chars)


def one_name_ls(name, args):

    _ = os.stat(name)
    print(name)


def pack_cells_in_columns(cells, tty_columns, sep):
    """Pack Cells into Columns with Sep's between them"""

    strs = list(str(_) for _ in cells)

    # Search for the shortest Matrix Height that fits Cells into the Tty Columns

    shafts = list()
    columns_by_x = list()

    if strs:
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

            if matrix_columns < tty_columns:

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
