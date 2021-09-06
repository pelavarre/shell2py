#!/usr/bin/env python3

"""
usage: tar.py [-h] [-t] [-x] [-v] [-k] [-f FILE]

walk the files and dirs found inside a top dir compressed as Tgz

optional arguments:
  -h, --help  show this help message and exit
  -t          list every file, without writing any files
  -x          write out a copy of every file
  -v          trace each file or dir name found inside to stdout
  -k          decline to replace pre-existing output files
  -f FILE     name the file to uncompress

quirks:
  lets you say 'tvf' to mean '-tvf', 'xvkf' to mean '-xvkf', etc
  takes '-k' as meaning don't replace existing files, like linux, unlike mac
  traces files and dirs in linux "u/g" "s" "y-m-D" format, not mac "u" "g" " s" "m d"
  traces extracts in linux "f" format, not mac "x f" format
  lists and extracts the compressed files and dirs in python order, not linux order

bash script to compress a top dir as Tgz for test:
  rm -fr dir/ dir.tgz
  mkdir -p dir/a/b/c dir/p/q/r
  echo hello >dir/a/b/d
  echo goodbye > dir/a/b/e
  tar czf dir.tgz dir/

examples:
  tar tvf dir.tgz  # say what's inside
  tar xvkf dir.tgz  # copy out what's inside
"""

# TODO: solve -O --wildcards, solve FILE is "-" to mean Stdin

import datetime as dt
import os
import re
import sys
import tarfile

import _scraps_


def main(argv=None):

    as_argv = sys.argv if (argv is None) else argv

    _scraps_.to_py_main(name=__name__, argv=as_argv)


def bash2py(argv):

    args = parse_tar_args(argv)

    module = sys.modules[__name__]
    with open(module.__file__) as incoming:  # read this sourcefile
        module_py = incoming.read()

    # Shrug off some obvious contradictions: accept only r'(t|xk|x)v?f'

    if args.t and args.x:
        return
    if (not args.t) and (not args.x):
        return

    if args.k and not args.x:
        return

    if not args.f:
        return

    # Write the first sourceline

    rep_file_path = _scraps_.as_py_value(args.f)
    main_func_name = "tar_extract" if args.x else "tar_list"
    py1 = "{}({})".format(main_func_name, rep_file_path)

    # Expand it once, and refine its DocString's

    py2 = _scraps_.py_pick_lines(py=py1, module_py=module_py)
    flags = "".join(_ for _ in "txvkf" if vars(args)[_])
    py2 = py2.replace(
        '''a la 'tar tvf'"""''',
        '''a la 'tar {}'"""'''.format(flags),
    )

    # Expand it to two levels, and drop/keep the source guarded by 'tar -v'

    py3 = py2
    py3 = py3.replace(", args):", "):")
    py3 = _scraps_.py_dedent(py3, ifline="if args.k:", as_truthy=args.k)
    py3 = _scraps_.py_dedent(py3, ifline="if args.v:", as_truthy=args.v)

    # Expand it to three levels

    py4 = py3
    py4 = _scraps_.py_pick_lines(py=py4, module_py=module_py)
    py4 = py4.replace(", args):", "):")
    py4 = _scraps_.py_dedent(py4, ifline="if args.k:", as_truthy=args.k)
    py4 = _scraps_.py_dedent(py4, ifline="if args.v:", as_truthy=args.v)
    assert py4 != py3, stderr_print(_scraps_.unified_diff_chars(a=py3, b=py4))

    # Expand it once more, if needed to surface the imports of the bottom level

    py5 = py4
    py5 = _scraps_.py_pick_lines(py=py5, module_py=module_py)
    py5 = py5.replace(", args):", "):")
    py5 = _scraps_.py_dedent(py5, ifline="if args.k:", as_truthy=args.k)
    py5 = _scraps_.py_dedent(py5, ifline="if args.v:", as_truthy=args.v)

    # Expand it one extra time, to demo no more need to expand it

    py6 = py5
    py6 = _scraps_.py_pick_lines(py=py6, module_py=module_py)
    py6 = py6.replace(", args):", "):")
    py6 = _scraps_.py_dedent(py6, ifline="if args.k:", as_truthy=args.k)
    py6 = _scraps_.py_dedent(py6, ifline="if args.v:", as_truthy=args.v)
    assert py6 == py5, stderr_print(_scraps_.unified_diff_chars(a=py5, b=py6))

    # Succeed

    return py6


def tar_list(filepath, args):
    """List tarred files, a la 'tar tvf'"""

    # Walk to each file or dir found inside

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Decline to extract above Top

            outpath = os.path.realpath(name)
            outdir = os.path.dirname(outpath)

            if top != outdir:
                assert outdir.startswith(top + os.sep), (outdir, top)

            # Trace the walk

            if args.v:
                print(tar_member_details(member))


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

            # Decline to extract above Top

            outpath = os.path.realpath(name)
            outdir = os.path.dirname(outpath)

            if top != outdir:
                assert outdir.startswith(top + os.sep), (outdir, top)

            # Trace the walk and make the dirs

            if member.isdir():
                if args.v:
                    print(name + os.sep)

                if not os.path.isdir(outpath):
                    os.makedirs(outpath)

                continue

            if args.v:
                print(name)

            # Skip existing files

            with untarring.extractfile(name) as incoming:

                if args.k:
                    if os.path.exists(name):
                        stderr_print(
                            "tar.py: {}: Cannot open: File exists".format(name)
                        )
                        exists += 1

                        continue

                # Save the bytes of the member as a file

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


# TODO: shuffle up 'def tar_member_details' to below `def tar_list'
def tar_member_details(member):
    """Return such as '-rw-r--r-- jqdoe/staff 8 2021-09-03 20:41 dir/a/b/e'"""

    d_perm = "d" if member.isdir() else "-"
    bits = ((9 * "0") + bin(member.mode)[len("0b") :])[-9:]
    perms = d_perm + "".join("rwxrwxrwx"[_] for _ in range(len(bits)))

    owns = member.uname + os.sep + member.gname
    # TODO: default to ".../..." anonymity, and who extracts to match sender anyhow?

    str_size = str(member.size)
    # TODO: str_size = "." if member.isdir() else str(member.size)

    when = dt.datetime.fromtimestamp(member.mtime)
    stamp = when.strftime("%Y-%m-%d %H:%M")

    name = (member.name + os.sep) if member.isdir() else member.name

    line = "{} {} {} {} {}".format(perms, owns, str_size, stamp, name)

    return line


# deffed in many files  # missing from docs.python.org
def stderr_print(*args, **kwargs):
    """Like Print, but flush don't write Stdout and do write and flush Stderr"""

    sys.stdout.flush()
    print(*args, **kwargs, file=sys.stderr)
    sys.stderr.flush()

    # else caller has to "{}\n".format(...) and flush


# TODO: shuffle 'def parse_tar_args' to below 'def main' above 'def bash2py'
def parse_tar_args(argv):

    as_argv = list(argv)
    if as_argv[1:]:
        flags = as_argv[1]
        if re.match(r"^[txvkf]+$", string=flags):
            as_argv[1] = "-" + flags

    parser = _scraps_.compile_argdoc(epi="quirks:", doc=__doc__)

    parser.add_argument(
        "-t",
        action="count",
        default=0,
        help="list every file, without writing any files",
    )

    parser.add_argument(
        "-x",
        action="count",
        default=0,
        help="write out a copy of every file",
    )

    parser.add_argument(
        "-v",
        action="count",
        default=0,
        help="trace each file or dir name found inside to stdout",
    )

    parser.add_argument(
        "-k",
        action="count",
        default=0,
        help="decline to replace pre-existing output files",
    )

    parser.add_argument(
        "-f",
        metavar="FILE",
        default=0,
        help="name the file to uncompress",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(as_argv[1:])

    return args


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git