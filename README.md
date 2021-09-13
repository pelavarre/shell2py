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

Shell2Py more reminds you well of the stuff you only do now and again, not so much explains the stuff you do often

Examples =>

### 1 ) How Python spells each Shell idea

Shell2Py tels you how Python spells the Shell idea of reading binary Bytes out of Stdin, in place of text Chars, exactly where your knowledge of the Shell teaches you to expect to hear this story, at

    shell2py grep -a HelloBinaryStdin

### 2 ) How your Shell reads you

Shell2Py shows you how your Shell reads you, such as does it find 1 or 2 or 3 words here

    shell2py echo 'quotes '\''within'\'' quotes'

### 3 ) Ordinary Shell features that your Shell doesn't deliver

Shell2Py gives you ordinary Shell features that your Shell doesn't deliver, as double-dash long options
    
    bin/echo.py --verbose Hello 'Shell World!'

In particular, you can learn the Linux Shell way or the Mac Shell way and still carry your way with you on into the other place


### 4 ) Just the Help Lines that matter to you

Forking Shell2Py sets you up to keep just the Help Lines that matter to you in front of you, such as our choice of a couple of dozen lines for our Man Less

    bin/less.py |wc -l

By contrast, your 'man less' will give you more than a thousand Help Lines to wade through, and less relevant examples

