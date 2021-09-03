# shell2py
Let you paste fragments of Bash into Python, by cleaning up the syntax for you

Like if you say

    git clone https://github.com/pelavarre/shell2py.git
    cd shell2py/

    bin/shell2py ls -1

Then it says

    import os

    filenames = sorted(os.listdir())
    for filename in filenames:
        if not filename.startswith("."):  # if not hidden
            print(filename)

\- copied by:  `git clone https://github.com/pelavarre/shell2py.git`
