#!/usr/bin/env python3

"""
usage: echo.py [-h] [-n] [--verbose] [WORD [WORD ...]]

show some words

positional arguments:
  WORD        a word to show

optional arguments:
  -h, --help  show this help message and exit
  -n          show just the words, don't add a line-break
  --verbose   show each word separately, don't join them together as one line

quirks:
  understand "-n" like bash or zsh echo, unlike sh echo

examples:
  echo 'Hello, Echo World!'
  echo -n '⌃ ⌥ ⇧ ⌘ ← → ↓ ↑ ' |hexdump -C
  echo.py --v 'Hello,' 'Echo World!'
"""

import sys
import textwrap

import _scraps_


def main(argv=None):
    as_argv = sys.argv if (argv is None) else argv
    _scraps_.to_py_main(name=__name__, argv=as_argv)


def bash2py(argv):

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

    parser.add_argument(
        "-n", action="count", help="show just the words, don't add a line-break"
    )
    parser.add_argument(
        "--verbose",
        action="count",
        help="show each word separately, don't join them together as one line",
    )
    parser.add_argument("words", metavar="WORD", nargs="...", help="a word to show")

    usage = parser.format_usage()
    assert usage == "usage: echo.py [-h] [-n] [--verbose] ...\n", repr(usage)
    parser.usage = __doc__.strip().splitlines()[0][len("usage: ") :]

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(argv[1:])

    if (args.n, args.verbose) == (None, None):
        return echo(args.words)
    elif (args.n, args.verbose) == (True, None):
        return echo_n(args.words)
    elif (args.n, args.verbose) == (None, True):
        return echo_verbose(args.words)


def echo(words):

    py = textwrap.dedent(
        """

        import sys

        sys.argv = $ARGV  # delete this line to stop replacing the args

        sys.stderr.flush()  # unneeded if not also writing Stderr
        print(*sys.argv[1:])
        sys.stdout.flush()  # unneeded if exiting now

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_argv(words))

    return py


def echo_n(words):

    py = textwrap.dedent(
        """

        import sys

        sys.argv = $ARGV  # delete this line to stop replacing the args
        str_args = " ".join(sys.argv[1:])

        sys.stderr.flush()  # unneeded if not also writing Stderr
        sys.stdout.write(str_args)  # tada, no line break
        sys.stdout.flush()  # unneeded if exiting now

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_argv(words))

    return py


def echo_verbose(words):

    py = textwrap.dedent(
        """

        import sys

        sys.argv = $ARGV  # delete this line to stop replacing the args

        for (index, arg) in enumerate(sys.argv):
            if index:
                print("{}: {!r}".format(index, arg))

        """
    ).strip()
    py = py.replace("$ARGV", _scraps_.as_py_argv(words))

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
