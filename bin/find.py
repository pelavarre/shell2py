#!/usr/bin/env python3

"""
usage: find.py [-h] [--maxdepth MAXDEPTH] [--name NAME] [--not] [--o]
               [--print] [--prune] [--type D]
               [TOP]

show the dirs of dirs here, and the files they contain

positional arguments:
  TOP                  where to start looking (default: '.')

optional arguments:
  -h, --help           show this help message and exit
  --maxdepth MAXDEPTH  look just here at depth 1, or also children at depth 2, etc
  --name NAME          find only names matching the glob pattern, such as '.?*'
  --not                reverse what follows, like '-not type d' to find files not dirs
  --o                  introduce an alt choice, such as to '-o -print'
  --print              show names not pruned, when asked to '-prune -o -print'
  --prune              don't show these names, maybe show some others
  --type D             find only dirs of dirs, not also files

quirks:
  linux makes you to type '-' in place of '--' for 'find' options
  linux makes you to type the TOP before the '-' and '--' options
  mac makes you spell out 'find .', in place of 'find', to search the current dir

examples:
  find -maxdepth 1 -type d  # dirs inside this dir, but not their children
  find -name '.?*'  # dirs and files inside, but only hidden ones
  find -name '.?*' -prune -o -print  # dirs and files inside, but not hidden ones
  find -type d  # all the dirs of dirs here
  find -not -type d  # all the files, none of the dirs
  find -type d -name '.?*' -prune -o -print  # like 'find -type d' but no hidden ones
"""

# TODO: -newer, -size

import sys

import _scraps_


def main(argv=None):

    as_argv = sys.argv if (argv is None) else argv

    _scraps_.to_py_main(name=__name__, argv=as_argv)


def bash2py(argv):

    args = parse_find_args(argv)
    args_not = vars(args)["not"]

    top = args.top if args.top else "."

    if args.type and args.type != "d":
        return

    drop_deeper = args.maxdepth
    drop_dirs = args.type and args_not
    drop_files = args.type and not args_not
    drop_hidden = args.name and args.prune and args.o and args.print
    take_hidden = args.name and not drop_hidden

    assert not (drop_dirs and drop_files)
    assert not (drop_hidden and take_hidden)

    if args_not:
        if not drop_dirs:
            return

    if args.prune or args.o or args.print:
        if not drop_hidden:
            return

    # TODO: comment options into source

    py = """

        import os

        def find(top):

            print(top)
            for (dirpath, dirnames, filenames) in os.walk(top):
#if DROP_DEEPER
                depth = 1 + dirpath.count(os.sep)

                if depth > $MAXDEPTH:
                    continue
#endif

#if DROP_DIRS
#else
                for dirname in dirnames:
                    found_dir = os.path.join(dirpath, dirname)
  #if DROP_HIDDEN
                    if dirname.startswith("."):  # if Dir is hidden
                        continue
  #endif
  #if TAKE_HIDDEN
                    if not dirname.startswith("."):  # if Dir isn't hidden
                        continue
  #endif

                    print(found_dir)
#endif

#if DROP_FILES
#else
                for filename in filenames:
                    found_file = os.path.join(dirpath, filename)
  #if DROP_HIDDEN
                    if filename.startswith("."):  # if File is hidden
                        continue
  #endif
  #if TAKE_HIDDEN
                    if not filename.startswith("."):  # if File isn't hidden
                        continue
  #endif

                    print(found_file)
#endif

        find(top=$TOP)

        """

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
    if args.maxdepth is None:
        assert "$MAXDEPTH" not in py
    else:
        py = py.replace("$MAXDEPTH", args.maxdepth)

    return py


def parse_find_args(argv):

    as_argv = list(argv)
    for (index, arg) in enumerate(as_argv):
        if arg.startswith("-") and not arg.startswith("--"):
            as_argv[index] = "-" + arg

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

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
        action="count",
        help="reverse what follows, like '-not type d' to find files not dirs",
    )

    parser.add_argument(
        "--o",
        action="count",
        default=0,
        help="introduce an alt choice, such as to '-o -print'",
    )

    parser.add_argument(
        "--print",
        action="count",
        default=0,
        help="show names not pruned, when asked to '-prune -o -print'",
    )

    parser.add_argument(
        "--prune",
        action="count",
        default=0,
        help="don't show these names, maybe show some others",
    )

    parser.add_argument(
        "--type",
        metavar="D",
        dest="type",
        help="find only dirs of dirs, not also files",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(as_argv[1:])

    return args


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
