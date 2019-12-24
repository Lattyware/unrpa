# unrpa - Extract files from the RPA archive format.

[![PyPI](https://img.shields.io/pypi/v/unrpa)](https://pypi.org/project/unrpa/) 
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/unrpa)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/license/Lattyware/unrpa)](https://github.com/Lattyware/unrpa/blob/master/COPYING)
[![MyPy Check](https://github.com/Lattyware/unrpa/workflows/MyPy%20Check/badge.svg)](https://github.com/Lattyware/unrpa/actions?query=workflow%3A%22MyPy+Check%22)

## About

unrpa is a tool to extract files from the RPA archive format (from 
[the Ren'Py Visual Novel Engine](http://www.renpy.org/)).

It can also be used as a library.

## Installation

### Package manager

The best way to install unrpa is through your package manager, if a package is available for your operating system.
I maintain [an AUR package](https://aur.archlinux.org/packages/unrpa/) for Arch Linux users.

### pip

You can also install unrpa through pip, the Python package manager. You can do this on Windows with:

    py -3 -m pip install "unrpa"
    
Or use `python3` rather than `py -3` on unix systems. You can see 
[the official documentation](https://packaging.python.org/tutorials/installing-packages/) for more help installing 
through pip.

### From source

You can also [download the latest release](https://github.com/Lattyware/unrpa/releases/latest)
and extract it.

## Dependencies

You will need Python 3.7 or later in order to run it (either install through
your package manager or
[directly from python.org](https://www.python.org/downloads/)).

If you are trying to extract more exotic RPA archives, there may be additional dependencies. unrpa should instruct 
you how to install them if required.

Package maintainers can see [`setup.py`](https://github.com/Lattyware/unrpa/blob/master/setup.py) for a complete set 
of dependencies.

### Examples

When installed through your package manager or pip, you should be able to use unrpa by opening a terminal or command 
prompt and doing something like:

    unrpa -mp "path/to/output/dir" "path/to/archive.rpa"
    
If you are running from source, you will need execute python directly:

 - On most unix systems, open a terminal in the directory containing unrpa then:
 
       python3 -m unrpa -mp "path/to/output/dir" "path/to/archive.rpa"
     
 - On most Windows systems, open a Command Prompt in the directory containing unrpa then:
 
       py -3 -m unrpa -mp "path\to\output\dir" "path\to\archive.rpa"

## Command line usage

```
usage: unrpa [-h] [-v] [-s] [-l | -t] [-p PATH] [-m] [--version]
             [--continue-on-error] [-f VERSION] [-o OFFSET] [-k KEY]
             FILENAME [FILENAME ...]
```

### Options

| Positional Argument | Description                |
|---------------------|----------------------------|
| FILENAME            | the archive(s) to extract. |

| Optional Argument            | Description                                                               |
|------------------------------|---------------------------------------------------------------------------|
| -h, --help                   | show this help message and exit                                           |
| -v, --verbose                | explain what is being done, duplicate for more verbosity (default: 1).    |
| -s, --silent                 | no non-essential output.                                                  |
| -l, --list                   | list the contents of the archive(s) in a flat list.                       |
| -t, --tree                   | list the contents of the archive(s) in a tree view                        |
| -p PATH, --path PATH         | extract files to the given path (default: the current working directory). |
| -m, --mkdir                  | will make any missing directories in the given extraction path.           |
| --version                    | show program's version number and exit                                    |

| Advanced Argument            | Description                                           |
|------------------------------|-------------------------------------------------------|
| --continue-on-error          | try to continue extraction when something goes wrong. |
| -f VERSION, --force VERSION  | ignore the archive header and assume this exact version. Possible versions: RPA-1.0, RPA-2.0, RPA-3.0, ALT-1.0, ZiX-12A, ZiX-12B, RPA-3.2, RPA-4.0. |
| -o OFFSET, --offset OFFSET   | ignore the archive header and use this exact offset.  |
| -k KEY, --key KEY            | ignore the archive header and use this exact key.     |  


## Errors

### Common errors

  - Check you are using the latest version of Python 3.
  - Check you are using quotes around file paths.
  - Video guides may be out of date, please check this file for up-to-date advice on using the tool.

### New errors

If something goes wrong while extracting an archive, please 
[make an issue](https://github.com/Lattyware/unrpa/issues/new). 

New variants of the RPA format get created regularly, so new games might not work - generally support can be 
added quickly though.
