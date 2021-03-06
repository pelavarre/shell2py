#!/usr/bin/env python3

"""
usage: find.py [-h] [--maxdepth MAXDEPTH] [--name NAME] [--not] [--prune] [--o]
               [--type D] [--print]
               [TOP]

show a top dir of dirs, and the files and dirs it contains

positional arguments:
  TOP                  where to start looking (default: '.')

optional arguments:
  -h, --help           show this help message and exit
  --maxdepth MAXDEPTH  look just here at depth 1, or also children at depth 2, etc
  --name NAME          find only names matching the glob pattern, such as '.?*'
  --not                reverse what follows, like '-not type d' to find files not dirs
  --prune              don't show these names, maybe show some others
  --o                  introduce an alt choice, such as to '-o -print'
  --type D             find only dirs of dirs, not also files
  --print              show names not pruned, when asked to '-prune -o -print'

quirks:
  gets many combinations wrong, such as:  find . -type d -name '.?*' -prune -o -print
  Linux & Mac make you to type '-' in place of '--' for 'find' options
  Linux * Mac make you type the TOP only before the '-' or '--' options, never after
  Mac makes you spell out 'find .', in place of 'find', to search the Current Dir

examples:
  find . -maxdepth 1 -type d  # dirs inside this dir, but not their children
  find . -name '.?*'  # dirs and files inside, but only hidden ones
  find . -name '.?*' -prune -o -print  # dirs and files inside, but not hidden ones
  find . -type d  # all the dirs of dirs here
  find . -not -type d  # all the files, none of the dirs
  find . -type d -name '.?*' -prune -o -print  # like 'find -type d' but no hidden ones
"""

# TODO: -newer, -size

import sys

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_find_py)


def parse_find_args(argv):
    """Convert a Find Sys ArgV to an Args Namespace, or print some Help and quit"""

    # Open up

    parser = compile_find_argdoc()

    altv = list(argv)
    for (index, arg) in enumerate(altv):
        if arg.startswith("-") and not arg.startswith("--"):
            altv[index] = "-" + arg  # change to "--" from "-"

    # Parse args

    args = parser.parse_args(altv[1:])
    _scraps_.args_cancel_pairs(args, exclusions="maxdepth".split())

    # Close out

    if args.maxdepth is not None:

        try:
            _ = int(args.maxdepth)
        except ValueError as exc:
            sys.stderr.write("find.py: error: argument -maxdepth: {}\n".format(exc))

            sys.exit(2)

    return args


def compile_find_argdoc():
    """Convert the Find Main Doc to an ArgParse Parser"""

    parser = _scraps_.compile_argdoc(epi="quirks:")

    parser.add_argument(
        "top", metavar="TOP", nargs="?", help="where to start looking (default: '.')"
    )

    parser.add_argument(
        "--maxdepth",
        metavar="MAXDEPTH",
        dest="maxdepth",
        help="look just here at depth 1, or also children at depth 2, etc",
    )

    parser.add_argument(
        "--name",
        metavar="NAME",
        dest="name",
        help="find only names matching the glob pattern, such as '.?*'",
    )

    parser.add_argument(
        "--not",
        dest="not_",
        action="count",
        help="reverse what follows, like '-not type d' to find files not dirs",
    )

    parser.add_argument(
        "--prune",
        action="count",
        default=0,
        help="don't show these names, maybe show some others",
    )

    parser.add_argument(
        "--o",
        action="count",
        default=0,
        help="introduce an alt choice, such as to '-o -print'",
    )

    parser.add_argument(
        "--type",
        metavar="D",
        dest="type",
        help="find only dirs of dirs, not also files",
    )

    parser.add_argument(
        "--print",
        action="count",
        default=0,
        help="show names not pruned, when asked to '-prune -o -print'",
    )

    _scraps_.exit_unless_doc_eq(parser)

    return parser


def argv__to_find_py(argv):
    """Write the Python for a Find ArgV, else print some Help and quit"""

    args = parse_find_args(argv)

    top = args.top if args.top else "."

    # Reject obvious contradictions

    drop_deeper = args.maxdepth
    drop_dirs = args.type and args.not_
    drop_files = args.type and not args.not_
    drop_hidden = args.name and args.prune and args.o and args.print
    take_hidden = args.name and not drop_hidden

    exit_unless_simple_find(
        args,
        drop_deeper=drop_deeper,
        drop_dirs=drop_dirs,
        drop_files=drop_files,
        drop_hidden=drop_hidden,
        take_hidden=take_hidden,
    )

    # Form a stylish copy of the Shell Find Command Line

    shline = shlex_join_find(args)

    # Form the Python

    py = '''

        import os

        def find(top):
            """$SHLINE"""

            print(top)
            for (dirpath, dirnames, filenames) in os.walk(top):

#if DROP_DEEPER
                depth = 1 + dirpath.count(os.sep)
                if depth > $MAXDEPTH:
                    continue

#endif
#if DROP_DIRS
#else
  #if DROP_HIDDEN
                dirnames[:] = list(_ for _ in dirnames if not _.startswith("."))
  #endif
  #if TAKE_HIDDEN
                dirnames[:] = list(_ for _ in dirnames if _.startswith("."))
  #endif
                dirnames[:] = sorted(dirnames)
                for dirname in dirnames:
                    found_dir = os.path.join(dirpath, dirname)
                    print(found_dir)

#endif
#if DROP_FILES
#else
  #if DROP_HIDDEN
                filenames[:] = list(_ for _ in filenames if not _.startswith("."))
  #endif
  #if TAKE_HIDDEN
                filenames[:] = list(_ for _ in filenames if _.startswith("."))
  #endif
                filenames[:] = sorted(filenames)
                for filename in filenames:
                    found_file = os.path.join(dirpath, filename)
                    print(found_file)

#endif
        find(top=$TOP)

        '''

    py = _scraps_.c_pre_process(
        py,
        cpp_vars=dict(
            drop_deeper=drop_deeper,
            drop_dirs=drop_dirs,
            drop_files=drop_files,
            drop_hidden=drop_hidden,
            take_hidden=take_hidden,
        ),
    )

    py = py.replace("$TOP", _scraps_.as_py_value(top))
    py = py.replace("$SHLINE", shline)
    if args.maxdepth is None:
        assert "$MAXDEPTH" not in py
    else:
        py = py.replace("$MAXDEPTH", args.maxdepth)

    return py


def exit_unless_simple_find(
    args, drop_deeper, drop_dirs, drop_files, drop_hidden, take_hidden
):
    """Reject obvious Find option contradictions, as if untranslatable"""

    if args.name and (args.name != ".?*"):
        sys.stderr.write(
            "find.py: error: argument -name {}: choose {!r}\n".format(
                _scraps_.shlex_quote(args.name), _scraps_.shlex_quote(".?*")
            )
        )

        sys.exit(2)

    if args.type and (args.type != "d"):
        sys.stderr.write(
            "find.py: error: argument -type {}: choose d\n".format(
                _scraps_.shlex_quote(args.name)
            )
        )

        sys.exit(2)

    assert not (drop_dirs and drop_files)
    assert not (drop_hidden and take_hidden)

    if not drop_dirs:
        if args.not_:
            sys.stderr.write("find.py: error: argument -not {}: choose -not -type d\n")

            sys.exit(2)

    if not drop_hidden:
        for argname in "prune o print".split():
            if vars(args)[argname]:
                sys.stderr.write(
                    "find.py: error: argument -{}: choose -prune -o -print\n".format(
                        argname
                    )
                )

                sys.exit(2)


def shlex_join_find(args):
    """Form a stylish copy of the Shell Find Command Line"""

    shline = "find"
    if args.maxdepth:
        shline += " -maxdepth {}".format(args.maxdepth)
    if args.name:
        shline += " -name {}".format(_scraps_.shlex_quote(args.name))
    if args.not_:
        shline += " -not"
    if args.prune:
        shline += " -prune"
    if args.o:
        shline += " -o"
    if args.type:
        shline += " -type {}".format(args.type)
    if args.print:
        shline += " -print"

    return shline


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
