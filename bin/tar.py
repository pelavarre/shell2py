#!/usr/bin/env python3

"""
usage: tar.py [-h] [-t] [-x] [-c] [-v] [-k] [-f FILE] [-O] [--dict]
              [PATTERN ...]

walk the files and dirs found inside a top dir compressed as Tgz

positional arguments:
  PATTERN     list or extract only the files or dirs at or below pattern

optional arguments:
  -h, --help  show this help message and exit
  -t          dry run: list each dir or file at Stdout, but do Not extract them
  -x          write out a copy of each file, back to where it came from
  -c          compress: take the so-called PATTERN's as FILE's and DIR's to read
  -v          say more: add details to '-t', or list each dir or file when extracted
  -k          stop extract from replacing files created before now
  -f FILE     name the file to uncompress
  -O          extract to Stdout, not to where the files came from
  --dict      extract to a Python Dict, not to where the files came from

quirks:
  lets you say classic 'tvf' to mean '-tvf', classic 'xvkf' to mean '-xvkf', etc
  takes '-k' as meaning don't replace files created before now (like Linux, unlike Mac)
  traces '-tv' dirs and files like Linux "u/g s y-m-D", not like Mac "u g s m d"
  traces '-x' dirs and files in Linux "f" format, not Mac "x f" format
  exits 1 if file is empty - like Linux exits 2, unlike Mac silently exits zero
  exits 1 if any pattern matches no names (like Mac, vs Linux exits 2 and at overlaps)
  exits 2 if pattern is empty string (like Mac, vs Linux silently exits zero)

Bash script to compress a top dir as Tgz for test:
  rm -fr dir/ dir.tgz
  mkdir -p dir/a/b/c dir/p/q/r
  echo hello >dir/a/b/d
  echo goodbye > dir/a/b/e
  tar czf dir.tgz dir/

examples:
  tar tvf dir.tgz  # show what's inside
  tar xvkf dir.tgz  # copy out what's inside
  tar tf dir.tgz dir/a  # show just some of what's inside
  tar.py tf dir.tgz dir dir/a/b/d/// dir  # match repeatedly, & dirs w files, like Mac
  tar xf dir.tgz -O 'dir/a/*/?'  # accept quoted '?' and '*' patterns, like Linux & Mac
  python3 -i bin/tar.py xf dir.tgz --dict 'dir/a/*/?'  # extract to a Python Dict
"""

# TODO: solve FILE "-" means Stdin

import datetime as dt
import fnmatch
import os
import re
import sys
import tarfile

import _scraps_


BYTES_BY_NAME = dict()  # collect bytes of Tgz members, for the '-x --dict' mode


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_tar_py)

    if hasattr(main, "args"):
        if main.args.dict:
            BYTES_BY_NAME.update(_scraps_.BYTES_BY_NAME)


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
        help="dry run: list each dir or file at Stdout, but do Not extract them",
    )

    parser.add_argument(
        "-x",
        action="count",
        default=0,
        help="write out a copy of each file, back to where it came from",
    )

    parser.add_argument(
        "-c",
        action="count",
        default=0,
        help="compress: take the so-called PATTERN's as FILE's and DIR's to read",
    )

    parser.add_argument(
        "-v",
        action="count",
        default=0,
        help="say more: add details to '-t', or list each dir or file when extracted",
    )

    parser.add_argument(
        "-k",
        action="count",
        default=0,
        help="stop extract from replacing files created before now",
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
        help="extract to Stdout, not to where the files came from",
    )

    parser.add_argument(
        "--dict",
        action="count",
        default=0,
        help="extract to a Python Dict, not to where the files came from",
    )

    _scraps_.exit_unless_doc_eq(parser, file=__file__, doc=__doc__)

    args = parser.parse_args(as_argv[1:])

    return args


def argv__to_tar_py(argv):
    """Write the Python for a Tar ArgV, else print some Help and quit"""

    # Intercept '-h', '--h', '--he', ... '--help' as first arg,
    # before requiring all args declared

    _scraps_.parse_left_help_args(argv, doc=__doc__)

    # Intercept '-c' inside first arg, if first arg is not a '--...' arg

    if argv[1:]:
        argv1 = argv[1]
        if not argv1.startswith("--"):
            if "c" in argv1:

                altv = list(argv)
                altv[0] = "tar"

                py = _scraps_.argv__to_shline_py(altv)

                return py

    # Else fallback to parse the command line as per top-of-file Docstring

    args = parse_tar_args(argv)
    main.args = args

    module_py = _scraps_.module_name__readlines(__name__)

    # Reject obvious contradictions

    exit_unless_simple_tar(args)

    # Shrug off the trailing 'os.sep's of each pattern, if they exist

    patterns = list()
    for pat in args.patterns:
        assert pat  # because guarded by 'exit_unless_simple_tar'
        rstripped = pat.rstrip(os.sep)
        rstripped = rstripped if rstripped else os.sep
        patterns.append(rstripped)  # may be dupe

    # Form a stylish copy of the Shell Tar Command Line

    shline = shlex_join_tar(args, patterns=patterns)

    # Collect

    (commons, specials) = defer_calls_to_replace(shline, args=args, patterns=patterns)

    # Write the Top Level Tar Python

    main_func_name = "tar_extract" if args.x else "tar_list"

    py1 = "{}($FILEPATH)".format(main_func_name)
    if patterns:
        py1 = "{}($FILEPATH, patterns=$PATTERNS)".format(main_func_name)

    # Add its Import's and Func's, delete its Dead Code

    py2 = tar_edit_py(
        py=py1, args=args, module_py=module_py, commons=commons, specials=specials
    )

    # Inject strings, last of all

    rep_file_path = _scraps_.as_py_value(args.f)
    rep_patterns = _scraps_.as_py_value(patterns)

    py3 = py2
    py3 = py3.replace("$FILEPATH", rep_file_path)
    py3 = py3.replace("$PATTERNS", rep_patterns)

    return py3


def tar_edit_py(py, args, module_py, commons, specials):

    py1 = py

    count = 0
    while True:
        count += 1
        assert count <= 4, count

        py0 = py1

        # Look for one more expansion

        py1 = _scraps_.py_pick_lines(py=py1, module_py=module_py)

        argnames = "v k O dict".split()
        py1 = _scraps_.py_dedent_args(py=py1, args=args, argnames=argnames)
        py1 = _scraps_.py_dedent_bool(py=py1, name="patterns", truthy=args.patterns)

        for (common, special) in zip(commons, specials):
            py1 = py1.replace(common, special)

        # Succeed when no more expansion found

        if py0 == py1:

            assert count >= 2, count

            py1 = _scraps_.py_add_imports(py=py0, module_py=module_py)
            assert py1 != py0, py0

            return py1


def exit_unless_simple_tar(args):  # noqa Flake8 C901 too complex (11)
    """Reject obvious Tar option contradictions, as if untranslatable"""

    for pat in args.patterns:
        if not pat:
            stderr_print("tar: Error inclusion pattern: pattern is empty")
            sys.exit(2)

    if args.t and args.x:
        stderr_print("tar.py: error: arguments -t -x: choose one, not both")
        sys.exit(2)
    if (not args.t) and (not args.x):
        stderr_print("tar.py: error: arguments -t -x: choose one, not neither")
        sys.exit(2)

    if not args.x:
        for argname in "dict k O".split():
            if vars(args)[argname]:
                stderr_print(
                    "tar.py: error: argument {}: add -x if you mean it".format(argname)
                )
                sys.exit(2)

    if (args.dict or args.k or args.O) and not args.x:
        stderr_print("tar.py: error: argument -f FILE required")
        sys.exit(2)

    if args.dict and args.O:
        stderr_print("tar.py: error: arguments --dict -O: choose one, not both")
        sys.exit(2)

    if not args.f:
        stderr_print("tar.py: error: argument -f FILE required")
        sys.exit(2)


def shlex_join_tar(args, patterns):
    """Form a stylish copy of the Shell Tar Command Line"""

    flags = "".join(_ for _ in "txvkf" if vars(args)[_])

    shline = "tar"
    if not (args.dict or args.O or patterns):
        shline += " " + flags
    else:
        shline += " -" + flags
        if args.O:
            shline += " -O" + flags
        if args.dict:
            shline += " --dict" + flags
        if patterns:
            for pattern in patterns:
                shline += " " + _scraps_.shlex_quote(pattern)

    return shline


def defer_calls_to_replace(shline, args, patterns):  # noqa Flake8 C901 too complex (13)
    """Calculate the edits that may be required, without immediately applying them"""

    # FIXME: Less explicit deletes of comments before the deletes of code

    commons = list()
    specials = list()

    if args.dict:
        commons.append("import tarfile\n\n\n")
        specials.append("import tarfile\n\n\nBYTES_BY_NAME = dict()\n\n\n")

    commons.append(", args")
    specials.append("")

    if not patterns:
        commons.append(", patterns")
        specials.append("")

    commons.append("tar xvkf" if args.x else "tar tvf")
    specials.append(shline)

    if args.x and not args.k:
        commons.append(
            "                # Skip File's created before now\n\n",
        )
        specials.append("")

    if args.x and not args.v:
        commons.append("# Trace the walk and make the Dirs")
        if args.dict or args.O:
            specials.append("# Skip the Dirs")
        else:
            specials.append("# Make the Dirs")
    if args.x and args.v:
        if args.dict or args.O:
            commons.append("# Trace the walk and make the Dirs")
            specials.append("# Trace the walk")

    if args.dict or args.O:
        commons.append(
            "                # Write the bytes as a separate File\n\n",
        )
        specials.append("")
    if not args.O:
        commons.append(
            "                # Write the bytes to Stdout\n\n",
        )
        specials.append("")
    if not args.dict:
        commons.append(
            "                # Write the bytes to Dict\n\n",
        )
        specials.append("")

    if not patterns:
        commons.append(
            "            # Skip the Dir or File if not at or below Pattern\n\n",
        )
        specials.append("")

    commons.append("  # noqa Flake8 C901 too complex (22)")
    specials.append("")

    commons.append("  # noqa Flake8 C901 too complex (32)")
    specials.append("")

    return (commons, specials)


def tar_list(filepath, patterns, args):  # noqa Flake8 C901 too complex (32)
    """List tarred files, a la 'tar tvf'"""

    if patterns:
        fnmatches = tar_fnmatches_open(patterns)

    # Visit each Dir or File

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Skip the Dir or File if not at or below Pattern

            if patterns:
                if not tar_fnmatches_find_name(fnmatches, name=name):
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

    if patterns:
        misses = tar_fnmatches_close(fnmatches)
        if misses:
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


def tar_extract(filepath, patterns, args):  # noqa Flake8 C901 too complex (22)
    """Extract tarred files, a la 'tar xvkf'"""

    if args.k:
        exists = list()

    if patterns:
        fnmatches = tar_fnmatches_open(patterns)

    # Walk to each file or dir found inside

    top = os.path.realpath(os.getcwd())
    with tarfile.open(filepath) as untarring:  # instance of 'tarfile.TarFile'
        names = untarring.getnames()

        for name in names:
            member = untarring.getmember(name)

            # Skip the Dir or File if not at or below Pattern

            if patterns:
                if not tar_fnmatches_find_name(fnmatches, name=name):
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

                if not args.O:
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
                    with open("/dev/stdout", "wb") as outgoing:
                        outgoing.write(member_bytes)

                # Write the bytes to Dict

                if args.dict:
                    BYTES_BY_NAME[name] = member_bytes

                # : also extract the Perms and Stamp, but not so much the Owns

    if args.k:
        if exists:
            stderr_print("tar: Exiting with failure status due to previous errors")
            sys.exit(2)

    if patterns:
        if tar_fnmatches_close(fnmatches):
            sys.exit(1)

    if args.dict:
        stderr_print(
            "tar: Exiting with {} keys in BYTES_BY_NAME".format(
                len(BYTES_BY_NAME.keys())
            )
        )


def tar_fnmatches_open(patterns):
    """Starting counting fnmatch'es"""

    fnmatches = dict()
    for pat in patterns:
        fnmatches[pat] = 0

    return fnmatches


def tar_fnmatches_find_name(fnmatches, name):
    """Count fnmatch'es found, if any"""

    count = 0
    for pat in fnmatches.keys():

        at_or_below_pat = False
        name_or_above = name
        while name_or_above:
            if fnmatch.fnmatchcase(name_or_above, pat=pat):
                at_or_below_pat = True
                break
            name_or_above = os.path.dirname(name_or_above)

        if at_or_below_pat:
            fnmatches[pat] += 1

            count += 1

    return count


def tar_fnmatches_close(fnmatches):
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
