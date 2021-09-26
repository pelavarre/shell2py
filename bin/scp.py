#!/usr/bin/env python3

"""
usage: scp.py [--help] SOURCE TARGET

copy Files and Dirs between Hosts over Https, less openly than over Http without S

positional arguments:
  SOURCE  a local FILE or DIR, or a remote HOST: or HOST:FILE or HOST:DIR
  TARGET  same syntax as Source, but for where to copy to, not where to copy from

optional arguments:
  --help  show this help message and exit
  -p      copy out date/time stamps & permissions, not just dirs and bytes of files
  -q      say much less, like maybe forget to mention some failures
  -r      copy out a dir of dirs and files, not just bytes of a file

quirks:
  chokes till you provide some explicit Target, such as the LocalHost's '.'
  accepts lots more options, as sketched by:  man scp
  secretly silently adds options as configured by:  less -FIXR ~/.ssh/config'
  demos at Mac substitute 'sleep 1 && ls -l' for 'ls --full-time'

bash script to test this 'scp.py' locally or remotely:
  H=$(hostname)
  echo $H
  (set -xeuo pipefail
    (cd ..; tar czf shell2py.tgz shell2py/)
    scp -pqr ../shell2py.tgz $H:
    ssh $H 'rm -fr shell2py/'
    ssh $H 'tar xf shell2py.tgz'
    ssh -tA $H 'cd ~/ && shell2py/bin/scp.py --help && bash'
  )

examples:
  scp.py --h
  cd ~/
  SCP='shell2py/bin/scp.py'
  touch file && $SCP -pqr file localhost: && ls --full-time file
  rm -fr dir/ && mkdir -p dir/chi && $SCP -pr dir/ localhost: && ls --full -d dir/
"""

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_scp_py)


def parse_scp_args(argv):

    _scraps_.parse_left_help_args(argv, doc=__doc__)


def argv__to_scp_py(argv):
    """Write the Python for a Scp ArgV, else print some Help and quit"""

    parse_scp_args(argv)

    altv = list(argv)
    altv[0] = "scp"

    py = _scraps_.argv__to_shline_py(altv)

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
