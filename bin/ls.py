#!/usr/bin/env python3

"""
usage: ls.py [--help] [-1 | -l | -C] [--headings] [--full-time] [-X | -f] [-a] [-d]
             [-F]
             [TOP ...]

show the files and dirs inside some dirs

positional arguments:
  TOP              a file or dir to show (default: show '.' current dir)

optional arguments:
  --help           show this help message and exit
  -1               show one name per line
  -l               show details of perms, links, user, group, bytes, stamp, name
  -C               show columns of names (default: True)
  --headings       insert a row of headings before the rows of '-l' details
  --full-time      stamp with a more precise date/time in the rows of '-l' details
  -X               sort by ext (default: sort by name)
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
import datetime as dt
import grp
import os
import pathlib
import pwd
import stat
import sys

import _scraps_


DENT = 4 * " "  # solve only the case of in/out/dent'ed by 4 columns


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

    parser = _scraps_.compile_argdoc(epi="quirks:", drop_help=True)
    parser.add_argument(
        "--help", action="count", help="show this help message and exit"
    )

    parser.add_argument(
        "tops",
        metavar="TOP",
        nargs="*",
        help="a file or dir to show (default: show '.' current dir)",
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
    group_Xf.add_argument(
        "-X", action="count", help="sort by ext (default: sort by name)"
    )
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

    _scraps_.parser_patch_usage(parser, metavar="TOP", nargs="*")

    _scraps_.exit_unless_doc_eq(parser)

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

    # Don't yet translate Usage: '[--headings] [--full-time]'

    if args.headings or args.full_time:
        return

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
                    py1 = "one_stat_ls(name=$TOP)"
                    calling_to = "def one_stat_ls(name):"
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
    py2 = edit_ls_py(py=py2, args=args, argnames=argnames, module_py=module_py)
    assert py2 != py1, py1

    py3 = py2
    py3 = edit_ls_py(py=py3, args=args, argnames=argnames, module_py=module_py)

    py4 = py3
    py4 = edit_ls_py(py=py4, args=args, argnames=argnames, module_py=module_py)

    py5 = py4
    py5 = edit_ls_py(py=py5, args=args, argnames=argnames, module_py=module_py)

    # Expand a single call of 'def some_names_ls' inline

    py6 = py5

    py6 = py6.replace(
        "# Choose an order of names\n ", "# Choose an order of names\n\n "
    )  # TODO: less custom styling

    while "\n\n\n " in py6:
        py6 = py6.replace("\n\n\n ", "\n\n ")

    # Reduce Stats to Names, when not showing Stats
    # Emit an implicit $TOPS if called with an implicit $TOPS

    py7 = py6

    if not args.classify and not args.long_rows:

        py7 = reduce_ls_py_stats_to_names(py=py7, module_py=module_py)

    py7 = py7.replace(", args=args)", ")")

    if (not args.topfiles) or (not args.topdirs):

        py7 = py7.replace(
            "\n    some_names_ls(names)\n\n\ndef some_names_ls(names):\n", "\n"
        )

        old = "\nsome_names_ls(names)\n\n\ndef some_names_ls(names):\n"
        if old in py7:

            py7 = py7.replace(
                old,
                "\ndef some_names_ls(names):\n",
            )

            def_some_names_ls = "def some_names_ls(names):"
            py7 = _scraps_.py_dedent(py=py7, line=def_some_names_ls, truthy=True)

        py7 = py7.replace(
            "\n\n\n    for name in sorted(names):\n",
            "\n\n    for name in sorted(names):\n",
        )

    py7 = py7.replace(
        "\n\n\n    some_names_ls(names)\n", "\n\n    some_names_ls(names)\n"
    )

    py7 = py7.replace("def one_dir_ls():\n ", "def one_dir_ls():\n\n ")
    py7 = py7.replace("def one_dir_ls(top):\n ", "def one_dir_ls(top):\n\n ")

    if py1 == "one_dir_ls()":

        if not args.cells:
            py7 = py7.replace("(top)", "()")
        else:
            def_one_dir = "def one_dir_ls(top):"
            assert def_one_dir in py7
            py7 = _scraps_.py_dedent(py7, line=def_one_dir, truthy=True)
            py7 = py7.replace("import os\n\n\n\n", "import os\n\n")
            py7 = py7.replace("(top)", "()")
            py7 = py7.replace("os.stat(os.path.join(top, name))", "os.stat(name)")
            py7 = py7.replace("\n\n\none_dir_ls()", "")

        py7 = py7.replace(
            "sub_stats = {_: os.stat(os.path.join(top, _)) for _ in names}",
            "sub_stats = {_: os.stat(_) for _ in names}",
        )

        # TODO: less custom styling

    py7 = py7.replace(calling_to, calling_as_if)

    py7 = _scraps_.py_add_imports(py=py7, module_py=module_py)

    py7 = py7.replace("\n\n\nnames = os.listdir()\n", "\n\nnames = os.listdir()\n")
    py7 = py7.replace(
        "\n\n\nnames = list([os.curdir, os.pardir] + os.listdir())\n",
        "\n\nnames = list([os.curdir, os.pardir] + os.listdir())\n",
    )

    # Inject strings, last of all

    py8 = py7

    while "\n\n\n    " in py8:  # also strip extra blank lines from inside Def's
        py8 = py8.replace("\n\n\n    ", "\n\n    ")

    py8 = py8.replace("$TOPFILES", _scraps_.as_py_value(args.topfiles))
    py8 = py8.replace("$TOPDIRS", _scraps_.as_py_value(args.topdirs))
    py8 = py8.replace("$TOPS", _scraps_.as_py_value(args.some_tops))
    py8 = py8.replace("$TOP", _scraps_.as_py_value(args.last_top))

    return py8

    # # TODO: FIXME meta-comments differently and drop them

    # TODO: trace Bash in the DocStrings
    # TODO: calculate DocStrings by Args


def edit_ls_py(py, args, argnames, module_py):
    """Fill out the next layer of missing Source Lines of an Ls Py"""

    py1 = py
    py1 = _scraps_.py_pick_lines(py=py1, module_py=module_py)
    py1 = _scraps_.py_dedent_args(py=py1, args=args, argnames=argnames)

    if not args.classify and not args.long_rows:
        py1 = py1.replace("stats_item_print", "print")

    return py1


def reduce_ls_py_stats_to_names(py, module_py):
    """Reduce Stats to Names"""

    py1 = py

    # List the pairs of changes

    diffs = """
-         tops_stats = dict()
+
-             tops_stats[top] = os.stat(top)
+             _ = os.stat(top)
-         some_stats_ls(stats=tops_stats)
+         some_names_ls(names=tops)
-             topfiles_stats = dict()
+
-                 topfiles_stats[topfile] = os.stat(topfile)
+                 _ = os.stat(topfile)
-             some_stats_ls(stats=topfiles_stats)
+             some_names_ls(names=topfiles)
-                 topdir_sub_stats = {_: os.stat(os.path.join(topdir, _)) for _ in names}
+
-                 some_stats_ls(stats=topdir_sub_stats)
+                 some_names_ls(names)
-             top_item = (top, os.stat(top))
+             _ = os.stat(top)
-             stats_item_print(top_item, args=args)
+             print(top)
-         sub_stats = {_: os.stat(os.path.join(top, _)) for _ in names}
+
-         some_stats_ls(stats=sub_stats)
+         some_names_ls(names)
- def some_stats_ls(stats, args):
+ def some_names_ls(names, args):
-             for item in stats.items():
+             for name in names:
-                 stats_item_print(item, args=args)
+                 print(name)
-                 stats.items(), key=lambda _: (pathlib.Path(_[0]).suffix, _[0])
+                 names, key=lambda _: (pathlib.Path(_]).suffix, _)
-             for item in items:
+             for name in names:
-                 stats_item_print(item, args=args)
+                 print(name)
-                 for item in sorted(stats.items()):
+                 for name in sorted(names):
-                     stats_item_print(item, args=args)
+                     print(name)
-             sorted_items = list(stats.items())
+             cells = names
-             sorted_items = sorted(
+             cells = sorted(
-                 stats.items(), key=lambda _: (pathlib.Path(_[0]).suffix, _[0])
+                 names, key=lambda _: (pathlib.Path(_).suffix, _)
-                 sorted_items = sorted(stats.items())
+                 cells = sorted(names)
-             cells = list(_[0] for _ in sorted_items)
+
-             cells = list(stats_item_format(_, args) for _ in sorted_items)
+
- def one_stat_ls(name, args):
+ def one_name_ls(name, args):
-         item = (name, os.stat(name))
+         _ = os.stat(name)
-         stats_item_print(item, args=args)
+         print(name)
    """

    difflines = diffs.splitlines()
    assert not difflines[0], repr(difflines[0])
    assert not difflines[-1].strip(), repr(difflines[-1].strip())
    difflines = difflines[1:-1]

    assert (len(difflines) % 2) == 0, len(difflines)

    stripped_olds_set = set()
    pairs = list(zip(difflines, difflines[1:]))[::2]
    for pair in pairs:
        (stale, fresh) = pair

        # Pick out a pair of changes

        assert stale.startswith("- "), (fresh, stale)
        old = "\n" + stale[len("- ") :] + "\n"
        assert old in module_py, (old, fresh)

        assert fresh.startswith("+ ") or (fresh == "+"), (fresh, stale)
        new = "\n" + fresh[len("+ ") :] + "\n"
        if new == "\n\n":
            new = "\n"

        # Set up to apply the change as if inside a larger blank area

        dented1 = "\n".join((DENT + _) for _ in py1.splitlines())
        enclosed1 = "\n" + dented1 + "\n"

        unrolled1 = enclosed1[len("\n") : -len("\n")]
        undented1 = "\n".join(_[len(DENT) :] for _ in unrolled1.splitlines())

        assert undented1 == py1

        # Apply the change without regard to indentation

        stripped_old = old
        stripped_old = stripped_old.replace(", args)", ")")
        stripped_old = stripped_old.replace("stats_item_print", "print")
        stripped_old = stripped_old.strip() + "\n"

        stripped_new = new
        stripped_new = stripped_new.replace(", args)", ")")
        stripped_new = stripped_new.replace("stats_item_print", "print")
        stripped_new = stripped_new.strip() + "\n"

        enclosed2 = enclosed1
        if stripped_old in stripped_olds_set:
            if stripped_old:
                assert stripped_old not in py1, stripped_old
        else:
            stripped_olds_set.add(stripped_old)
            enclosed2 = enclosed1.replace(stripped_old, stripped_new)

        # Pick the changed text out of the larger blank area

        unrolled2 = enclosed2[len("\n") : -len("\n")]
        undented2 = "\n".join(_[len(DENT) :] for _ in unrolled2.splitlines())

        py1 = undented2

    # Strip trailing spaces in any line

    py1 = "\n".join(_.rstrip() for _ in py1.splitlines())

    # Change partial lines

    py1 = py1.replace("one_stat_ls(name=", "one_name_ls(")

    return py1


def some_tops_ls(tops, topfiles, topdirs, args):  # noqa Flake8 C901 too complex

    if args.directory:

        tops_stats = dict()
        for top in tops:
            tops_stats[top] = os.stat(top)
        some_stats_ls(stats=tops_stats)

    if not args.directory:

        if args.topfiles:

            topfiles_stats = dict()
            for topfile in topfiles:
                topfiles_stats[topfile] = os.stat(topfile)
            some_stats_ls(stats=topfiles_stats)

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

                topdir_sub_stats = {_: os.stat(os.path.join(topdir, _)) for _ in names}
                some_stats_ls(stats=topdir_sub_stats)


def one_dir_ls(top, args):

    if args.directory:

        if not args.long_rows:

            top_item = (top, os.stat(top))
            stats_item_print(top_item, args=args)

        if args.long_rows:

            print("total .")  # TODO: count blocks of 512B each

            top_item = (top, os.stat(top))
            row = stats_item_row(top_item, args=args)
            print("  ".join(row))

    if not args.directory:

        if args.all:
            names = list([os.curdir, os.pardir] + os.listdir(top))
        if not args.all:
            names = os.listdir(top)
            names = list(_ for _ in names if not _.startswith("."))

        sub_stats = {_: os.stat(os.path.join(top, _)) for _ in names}
        some_stats_ls(stats=sub_stats)


def some_stats_ls(stats, args):  # noqa Flake8 C901 too complex

    if args.cells:

        if args.f:
            for item in stats.items():
                stats_item_print(item, args=args)
        if args.X:
            items = sorted(
                stats.items(), key=lambda _: (pathlib.Path(_[0]).suffix, _[0])
            )
            for item in items:
                stats_item_print(item, args=args)
        if not args.f:
            if not args.X:
                for item in sorted(stats.items()):
                    stats_item_print(item, args=args)

    if args.long_rows:

        print("total .")  # TODO: count blocks of 512B each

        rows = list()
        if args.f:
            for item in stats.items():
                row = stats_item_row(item, args=args)
                rows.append(row)
        if args.X:
            items = sorted(
                stats.items(), key=lambda _: (pathlib.Path(_[0]).suffix, _[0])
            )
            for item in items:
                row = stats_item_row(item, args=args)
                rows.append(row)
        if not args.f:
            if not args.X:
                for item in sorted(stats.items()):
                    row = stats_item_row(item, args=args)
                    rows.append(row)

        chars = format_rows_as_columns(rows)
        print(chars)

    if args.tall_columns:

        # Choose an order of names

        if args.f:
            sorted_items = list(stats.items())
        if args.X:
            sorted_items = sorted(
                stats.items(), key=lambda _: (pathlib.Path(_[0]).suffix, _[0])
            )
        if not args.f:
            if not args.X:
                sorted_items = sorted(stats.items())

        # Guess the width of the Terminal

        tty_size = argparse.Namespace(columns=80, lines=24)  # classic Terminal
        try:
            tty_size = os.get_terminal_size()
        except OSError:
            pass  # such as Stdout redirected to file

        tty_columns = tty_size.columns

        # Pack names into columns

        if not args.classify:
            cells = list(_[0] for _ in sorted_items)
        if args.classify:
            cells = list(stats_item_format(_, args) for _ in sorted_items)
        chars = pack_cells_in_columns(cells, tty_columns=tty_columns, sep="  ")
        if chars:
            print(chars)


def one_stat_ls(name, args):

    if not args.long_rows:

        item = (name, os.stat(name))
        stats_item_print(item, args=args)

    if args.long_rows:

        print("total .")  # TODO: count blocks of 512B each

        item = (name, os.stat(name))
        row = stats_item_row(item, args=args)
        print("  ".join(row))


def stats_item_print(item, args):

    if not args.classify:

        assert False

    if not args.long_rows:

        if not args.classify:
            marked_name = item[0]
        if args.classify:
            marked_name = stats_item_format(item, args=args)
        print(marked_name)

    if args.long_rows:

        assert False


def stats_item_row(item, args):

    (item_name, item_stat) = item

    st_mode = item_stat.st_mode
    filemode = stat.filemode(st_mode)
    islnk = stat.S_ISLNK(st_mode)
    _ = islnk  # FIXME

    links = str(item_stat.st_nlink)

    gid_uid = (os.getgid(), os.getuid())

    st_gid = item_stat.st_gid
    st_uid = item_stat.st_uid
    st_gid_uid = (st_gid, st_uid)

    user_name = pwd.getpwuid(st_uid).pw_name
    user = "." if (st_gid_uid == gid_uid) else user_name

    group_name = grp.getgrgid(st_gid).gr_name
    group = "." if (st_gid_uid == gid_uid) else group_name

    st_mtime = item_stat.st_mtime
    item_datetime = dt.datetime.fromtimestamp(st_mtime)

    len_bytes = "." if filemode.startswith("d") else str(item_stat.st_size)
    stamp = item_datetime.strftime("%h %d %H:%M")
    if item_datetime.year != dt.datetime.now().year:
        stamp = item_datetime.strftime("%h %d %Y")
        # TODO: "%h %d %Y" for more than 6 months away

    if not args.classify:
        marked_name = item[0]
    if args.classify:
        marked_name = stats_item_format(item, args=args)

    row = (filemode, links, user, group, len_bytes, stamp, marked_name)

    return row


def stats_item_format(item, args):

    if not args.classify:
        assert False

    (item_name, item_stat) = item
    st_mode = item_stat.st_mode

    filemode = stat.filemode(st_mode)
    islnk = stat.S_ISLNK(st_mode)

    if args.classify:

        if filemode.startswith("d"):
            mark = "/"
        elif "x" in filemode:
            mark = "*"
        elif islnk:
            mark = "@"  # TODO: pass tests of this
        else:
            mark = ""  # wrong mark when it should be socket as '=', or door as '>'

    marked_name = item_name + mark

    return marked_name


def format_rows_as_columns(rows):
    """Format Rows of Cells as Vertically Aligned Columns of Cells"""

    justs = (
        str.ljust,
        str.rjust,
        str.ljust,
        str.ljust,
        str.rjust,
        str.ljust,
        str.ljust,
    )
    # justs for (filemode, links, user, group, len_bytes, stamp, marked_naem)

    columns = list(zip(*rows))
    widths = list(max(len(_) for _ in c) for c in columns)

    assert len(columns) == len(widths) == len(justs)

    padded_columns = list()
    for (column, just, width) in zip(columns, justs, widths):
        padded_column = list(just(_, width) for _ in column)
        padded_columns.append(padded_column)

    padded_rows = list(zip(*padded_columns))
    chars = "\n".join("  ".join(_).rstrip() for _ in padded_rows)

    return chars


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
