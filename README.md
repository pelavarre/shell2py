# shell2py
Let you paste fragments of Bash into Python, by cleaning up the syntax for you

Like if you say

    shell2py ls -1

Then it says

    import os

    filenames = os.listdir()
    for filename in filenames:
        print(filename)

\- copied by:  `git clone https://github.com/pelavarre/shell2py.git`
