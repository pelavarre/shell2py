#!/usr/bin/env python3

"""
usage: shell2py.py [-h] VERB [WORD [WORD ...]]

say in Python what you said in Shell

positional arguments:
  VERB        the first word of a Shell line, being the program to run
  WORD        another word of a Shell line, being an arg of the program to run

optional arguments:
  -h, --help  show this help message and exit

examples:
  shell2py -h  # show this help message and exit
  ls.py -1  # show the files and dirs inside a dir
  shell2py ls -1  # show how to say 'ls -1' in Python
  echo.py a 'b c'  # show some words
  shell2py echo a 'b c'  # show how your Shell splits apart the chars you're typing
  ls bin/*  # show the verbs of Bash that this revision of Shell2Py will explain
"""

import argparse
import glob
import os
import sys

import _scraps_

import dig

import echo

import find

import grep

import less

import ls

import scp

import ssh

import tac

import tar


def main():

    argv = sys.argv
    altv = sys.argv[1:]

    # TODO: import just the modules needed for this run of the main args

    _ = (dig, echo, find, grep, less, ls, scp, ssh, tac, tar)

    # Discover the Python modules of Shell Verbs near here

    file_dir = os.path.dirname(os.path.abspath(__file__))

    with_dir = os.getcwd()
    os.chdir(file_dir)
    try:
        hits = glob.glob("*.py")
    finally:
        os.chdir(with_dir)

    # Quit now if the Verb not found

    verbs = sorted(os.path.splitext(_)[0] for _ in hits if not _.startswith("_"))
    verbs = list(_ for _ in verbs if _ != "shell2py")
    str_verbs = ", ".join(repr(_) for _ in verbs)

    args = parse_shell2py_args(argv)

    if args.verb not in verbs:
        sys.stderr.write(
            "shell2py.py: error: "
            "argument VERB: invalid choice: {!r} (choose from {})\n".format(
                args.verb, str_verbs
            )
        )
        sys.exit(2)

    # Write the Python for a Shell Argv, else print some Help and quit

    name = args.verb
    argv__to_py_name = "argv__to_{}_py".format(name)
    module = sys.modules[name]
    argv__to_py = getattr(module, argv__to_py_name)

    py = _scraps_.module_name__to_main_py(name, argv__to_py=argv__to_py, argv=altv)

    # Print the Python formed

    print(py)


def parse_shell2py_args(argv):
    """Convert a Shell2Py Sys ArgV to an Args Namespace, or print some Help and quit"""

    # Print stripped doc & exit 0 if first arg is '-h', '--h', '--he', ... '--help'

    _scraps_.parse_left_help_args(argv, doc=__doc__)

    # Require Verb

    if not argv[1:]:
        usage = __doc__.strip().splitlines()[0]
        sys.stderr.write(usage + "\n")
        sys.stderr.write(
            "shell2py.py: error: the following arguments are required: VERB\n"
        )
        sys.exit(2)

    # Strip a "bin/" prefix and/or ".py.gz" suffix from the Verb

    verb = argv[1]
    verb = os.path.basename(verb)  # such as "find.py" from "bin/find.py"
    verb = verb.split(os.extsep)[0]  # such as "find" from "find.py.gz"

    # Return the Verb inside a Namespace of Parsed Args

    args = argparse.Namespace(verb=verb)

    return args


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
