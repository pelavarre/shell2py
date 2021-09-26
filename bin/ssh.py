#!/usr/bin/env python3

"""
usage: ssh.py [--help] [-t] [-A] HOST SHLINE

send Shell Command Lines to Remote Hosts, less openly than over Http without S

positional arguments:
  HOST    where to run the Shell Command Line (such as 'localhost')
  SHLINE  the Shell Command Line to interpret as configured out there

optional arguments:
  --help  show this help message and exit
  -t      keep the Terminal connected while running (like for 'vim' to work)
  -A      tell the 'ssh-add -l' LocalHost Ssh Agent to trust the Remote Host

quirks:
  accepts lots more options, as sketched by:  man ssh
  secretly silently adds options as configured by:  less -FIXR ~/.ssh/config'

examples:
  ssh.py --h
  H=$(hostname)
  ssh $H 'hostname; pwd; TZ=America/Los_Angeles date; date -u'
"""

import _scraps_


def main():

    _scraps_.module_name__main(__name__, argv__to_py=argv__to_ssh_py)


def parse_ssh_args(argv):

    _scraps_.parse_left_help_args(argv, doc=__doc__)


def argv__to_ssh_py(argv):
    """Write the Python for a Ssh ArgV, else print some Help and quit"""

    parse_ssh_args(argv)

    altv = list(argv)
    altv[0] = "ssh"

    py = _scraps_.argv__to_shline_py(altv)

    return py


if __name__ == "__main__":
    main()


# copied by: git clone https://github.com/pelavarre/shell2py.git
