#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1 | -l | -C] [--headings] [--full-time] [-X | -f] [-a]
             [-d] [-F]
             [TOP ...]

show the files and dirs inside some dirs

positional arguments:
  TOP              a file or dir to list (default: '.')

optional arguments:
  --help           show this help message and exit
  -1               show one name per line
  -l               show details of perms, links, user, group, bytes, stamp, name
  -C               show columns of names (default: True)
  --headings       insert a row of headings before the rows of '-l' details
  --full-time      stamp with a more precise date/time in the rows of '-l' details
  -X               sort by ext (default: by name)
  -f               do not sort
  -a, --all        hide no names (by showing the names that start with the '.' dot)
  -d, --directory  show the names of dirs (not the files and dirs inside)
  -F, --classify   add '*/=>@' suffixes to exec, dir, socket, door, or sym

quirks:
  shows columns like Linux, separated by two spaces, not equal width like Mac
  quits at first top found, doesn't show all not found like Linux or Mac
  shows user and group as "." dot when same as $HOME
  actually doesn't yet know how to mark socket as '=', nor door as '>'
  writes less code when given just dirs, or just files, or just one top

examples:
  ls.py --help  # show this help message and exit
  ls -1  # show each file or dir inside the current dir
  ls -C  # ask explicitly for the default output
  ls *  # show each file, then show each file or dir inside each child dir
"""

# reserve 'ls --he' to quit via 'ambiguous option: --he could match --help, --headings'
# reserve 'ls -hl' to mean speak in humane units: 'B'yte, 'k'ibi, 'M'ebi, etc


import argparse
import os
import pathlib
import sys

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_ls_py)


def parse_ls_args(argv):
    """Convert an Ls Sys ArgV to an Args Namespace, or print some Help and quit"""

    parser = compile_ls_argdoc()

    args = parser.parse_args(argv[1:])
    if args.help:
        parser.print_help()
        sys.exit(0)

    expand_ls_args(args)

    return args


def compile_ls_argdoc():
    """Convert the Ls Main Doc to an ArgParse Parser"""

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__, drop_help=True)
    parser.add_argument(
        "--help", action="count", help="show this help message and exit"
    )

    parser.add_argument(
        "tops", metavar="TOP", nargs="*", help="a file or dir to list (default: '.')"
    )

    group_1lC = parser.add_mutually_exclusive_group()
    group_1lC.add_argument(
        "-1", dest="cells", action="count", help="show one name per line"
    )
    group_1lC.add_argument(
        "-l",
        dest="long_rows",  # duck Flake8 E741 ambiguous variable name 'l'
        action="count",
        help="show details of perms, links, user, group, bytes, stamp, name",
    )
    group_1lC.add_argument(
        "-C",
        action="count",
        help="show columns of names (default: True)",
    )

    parser.add_argument(
        "--headings",
        action="count",
        help="insert a row of headings before the rows of '-l' details",
    )
    parser.add_argument(
        "--full-time",
        action="count",
        help="stamp with a more precise date/time in the rows of '-l' details",
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

    parser.add_argument(
        "-F",
        "--classify",
        action="count",
        help="add '*/=>@' suffixes to exec, dir, socket, door, or sym",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    return parser


def expand_ls_args(args):
    """Derive more Ls Args from the parsed Ls Args, or print some Help and quit"""

    # Choose one or more 'TOPS', never zero

    args.some_tops = args.tops if args.tops else ".".split()
    args.last_top = args.some_tops[-1]  # last is first is only, when just one exists

    # Choose one of '[-1 | -l | -C]' always
    # Accept '--headings' and '--full-time' only in place of, or as modifiers of, '-l'

    if args.headings or args.full_time:
        args.long_rows = 1

    args.tall_columns = args.C
    if not args.cells and not args.long_rows and not args.C:
        args.tall_columns = 1

    returncode = None
    for extra in "headings full_time".split():
        extra_argname = dict(headings="--headings", full_time="--full-time")[extra]
        if vars(args)[extra]:
            for mode in "cells tall_columns".split():
                mode_argname = dict(cells="-1", tall_columns="-C")[mode]
                if vars(args)[mode]:
                    returncode = 2

                    sys.stderr.write(
                        "ls.py: error: argument {}: not allowed with argument {}\n".format(
                            extra_argname, mode_argname
                        )
                    )  # a la:  ls.py: error: argument -C: not allowed with argument -1

    if returncode:
        sys.exit(2)

    output_formats = bool(args.cells) + bool(args.long_rows) + bool(args.tall_columns)
    assert output_formats == 1, args

    # Parse the example Args now, to choose what Code to run later

    topdirs = list()
    topfiles = list()

    for top in args.some_tops:
        _ = os.stat(top)  # raises OSError if 'top' not found

        if os.path.isdir(top):  # '.isdir' may have changed since 'stat.S_ISDIR'
            topdirs.append(top)
        else:
            topfiles.append(top)

    args.topdirs = topdirs
    args.topfiles = topfiles

    args.len_args_topdirs_gt_1 = len(topdirs) > 1
    args.len_args_topfiles_gt_1 = len(topfiles) > 1


#
# Form the Python of Ls
#


def argv__to_ls_py(argv):
    """Write the Python for a Ls Argv, else print some Help and quit"""

    # Open up

    args = parse_ls_args(argv)

    # Don't yet translate Usage: '[-l] [--headings] [--full-time] [-F]'

    if args.long_rows or args.classify:
        return

    assert not args.headings
    assert not args.full_time

    # Write the Source

    (py1, calling) = args__to_top_level_ls_py(args)
    ls_py = args__to_whole_ls_py(args, py1=py1, calling=calling)

    return ls_py


def args__to_top_level_ls_py(args):
    """Write the Top Level of Ls Python"""

    if args.directory:

        py1 = "some_tops_ls($TOPS)"
        calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
        calling_as_if = "def some_tops_ls(tops):"

    else:

        if args.topfiles:

            if args.topdirs:

                py1 = "some_tops_ls($TOPFILES, topdirs=$TOPDIRS)"
                calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                calling_as_if = "def some_tops_ls(topfiles, topdirs):"

            else:

                if args.len_args_topfiles_gt_1:
                    py1 = "some_tops_ls(topfiles=$TOPFILES)"
                    calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                    calling_as_if = "def some_tops_ls(topfiles):"
                else:
                    py1 = "one_name_ls($TOP)"
                    calling_to = "def one_name_ls(top):"
                    calling_as_if = calling_to

        else:
            assert args.topdirs, args.tops

            if args.len_args_topdirs_gt_1:

                py1 = "some_tops_ls(topdirs=$TOPS)"
                calling_to = "def some_tops_ls(tops, topfiles, topdirs):"
                calling_as_if = "def some_tops_ls(tops):"

            else:

                if not args.tops:
                    py1 = "one_dir_ls()"
                    calling_to = "def one_dir_ls(top):"
                    calling_as_if = "def one_dir_ls():"
                else:
                    py1 = "one_dir_ls($TOP)"
                    calling_to = "def one_dir_ls(top):"
                    calling_as_if = calling_to

    calling = (calling_to, calling_as_if)

    return (py1, calling)


def args__to_whole_ls_py(args, py1, calling):
    """Fill out the missing Source Lines of Ls Py"""

    argnames = sorted(vars(args).keys())
    module_py = _scraps_.module_name__readlines(__name__)
    (calling_to, calling_as_if) = calling

    # Form enough more sourcelines, but keep only the chosen options

    py2 = py1
    py2 = _scraps_.py_pick_lines(py=py2, module_py=module_py)
    py2 = _scraps_.py_dedent_args(py=py2, args=args, argnames=argnames)
    assert py2 != py1, py1

    py3 = py2
    py3 = _scraps_.py_pick_lines(py=py3, module_py=module_py)
    py3 = _scraps_.py_dedent_args(py=py3, args=args, argnames=argnames)

    py4 = py3
    py4 = _scraps_.py_pick_lines(py=py4, module_py=module_py)
    py4 = _scraps_.py_dedent_args(py=py4, args=args, argnames=argnames)

    py5 = py4
    py5 = _scraps_.py_add_imports(py=py5, module_py=module_py)

    # Expand a single call of 'def some_names_ls' inline

    py6 = py5

    if (not args.topfiles) or (not args.topfiles):
        py6 = py6.replace(
            "    some_names_ls(names=names)\n\n\ndef some_names_ls(names):\n", ""
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
        if args.tall_columns:
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

    py8 = py8.replace("$TOPFILES", _scraps_.as_py_value(args.topfiles))
    py8 = py8.replace("$TOPDIRS", _scraps_.as_py_value(args.topdirs))
    py8 = py8.replace("$TOPS", _scraps_.as_py_value(args.some_tops))
    py8 = py8.replace("$TOP", _scraps_.as_py_value(args.last_top))

    py8 = py8.replace(calling_to, calling_as_if)

    return py8

    # # TODO: FIXME meta-comments differently and drop them

    # TODO: trace Bash in the DocStrings
    # TODO: calculate DocStrings by Args


def some_tops_ls(tops, topfiles, topdirs, args):  # noqa Flake8 C901 too complex

    if args.directory:

        for top in tops:
            _ = os.stat(top)
        some_names_ls(names=tops)

    if not args.directory:

        if args.topfiles:

            for topfile in topfiles:
                _ = os.stat(topfile)
            some_names_ls(names=topfiles)

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

                some_names_ls(names=names)


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

        some_names_ls(names=names)


def some_names_ls(names, args):  # noqa Flake8 C901 too complex

    if args.cells:

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

    if args.tall_columns:

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
