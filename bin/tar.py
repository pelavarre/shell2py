#!/usr/bin/env python3

"""
usage: tar.py [-h] [-t] [-x] [-v] [-k] [-f FILE] [-O] [PATTERN [PATTERN ...]]

walk the files and dirs found inside a top dir compressed as Tgz

positional arguments:
  PATTERN     list or extract only the files or dirs at or below pattern

optional arguments:
  -h, --help  show this help message and exit
  -t          dry run:  list each dir or file at Stdout, but do Not extract them
  -x          write out a copy of each file, back to where it came from
  -v          say more:  add details to '-t', or list each dir or file when extracted
  -k          decline to replace files created before now
  -f FILE     name the file to uncompress
  -O          write out a copy of each file, but to Stdout, not to where it came from

quirks:
  lets you say classic 'tvf' to mean '-tvf', classic 'xvkf' to mean '-xvkf', etc
  takes '-k' as meaning don't replace files created before now, like Linux, unlike Mac
  traces '-tv' dirs and files like Linux "u/g s y-m-D", not like Mac "u g s m d"
  traces '-x' dirs and files in Linux "f" format, not Mac "x f" format

Bash script to compress a top dir as Tgz for test:
  rm -fr dir/ dir.tgz
  mkdir -p dir/a/b/c dir/p/q/r
  echo hello >dir/a/b/d
  echo goodbye > dir/a/b/e
  tar czf dir.tgz dir/

examples:
  tar tvf dir.tgz  # say what's inside
  tar xvkf dir.tgz  # copy out what's inside
"""

# TODO: solve FILE "-" means Stdin

import datetime as dt
import os
import re
import sys
import tarfile

import _scraps_


def main(argv=None):

    as_argv = sys.argv if (argv is None) else argv

    _scraps_.exec_shell_to_py(name=__name__, argv=as_argv)


def parse_tar_args(argv):

    as_argv = list(argv)
    if as_argv[1:]:
        flags = as_argv[1]
        if re.match(r"^[txvkf]+$", string=flags):
            as_argv[1] = "-" + flags

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

    parser.add_argument(
        "patterns",
        metavar="PATTERN",
        nargs="*",
        help="list or extract only the files or dirs at or below pattern",
    )

    parser.add_argument(
        "-t",
        action="count",
        default=0,
        help="dry run:  list each dir or file at Stdout, but do Not extract them",
    )

    parser.add_argument(
        "-x",
        action="count",
        default=0,
        help="write out a copy of each file, back to where it came from",
    )

    parser.add_argument(
        "-v",
        action="count",
        default=0,
        help="say more:  add details to '-t', or list each dir or file when extracted",
    )

    parser.add_argument(
        "-k",
        action="count",
        default=0,
        help="decline to replace files created before now",
    )

    parser.add_argument(
        "-f",
        metavar="FILE",
        default=0,
        help="name the file to uncompress",
    )

    parser.add_argument(
        "-O",
        action="count",
        default=0,
        help="write out a copy of each file, but to Stdout, not to where it came from",
    )

    got_usage = parser.format_usage()
    assert (
        got_usage
        == "usage: tar.py [-h] [-t] [-x] [-v] [-k] [-f FILE] [-O] [PATTERN ...]\n"
    ), got_usage
    parser.usage = (
        "tar.py [-h] [-t] [-x] [-v] [-k] [-f FILE] [-O] [PATTERN [PATTERN ...]]"
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(as_argv[1:])

    return args


def shell_to_py(argv):

    args = parse_tar_args(argv)

    patterns = args.patterns

    # Reject obvious contradictions

    if args.t and args.x:
        return
    if (not args.t) and (not args.x):
        return

    if (args.k or args.O) and not args.x:
        return

    if not args.f:
        return

    # Style the Shell line of the Python

    flags = "".join(_ for _ in "txvkf" if vars(args)[_])

    shline = "tar"
    if not (args.O or patterns):
        shline += " " + flags
    else:
        shline += " -" + flags
        if args.O:
            shline += " -O" + flags
        if patterns:
            for pattern in patterns:
                shline += " " + _scraps_.shlex_quote(pattern)

    # Stub out what doesn't work yet

    if patterns or args.O:
        raise NotImplementedError()

    # Calculate edits required
    # TODO: Less explicit deletes of comments before the deletes of code

    commons = list()
    specials = list()

    commons.append("tar xvkf" if args.x else "tar tvf")
    specials.append(shline)
    if args.t and not args.v:
        commons.append("            # Trace the walk\n\n")
        specials.append("")
    if args.x and not args.k:
        commons.append("                # Skip File's created before now\n\n")
        specials.append("")
    if args.x and not args.v:
        commons.append("# Trace the walk and make the Dirs")
        specials.append("# Make the Dirs")
    if args.O:
        commons.append("# Write the bytes of the Member as a separate File")
        specials.append("# Write the bytes of the Member as Stdout")

    def str_replace_common_special(py):

        edited = py
        for (common, special) in zip(commons, specials):
            edited = edited.replace(common, special)

        return edited

    # Read this sourcefile

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:
        module_py = incoming.read()

    # Write the first sourceline

    rep_file_path = _scraps_.as_py_value(args.f)
    main_func_name = "tar_extract" if args.x else "tar_list"
    py1 = "{}({})".format(main_func_name, rep_file_path)

    # Expand it once

    py2 = _scraps_.py_pick_lines(py=py1, module_py=module_py)

    # Expand it to two levels, and drop/keep the source guarded by 'tar -v'

    py3 = py2
    py3 = py3.replace(", args):", "):")
    py3 = _scraps_.py_dedent(py3, ifline="if args.k:", as_truthy=args.k)
    py3 = _scraps_.py_dedent(py3, ifline="if args.v:", as_truthy=args.v)
    py3 = _scraps_.py_dedent(py3, ifline="if not args.v:", as_truthy=(not args.v))

    # Expand it to three levels

    py4 = py3
    py4 = _scraps_.py_pick_lines(py=py4, module_py=module_py)
    py4 = py4.replace(", args):", "):")
    py4 = _scraps_.py_dedent(py4, ifline="if args.k:", as_truthy=args.k)
    py4 = _scraps_.py_dedent(py4, ifline="if args.v:", as_truthy=args.v)
    py4 = _scraps_.py_dedent(py4, ifline="if not args.v:", as_truthy=(not args.v))
    assert py4 != py3, stderr_print(_scraps_.unified_diff_chars(a=py3, b=py4))

    # Expand it once more, if needed to surface the imports of the bottom level
    # and refine its Docstrings

    py5 = py4
    py5 = _scraps_.py_pick_lines(py=py5, module_py=module_py)
    py5 = py5.replace(", args):", "):")
    py5 = _scraps_.py_dedent(py5, ifline="if args.k:", as_truthy=args.k)
    py5 = _scraps_.py_dedent(py5, ifline="if args.v:", as_truthy=args.v)
    py5 = _scraps_.py_dedent(py5, ifline="if not args.v:", as_truthy=(not args.v))
    py5 = str_replace_common_special(py5)

    # Form it one last time, to show no more need to expand it

    py6 = py5
    py6 = _scraps_.py_pick_lines(py=py6, module_py=module_py)
    py6 = py6.replace(", args):", "):")
    py6 = _scraps_.py_dedent(py6, ifline="if args.k:", as_truthy=args.k)
    py6 = _scraps_.py_dedent(py6, ifline="if args.v:", as_truthy=args.v)
    py6 = _scraps_.py_dedent(py6, ifline="if not args.v:", as_truthy=(not args.v))
    py6 = str_replace_common_special(py6)
    assert py6 == py5, stderr_print(_scraps_.unified_diff_chars(a=py5, b=py6))

    # Succeed

    return py6


def tar_list(filepath, args):
    """List tarred files, a la 'tar tvf'"""

    # Visit each Dir or File

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Decline to visit above Top

            outpath = os.path.realpath(name)
            outdir = os.path.dirname(outpath)

            if top != outdir:
                assert outdir.startswith(top + os.sep), (outdir, top)

            # Trace the walk

            if not args.v:
                if member.isdir():
                    print(name + os.sep)
                else:
                    print(name)

            if args.v:
                print(tar_member_details(member))


def tar_member_details(member):
    """Return such as '-rw-r--r-- jqdoe/staff 8 2021-09-03 20:41 dir/a/b/e'"""

    d_perm = "d" if member.isdir() else "-"
    bits = ((9 * "0") + bin(member.mode)[len("0b") :])[-9:]
    perms = d_perm + "".join("rwxrwxrwx"[_] for _ in range(len(bits)))

    member_uname = "..."  # ellipsis "..." is more anonymous than "member.uname"
    member_gname = "..."  # ellipsis "..." is more anonymous than "member.gname"
    owns = member_uname + os.sep + member_gname

    str_size = "." if member.isdir() else str(member.size)  # 0 at dirs is meaningless

    when = dt.datetime.fromtimestamp(member.mtime)
    stamp = when.strftime("%Y-%m-%d %H:%M")

    name = (member.name + os.sep) if member.isdir() else member.name

    line = "{} {} {} {} {}".format(perms, owns, str_size, stamp, name)

    return line


def tar_extract(filepath, args):
    """Extract tarred files, a la 'tar xvkf'"""

    if args.k:
        exists = 0

    # Walk to each file or dir found inside

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Decline to visit above Top

            outpath = os.path.realpath(name)
            outdir = os.path.dirname(outpath)

            if top != outdir:
                assert outdir.startswith(top + os.sep), (outdir, top)

            # Trace the walk and make the Dirs

            if member.isdir():
                if args.v:
                    stderr_print(name + os.sep)

                if not os.path.isdir(outpath):
                    os.makedirs(outpath)

                continue

            if args.v:
                stderr_print(name)

            # Visit each Dir or File

            with untarring.extractfile(name) as incoming:

                # Skip File's created before now

                if args.k:
                    if os.path.exists(name):
                        stderr_print(
                            "tar.py: {}: Cannot open: File exists".format(name)
                        )
                        exists += 1

                        continue

                # Write the bytes of the Member as a separate File

                member_bytes = incoming.read()
                member_size = len(member_bytes)
                assert member_size == member.size, (member_size, member.size)

                with open(outpath, "wb") as outgoing:
                    outgoing.write(member_bytes)

                # TODO: also extract the perms, stamp, and owns

    if args.k:
        if exists:
            stderr_print("tar: Exiting with failure status due to previous errors")
            sys.exit(2)


# deffed in many files  # missing from docs.python.org
def stderr_print(*args, **kwargs):
    """Like Print, but flush don't write Stdout and do write and flush Stderr"""

    sys.stdout.flush()
    print(*args, **kwargs, file=sys.stderr)
    sys.stderr.flush()

    # else caller has to "{}\n".format(...) and flush


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
