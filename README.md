# shell2py
Let you paste fragments of Bash into Python, by cleaning up the Python syntax for you

## Demo

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

## Motivation

When do you care?

When you know some little wrinkle in Python or Bash is on the tip of your tongue and you need it to come to you faster

Shell2Py helps you more with the stuff you only do some of the time, not so much with the stuff you do often

Examples =>

1 )

Shell2Py shows you how your Shell counts args, such as 1 or 2 or 3 words found here

    shell2py echo 'quotes '\''within'\'' quotes'

2 )

Shell2Py gives you features that your Shell doesn't deliver, as double-dash long options
    
    echo.py --verbose Hello 'Shell World!'

This way you can learn the Linux way or the Mac way and still carry it with you to the other place

3 )

Forking Shell2Py sets you up to keep just the Help Lines that matter to you in front of you, such as our choice of less than three dozen for Less

    bin/less.py |wc -l

By contrast, your 'man less' will give you more than a thousand Help Lines to wade through, and less relevant examples





