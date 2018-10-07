# unrpa - Extract files from the RPA archive format.

## About

unrpa is a script to extract files from the RPA archive format created
for [the Ren'Py Visual Novel Engine](http://www.renpy.org/).

## Dependencies

You will need Python 3.4 or later in order to run it (either install through
your package manager or
[directly from python.org](https://www.python.org/downloads/)).

## Installation

You can [download the latest release](https://github.com/Lattyware/unrpa/releases/latest)
and then run the script as described below.

## Command Line Usage

```
usage: unrpa [-h] [-v] [-s] [-l] [-p PATH] [-m] [-f VERSION]
             [--continue-on-error]
             FILENAME
```

### Options

| Positional Argument | Description              |
|---------------------|--------------------------|
| FILENAME            | the RPA file to extract. |

| Optional Argument            | Description                                                |
|------------------------------|------------------------------------------------------------|
|  -h, --help                  | show this help message and exit                            |
|  -v, --verbose               | explain what is being done [default].                      |
|  -s, --silent                | no output.                                                 |
|  -l, --list                  | only list contents, do not extract.                        |
|  -p PATH, --path PATH        | will extract to the given path.                            |
|  -m, --mkdir                 | will make any non-existent directories in extraction path. |
|  -f VERSION, --force VERSION | forces an archive version. May result in failure.          |
|  --continue-on-error         | try to continue extraction when something goes wrong.      |

### Examples

 - On most unix systems, open a terminal, then:
   `python3 unrpa -mp "path/to/output/dir" "path/to/archive.rpa"`
 - On most Windows systems, open a Command Prompt, then:
   `py -3 unrpa -mp "path\to\output\dir" "path\to\archive.rpa"`


