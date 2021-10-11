#!/usr/bin/env python3

"""
usage: echo.py [-h] [-n] [--verbose] [WORD ...]

show some words

positional arguments:
  WORD        a word to show

optional arguments:
  -h, --help  show this help message and exit
  -n          show just the words, don't add a line-break
  --verbose   show each word separately, don't join them together as one line

quirks:
  takes '-n' like Bash or Zsh Echo, unlike Sh Echo
  gets 'shell2py echo ...' to show your Shell splitting apart your chars

examples:
  echo 'Hello, Echo World!'
  echo -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ' |hexdump -C
  echo.py --v 'Hello,' 'Echo World!'
"""

import textwrap

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_echo_py)


def compile_echo_argdoc():
    """Convert the Echo Main Doc to an ArgParse Parser"""

    parser = _scraps_.compile_argdoc(epi="quirks:")

    parser.add_argument(
        "-n", action="count", help="show just the words, don't add a line-break"
    )
    parser.add_argument(
        "--verbose",
        action="count",
        help="show each word separately, don't join them together as one line",
    )
    parser.add_argument("words", metavar="WORD", nargs="*", help="a word to show")
    # TODO: distribute wise choice of 'nargs="..."' vs 'nargs="*"'

    _scraps_.parser_patch_usage(parser, metavar="WORD", nargs="*")

    _scraps_.exit_unless_doc_eq(parser)

    return parser


def argv__to_echo_py(argv):
    """Write the Python for an Echo ArgV, else print some Help and quit"""

    parser = compile_echo_argdoc()
    args = parser.parse_args(argv[1:])
    _scraps_.args_cancel_pairs(args)

    echo_py_argv = "echo.py".split() + args.words

    if (args.n, args.verbose) == (None, None):
        return echo(argv=echo_py_argv)
    elif (args.n, args.verbose) == (True, None):
        return echo_n(argv=echo_py_argv)
    elif (args.n, args.verbose) == (None, True):
        return echo_verbose(argv=echo_py_argv)


def echo(argv):

    py = textwrap.dedent(
        """

        import sys

        # $SHLINE
        sys.argv = $ARGV  # unwanted if trying to echo a command line

        sys.stderr.flush()  # unneeded if not also writing Stderr
        print(*sys.argv[1:])
        sys.stdout.flush()  # unneeded if exiting now

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_value(argv))
    py = py.replace("$SHLINE", _scraps_.shlex_join(argv))

    return py


def echo_n(argv):

    py = textwrap.dedent(
        """

        import sys

        # $SHLINE
        sys.argv = $ARGV  # unwanted if trying to echo a command line

        sys.stderr.flush()  # unneeded if not also writing Stderr
        sys.stdout.write(" ".join(sys.argv[1:]))  # tada, no line break
        sys.stdout.flush()  # unneeded if exiting now

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_value(argv))
    py = py.replace("$SHLINE", _scraps_.shlex_join(argv))

    return py


def echo_verbose(argv):

    py = textwrap.dedent(
        """

        import sys

        # $SHLINE
        sys.argv = $ARGV  # unwanted if trying to echo a command line

        for (index, arg) in enumerate(sys.argv):
            if index:
                print("{}: {!r}".format(index, arg))

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_value(argv))
    py = py.replace("$SHLINE", _scraps_.shlex_join(argv))

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
