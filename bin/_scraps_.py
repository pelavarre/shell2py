"""
Collect scraps of Code held in common by the Py near here, aka tools, utils, etc
"""

import __main__
import argparse
import ast
import contextlib
import difflib
import os
import pdb
import re
import shlex
import string
import sys

import textwrap


def b():
    pdb.set_trace()


#
# Rough edits of simple Py sources can produce correct Code
#


def as_py_value(value):
    """Convert a Value to the Python that means form an equal Value"""

    rep = repr(value)
    if '"' not in rep:
        rep = rep.replace("'", '"')

    evalled = ast.literal_eval(rep)
    assert evalled == value, (evalled, value)

    return rep


def py_pick_lines(py, module_py):
    """Pick out enough more lines from the 'module_py' to run the 'py' well"""

    paras = split_paragraphs(py.splitlines())
    core_py = "\n".join(paras[-1])  # TODO: more robust/ elegant

    # Add Defs of Mentioned Names till no more Defs found,
    # but go wrong over Dynamic Names, Non-Ascii Names, etc

    names = sorted(set(re.findall(r"[A-Z_a-z][0-9A-Z_a-z]*", string=py)))
    def_lines = _py_pick_def_lines(names, module_py=module_py)
    defs_py = _py_pick_defs(def_lines, module_py=module_py)

    import_lines = _py_pick_import_lines(names, module_py=module_py)
    import_py = "\n".join(import_lines)

    got_py = import_py + "\n\n\n" + defs_py + "\n\n\n" + core_py
    got_py = got_py.strip()  # such as empty 'import_py'

    return got_py


def _py_pick_defs(def_lines, module_py):
    """Pick out each Def Line and its Body, as ordered by Module Py"""

    def_lines_set = set(def_lines)
    inlines = module_py.splitlines()

    outlines = list()
    for (index, inline) in enumerate(inlines):
        if inline in def_lines_set:

            if True:  # TODO: more elegant tie to comments before 'def' func
                if inline == "def stderr_print(*args, **kwargs):":
                    outlines.append(
                        "# deffed in many files  # missing from docs.python.org"
                    )

            outlines.append(inline)

            # Copy Lines of the Body till next Outdent,
            # but go wrong over Comments, Multi-Line Strings, etc

            for inline in inlines[(index + 1) :]:
                if inline and not inline.startswith(" "):

                    break

                outlines.append(inline)

                continue

    chars = "\n".join(outlines).strip()

    return chars


def _py_pick_def_lines(names, module_py):
    """Pick top-level 'def' lines from 'module_py' that define words of 'py'"""

    # Pick out Top-Level Def Lines
    # but go wrong over Comments, Multi-Line Strings, etc

    def_line_by_name = dict()
    for line in module_py.splitlines():
        words = line.split()
        if words and (words[0] == "def"):
            deffed_name = words[1].split("(")[0]

            assert deffed_name not in def_line_by_name, deffed_name
            def_line_by_name[deffed_name] = line

    # Pick out Top-Level Def Lines that got a Mention

    picked_lines = list()
    for name in names:
        if name in def_line_by_name:
            def_line = def_line_by_name[name]

            picked_lines.append(def_line)

    return picked_lines


def _py_pick_import_lines(names, module_py):
    """Pick 'import' lines from 'module_py' that define words of 'py'"""

    # Pick out defined Import Lines,
    # but go wrong over From Imports, Conditional Imports, etc

    import_line_by_name = dict()
    for line in module_py.splitlines():
        words = line.split()
        if words and (words[0] == "import"):
            imported_name = words[-1]

            assert imported_name not in import_line_by_name, imported_name
            import_line_by_name[imported_name] = line

    # Pick out Defined Import Lines that got a Mention

    picked_lines = list()
    for name in names:
        if name in import_line_by_name:
            import_line = import_line_by_name[name]

            picked_lines.append(import_line)

    return picked_lines


def py_dedent(py, ifline, as_truthy):
    """Find the bodies of code that these 'ifline's guard, and keep or drop them"""

    inlines = py.splitlines()

    outlines = list()
    skip_index = 0
    for (index, inline) in enumerate(inlines):
        if index < skip_index:

            continue

        if inline.strip() != ifline:

            outlines.append(inline)

        else:

            (if_dent, _) = str_splitdent(inline)

            skip_index = index  # TODO: work each 'inline' just once, more elegantly
            skip_index += 1

            # Copy Lines of the Body till next Outdent,
            # but go wrong over Comments, Multi-Line Strings, etc

            for (sub_index, inline) in enumerate(inlines[(index + 1) :]):
                (dent, tail) = str_splitdent(inline)

                if len(dent) <= len(if_dent):
                    if inline:

                        break

                outline = inline
                if inline:

                    skip_index = index + 1 + sub_index + 1

                    dent = "    "
                    assert inline.startswith(dent + if_dent), repr(inline)
                    outline = inline[len(dent) :]

                if as_truthy:
                    outlines.append(outline)

                continue

            while not outlines[-1]:  # TODO: more clueful tie to blank lines from code
                outlines = outlines[:-1]

    chars = "\n".join(outlines).strip()

    return chars


#
# Every Bash command should know how to speak itsels as Python
#


def exec_shell_to_py(name, argv):
    """Convert one Shell Line to Python and run it"""

    module = sys.modules[name]
    py = module_shell_to_py(module, argv=argv)

    exec(py, globals())


def module_shell_to_py(module, argv):
    """Convert one Shell Line to Python, else Print the Help for it, else Exit Loudly"""

    file = os.path.basename(module.__file__)
    doc = module.__doc__
    func = module.shell_to_py

    py = func(argv)

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


#
# Run with a layer of general-purpose Python idioms
#


# deffed in many files  # missing from docs.python.org
class BrokenPipeErrorSink(contextlib.ContextDecorator):
    """Cut unhandled BrokenPipeError down to sys.exit(1)

    Test with large Stdout cut sharply, such as:  find.py ~ |head

    Cut more narrowly than:  signal.signal(signal.SIGPIPE, handler=signal.SIG_DFL)
    As per https://docs.python.org/3/library/signal.html#note-on-sigpipe
    """

    def __enter__(self, returncode=1):
        self.returncode = returncode
        return self

    def __exit__(self, *exc_info):
        (exc_type, exc, exc_traceback) = exc_info  # may be (None, None, None)
        if isinstance(exc, BrokenPipeError):  # catch one
            null_fileno = os.open(os.devnull, flags=os.O_WRONLY)
            os.dup2(null_fileno, sys.stdout.fileno())  # avoid the next one

            sys.exit(self.returncode)


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
        if stripped.startswith("#") and not stripped.startswith("# "):

            cpp_source = "#" + stripped[len("#") :].partition("#")[0]
            cpp_words = cpp_source.split()
            if cpp_words:
                cpp_verb = cpp_words[0]

                if cpp_verb == "#if":
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
def unified_diff_chars(a, b):
    """Return the chars of a 'diff -u' of two piles of source chars"""

    chars = "\n".join(difflib.unified_diff(a=a.splitlines(), b=b.splitlines()))

    return chars


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


# deffed in many files  # missing from docs.python.org till Oct/2019 Python 3.8
def shlex_quote(arg):
    """Mark up with quote marks and backslashes , but only as needed"""

    # trust the library, if available

    if hasattr(shlex, "quote"):
        quoted = shlex.quote(arg)
        return quoted

    # emulate the library roughly, because often good enough

    mostly_harmless = set(
        "%+,-./"
        + string.digits
        + ":@"
        + string.ascii_uppercase
        + "_"
        + string.ascii_lowercase
    )

    likely_harmful = set(arg) - set(mostly_harmless)
    if likely_harmful:
        quoted = repr(arg)  # as if the Py rules agree with Sh rules
        return quoted

    return arg


# deffed in many files  # missing from docs.python.org
def split_paragraphs(lines, keepends=False):
    """Split the lines into paragraphs"""

    paras = list()

    para = list()
    for line in lines:
        if line.strip():
            para.append(line)
        else:
            if keepends:
                para.append(line)
            if para or keepends:
                paras.append(para)
            para = list()
    if para:
        paras.append(para)

    return paras


# deffed in many files  # missing from docs.python.org
def str_splitdent(line):
    """Split apart the indentation of a line, from the remainder of the line"""

    lstripped = line.lstrip()
    len_dent = len(line) - len(lstripped)

    tail = lstripped
    if not lstripped:  # see no chars, not all chars, as the indentation of a blank line
        tail = line
        len_dent = 0

    dent = len_dent * " "

    return (dent, tail)


# copied by: git clone https://github.com/pelavarre/shell2py.git
