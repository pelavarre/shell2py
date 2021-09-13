# shell2py
Let you paste fragments of Bash into Python, by cleaning up the syntax for you

Like if you say

    git clone https://github.com/pelavarre/shell2py.git
    cd shell2py/

    bin/shell2py ls -1

Then it says

    import os

    names = sorted(os.listdir())
    for name in names:
        if not name.startswith("."):  # if not hidden
            print(name)

\- copied by:  `git clone https://github.com/pelavarre/shell2py.git`
