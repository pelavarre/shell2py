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
import textwrap


# deffed in many files  # missing from docs.python.org
def as_py_argv(words):
    """Convert a List of Strings to the Python that means form an equal List"""

    argv = [None] + words
    py = as_py_value(value=argv)

    return py


# deffed in many files  # missing from docs.python.org
def as_py_value(value):
    """Convert a Value to the Python that means form an equal Value"""

    rep = repr(value)
    if '"' not in rep:
        rep = rep.replace("'", '"')

    evalled = ast.literal_eval(rep)
    assert evalled == value, (evalled, value)

    return rep


# deffed in many files  # missing from docs.python.org
def c_pre_process(chars, cpp_vars):
    """Emulate the Linux 'cpp' C Programming Language Pre-Processor"""

    lines = chars.splitlines()

    votes = list()

    def cpp_get(cpp_vars, word):
        """Require UPPERCASE input, return lowercase equivalent"""

        assert word == word.upper(), word
        key = word.lower()

        assert key in cpp_vars.keys(), (key, cpp_vars)
        value = cpp_vars[key]

        return value

    emits = list()
    for line in lines:

        stripped = line.strip()
        if stripped.startswith("#"):
            cpp_source = "#" + stripped[len("#") :].partition("#")[0]
            cpp_words = cpp_source.split()
            if cpp_words:
                cpp_verb = cpp_words[0]

                if cpp_verb == "#":

                    pass

                elif cpp_verb == "#if":
                    assert len(cpp_words) == 2, cpp_words
                    value = cpp_get(cpp_vars, word=cpp_words[1])

                    vote = value or None
                    votes.append(vote)

                elif cpp_verb == "#elif":
                    assert len(cpp_words) == 2, cpp_words
                    value = cpp_get(cpp_vars, word=cpp_words[1])

                    got_vote = votes.pop()

                    vote = False
                    if got_vote is None:
                        vote = value or None

                    votes.append(vote)

                elif cpp_verb == "#else":
                    assert len(cpp_words) == 1, cpp_words

                    got_vote = votes.pop()

                    vote = got_vote is None

                    votes.append(vote)

                elif cpp_verb == "#endif":
                    assert len(cpp_words) == 1, cpp_words

                    votes.pop()

                else:

                    raise Exception("meaningless C Pre-Processing Verb", cpp_verb)

            continue

        if all(votes):
            emits.append(line)

    result = "\n".join(emits)
    result = textwrap.dedent(result).strip()

    return result


# deffed in many files  # missing from docs.python.org
def compile_argdoc(epi, doc=None, drop_help=None):
    """Construct the 'argparse.ArgumentParser' with Epilog but without Arguments"""

    as_doc = __main__.__doc__ if (doc is None) else doc

    prog = as_doc.strip().splitlines()[0].split()[1]

    description = list(
        _ for _ in as_doc.strip().splitlines() if _ and not _.startswith(" ")
    )[1]

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

    with_columns = os.getenv("COLUMNS")
    os.environ["COLUMNS"] = str(80)
    try:
        want_doc = parser.format_help()
    finally:
        if with_columns is None:
            os.environ.pop("COLUMNS")
        else:
            os.environ["COLUMNS"] = with_columns

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
        sys.stderr.write(
            "{}: error: need stronger translator, "
            "meanwhile the '{} --help' examples do work\n".format(file, file)
        )
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
