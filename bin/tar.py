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
  takes '-k' as meaning don't replace files created before now - like Linux, unlike Mac
  traces '-tv' dirs and files like Linux "u/g s y-m-D", not like Mac "u g s m d"
  traces '-x' dirs and files in Linux "f" format, not Mac "x f" format
  exits 1 if any pattern matches no names - like Mac, vs Linux exiting 2 and more often

Bash script to compress a top dir as Tgz for test:
  rm -fr dir/ dir.tgz
  mkdir -p dir/a/b/c dir/p/q/r
  echo hello >dir/a/b/d
  echo goodbye > dir/a/b/e
  tar czf dir.tgz dir/

examples:
  tar tvf dir.tgz  # show what's inside
  tar xvkf dir.tgz  # copy out what's inside
  tar tvf dir.tgz dir/a  # show just some of what's inside
  tar.py tvf dir.tgz dir dir/a// dir  # accept redundancy in every order, like Mac
"""

# TODO: solve FILE "-" means Stdin

import datetime as dt
import fnmatch
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

    commons.append(", args):")
    specials.append("):")

    commons.append("tar xvkf" if args.x else "tar tvf")
    specials.append(shline)

    if args.t and not args.v:
        commons.append(
            "            # Trace the walk\n\n",
        )
        specials.append("")
    if args.x and not args.k:
        commons.append(
            "                # Skip File's created before now\n\n",
        )
        specials.append("")
    if args.x and not args.v:
        commons.append("# Trace the walk and make the Dirs")
        specials.append("# Make the Dirs")
    if args.O:
        commons.append(
            "                # Write the bytes as a separate File\n\n",
        )
        specials.append("")
    if not args.O:
        commons.append(
            "                # Write the bytes to Stdout\n\n",
        )
        specials.append("")
    if not args.patterns:
        commons.append(
            "            # Skip the Dir or File if not at or below Pattern\n\n",
        )
        specials.append("")

    # Read this sourcefile

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:
        module_py = incoming.read()

    # Write the first sourceline

    rep_file_path = _scraps_.as_py_value(args.f)
    main_func_name = "tar_extract" if args.x else "tar_list"
    py1 = "{}({})".format(main_func_name, rep_file_path)

    # Add its Import's and Func's, delete its Dead Code

    py2 = tar_edit_py(
        py=py1, args=args, module_py=module_py, commons=commons, specials=specials
    )

    return py2


def tar_edit_py(py, args, module_py, commons, specials):

    py0 = py

    count = 0
    while True:
        count += 1

        assert count <= 4, count

        py1 = py0

        py1 = _scraps_.py_pick_lines(py=py1, module_py=module_py)

        for argname in "v k O patterns".split():

            got_yes = vars(args)[argname]
            if_yes_line = "if args.{}:".format(argname)
            py1 = _scraps_.py_dedent(py1, ifline=if_yes_line, as_truthy=got_yes)

            got_no = not got_yes
            if_no_line = "if not args.{}:".format(argname)
            py1 = _scraps_.py_dedent(py1, ifline=if_no_line, as_truthy=got_no)

        for (common, special) in zip(commons, specials):
            py1 = py1.replace(common, special)

        if py0 == py1:

            assert count >= 3, count

            return py0

        py0 = py1


def tar_list(filepath, args):
    """List tarred files, a la 'tar tvf'"""

    if args.patterns:
        fnmatches = tar_fnmatches_enter(patterns=args.patterns)

    # Visit each Dir or File

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Skip the Dir or File if not at or below Pattern

            if args.patterns:
                if not tar_fnmatches_find_name(fnmatches):
                    continue

            # Skip the Dir or File if not at or below Top

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

    if args.patterns:
        if tar_fnmatches_exit(fnmatches):
            sys.exit(1)


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
        exists = list()

    if args.patterns:
        fnmatches = tar_fnmatches_enter(patterns=args.patterns)

    # Walk to each file or dir found inside

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Skip the Dir or File if not at or below Pattern

            if args.patterns:
                if not tar_fnmatches_find_name(fnmatches, name):
                    continue

            # Skip the Dir or File if not at or below Top

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
                        exists.append(name)

                        continue

                # Fetch the bytes of the Member

                member_bytes = incoming.read()
                member_size = len(member_bytes)
                assert member_size == member.size, (member_size, member.size)

                # Write the bytes as a separate File

                if not args.O:
                    with open(outpath, "wb") as outgoing:
                        outgoing.write(member_bytes)

                # Write the bytes to Stdout

                if args.O:
                    sys.stdout.write(member_bytes)

                # : also extract the Perms and Stamp, but not so much the Owns

    if args.k:
        if exists:
            stderr_print("tar: Exiting with failure status due to previous errors")
            sys.exit(2)

    if args.patterns:
        if tar_fnmatches_exit(fnmatches):
            sys.exit(1)


def tar_fnmatches_enter(fnmatches, patterns):
    """Starting counting fnmatch'es"""

    fnmatches = dict()
    for pat in patterns:
        fnmatches[pat] = 0

    return fnmatches


def tar_fnmatches_find_name(fnmatches, name):
    """Count fnmatch'es found, if any"""

    count = 0
    for pat in fnmatches.keys():
        if fnmatch.fnmatchcase(name, pat=pat):
            fnmatches[pat] += 1

            count += 1

    return count


def tar_fnmatches_exit(fnmatches):
    """Count each Pattern not found, and trace it too"""

    count = 0
    for (pat, hits) in fnmatches.items():
        if not hits:
            stderr_print("tar: {}: Not found in archive".format(pat))
            count += 1

            # Mac and Linux rstrip 1 or all of the trailing '/' slashes in a Pattern

    return count


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
