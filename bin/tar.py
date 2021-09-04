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

import re
import sys

import _scraps_


def main(argv=None):

    as_argv = sys.argv if (argv is None) else argv

    _scraps_.to_py_main(name=__name__, argv=as_argv)


def bash2py(argv):

    args = parse_args(argv)

    # Shrug off some obvious contradictions

    if not args.f:
        return

    if args.t and not args.x:
        pass
    elif args.x and not args.t:
        pass
    else:
        return

    if args.k:
        if not args.x:
            return

    # TODO: comment options into source

    flags = "".join(_ for _ in "txvkf" if vars(args)[_])

    extract_doc_chars = "extract tarred files, a la 'tar {}'".format(flags)
    list_doc_chars = "list tarred files, a la 'tar {}'".format(flags)
    doc_chars = extract_doc_chars if args.x else list_doc_chars

    func = "tar_extract" if args.x else "tar_list"

    py = r'''

        import datetime as dt
        import os
        import sys
        import tarfile

        def $FUNC(filepath):
            """$DOC_CHARS"""

            # Walk to each file or dir found inside

#if TAR_ADD_NOT_REPLACE
            exists = 0
#endif
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

#if TAR_EXTRACT
#else
                    # Trace the walk

                    print(tar_member_details(member))
#endif
#if TAR_EXTRACT
                    # Trace the walk and make the dirs

                    if member.isdir():
                        print(name + os.sep)
                        if not os.path.isdir(outpath):
                            os.makedirs(outpath)
                        continue

                    print(name)
  #if TAR_ADD_NOT_REPLACE

                    # Skip existing files

                    with untarring.extractfile(name) as incoming:
                        if os.path.exists(name):
                            stderr_print(
                                "tar.py: {}: Cannot open: File exists".format(name)
                            )
                            exists += 1
                            continue

                        # Save the bytes of the member as a file
  #else
                    # Save the bytes of the member as a file

                    with untarring.extractfile(name) as incoming:
  #endif

                        member_bytes = incoming.read()
                        with open(outpath, "wb") as outgoing:
                            outgoing.write(member_bytes)

  #if TAR_ADD_NOT_REPLACE
            if exists:
                stderr_print(
                    "tar: Exiting with failure status due to previous errors"
                )
                sys.exit(2)

  #endif
#endif

        def tar_member_details(member):
            """Return such as '-rw-r--r-- jqdoe/staff 8 2021-09-03 20:41 dir/a/b/e'"""

            d_perm = 'd' if member.isdir() else '-'
            bits = ((9 * "0") + bin(member.mode)[len("0b"):])[-9:]
            perms = d_perm + "".join("rwxrwxrwx"[_] for _ in range(len(bits)))

            owns = member.uname + os.sep + member.gname

            size = member.size

            when = dt.datetime.fromtimestamp(member.mtime)
            stamp = when.strftime("%Y-%m-%d %H:%M")

            name = (member.name + os.sep) if member.isdir() else member.name

            line = "{} {} {} {} {}".format(perms, owns, size, stamp, name)

            return line


        # deffed in many files  # missing from docs.python.org
        def stderr_print(*args, **kwargs):
            """Like Print, but flush don't write Stdout and do write and flush Stderr"""

            sys.stdout.flush()
            print(*args, **kwargs, file=sys.stderr)
            sys.stderr.flush()

            # else caller has to "{}\n".format(...) and flush


        $FUNC($FILE_PATH)

        '''

    py = _scraps_.c_pre_process(
        py,
        cpp_vars=dict(tar_add_not_replace=args.k, tar_extract=args.x),
    )

    py = py.replace("$DOC_CHARS", doc_chars)
    py = py.replace("$FUNC", func)
    py = py.replace("$FILE_PATH", _scraps_.as_py_value(args.f))

    return py


def parse_args(argv):

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
