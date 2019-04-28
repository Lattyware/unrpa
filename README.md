# unrpa - Extract files from the RPA archive format.

## About

unrpa is a tool to extract files from the RPA archive format (from 
[the Ren'Py Visual Novel Engine](http://www.renpy.org/).

It can also be used as a library.

## Installation

### Package manager

The best way to install unrpa is through your package manager, if a package is available for your operating system.
I maintain [an AUR package](https://aur.archlinux.org/packages/unrpa/)) for Arch Linux users.

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

### Examples

When installed through your package manager or pip, you should be able to use unrpa by opening a terminal or command 
prompt and doing something like:

    unrpa -mp "path/to/output/dir" "path/to/archive.rpa"
    
If you are running from source, you will need execute python directly:

 - On most unix systems, open a terminal in the directory containing unrpa then:
 
       python3 -m unrpa -mp "path/to/output/dir" "path/to/archive.rpa"
     
 - On most Windows systems, open a Command Prompt in the directory containing unrpa then:
 
       py -3 -m unrpa -mp "path\to\output\dir" "path\to\archive.rpa"

## Command Line Usage

```
usage: unrpa [-h] [-v] [-s] [-l] [-p PATH] [-m] [-f VERSION]
             [--continue-on-error] [-o OFFSET] [-k KEY] [--version]
             FILENAME
```

### Options

| Positional Argument | Description              |
|---------------------|--------------------------|
| FILENAME            | the RPA file to extract. |

| Optional Argument            | Description                                                    |
|------------------------------|----------------------------------------------------------------|
| -h, --help                   | show this help message and exit                                |
| -v, --verbose                | explain what is being done [default].                          |
| -s, --silent                 | no output.                                                     |
| -l, --list                   | only list contents, do not extract.                            |
| -p PATH, --path PATH         | will extract to the given path.                                |
| -m, --mkdir                  | will make any non-existent directories in extraction path.     |
| -f VERSION, --force VERSION  | forces an archive version. May result in failure.<br>Possible versions: RPA-3.0, ZiX-12A, ZiX-12B, ALT-1.0, RPA-2.0, RPA-1.0. |
| --continue-on-error          | try to continue extraction when something goes wrong.          | 
| -o OFFSET, --offset OFFSET   | sets an offset to be used to decode unsupported archives.      |
| -k KEY, --key KEY            | sets a key to be used to decode unsupported archives.          |
| --version                    | show program's version number and exit                         |
