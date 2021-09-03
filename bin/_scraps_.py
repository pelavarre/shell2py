"""
Docs Python folk are still working up a sincere and competent welcome for contribution

Someday they might start publishing these fragments too
"""

import __main__
import argparse
import ast
import difflib
import os
import sys


# deffed in many files  # missing from docs.python.org
def as_py_argv(words):
    """Convert a List of Strings to the Python that means form an equal List"""

    argv = [None] + words

    rep = repr(argv)
    if '"' not in rep:
        rep = rep.replace("'", '"')

    evalled = ast.literal_eval(rep)
    assert evalled == argv, (evalled, argv)

    return rep


# deffed in many files  # missing from docs.python.org
def compile_argdoc(epi, doc=None, drop_help=None):
    """Construct the 'argparse.ArgumentParser' with Epilog but without Arguments"""

    as_doc = __main__.__doc__ if (doc is None) else doc

    prog = as_doc.strip().splitlines()[0].split()[1]
    description = list(_ for _ in as_doc.strip().splitlines() if _)[1]
    epilog_at = as_doc.index(epi)
    epilog = as_doc[epilog_at:]

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=not drop_help,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog,
    )

    return parser


# deffed in many files  # missing from docs.python.org
def exit_unless_doc_eq(parser, file, doc):
    """Exit nonzero, unless __main__.__doc__ equals "parser.format_help()" """

    got_file = __main__.__file__ if (file is None) else file
    got_file = os.path.split(got_file)[-1]
    got_file = "./{} --help".format(got_file)

    got_doc = __main__.__doc__ if (file is None) else doc
    got_doc = got_doc.strip()

    want_doc = parser.format_help()
    want_file = "argparse.ArgumentParser(..."

    diff_lines = list(
        difflib.unified_diff(
            a=got_doc.splitlines(),
            b=want_doc.splitlines(),
            fromfile=got_file,
            tofile=want_file,
        )
    )

    if diff_lines:

        lines = list((_.rstrip() if _.endswith("\n") else _) for _ in diff_lines)
        sys.stderr.write("\n".join(lines) + "\n")

        sys.exit(1)  # trust caller to log SystemExit exceptions well


# deffed in many files  # missing from docs.python.org
def shell_to_py(module, argv):
    """Convert one Shell Line to Python, else Print the Help for it, else Exit Loudly"""

    file = os.path.basename(module.__file__)
    doc = module.__doc__
    bash2py = module.bash2py

    py = bash2py(argv)

    if py is None:
        usage = doc.strip().splitlines()[0]
        sys.stderr.write(usage + "\n")
        sys.stderr.write("{}: error: need stronger translator\n".format(file))
        sys.exit(3)

    if not py:
        print(doc.strip())
        sys.exit(0)

    return py


# deffed in many files  # missing from docs.python.org
def to_py_main(name, argv):
    """Convert one Shell Line to Python and run it"""

    module = sys.modules[name]
    py = shell_to_py(module, argv=argv)
    exec(py)


# copied by: git clone https://github.com/pelavarre/shell2py.git
