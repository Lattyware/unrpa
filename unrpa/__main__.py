#!/usr/bin/env python3

"""
unrpa is a tool to extract files from Ren'Py archives (.rpa).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import os
import sys
from typing import Tuple, Optional, Any

from unrpa import UnRPA
from unrpa.errors import UnRPAError


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="unrpa",
        description="Extract files from the RPA archive format (from the Ren'Py Visual Novel Engine).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        default=1,
        help="explain what is being done [default].",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_const",
        const=0,
        dest="verbose",
        help="no output.",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        dest="list",
        default=False,
        help="only list contents, do not extract.",
    )
    parser.add_argument(
        "-p",
        "--path",
        action="store",
        type=str,
        dest="path",
        default=None,
        help="will extract to the given path.",
    )
    parser.add_argument(
        "-m",
        "--mkdir",
        action="store_true",
        dest="mkdir",
        default=False,
        help="will make any non-existent directories in extraction path.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store",
        type=str,
        dest="version",
        default=None,
        help="forces an archive version. May result in failure. Possible versions: "
        + ", ".join(version.name for version in UnRPA.provided_versions)
        + ".",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        dest="continue_on_error",
        default=False,
        help="try to continue extraction when something goes wrong.",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        type=int,
        dest="offset",
        default=None,
        help="sets an offset to be used to decode unsupported archives.",
    )
    parser.add_argument(
        "-k",
        "--key",
        action="store",
        type=int,
        dest="key",
        default=None,
        help="sets a key to be used to decode unsupported archives.",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 2.0.1")

    parser.add_argument(
        "filename", metavar="FILENAME", type=str, help="the RPA file to extract."
    )

    args: Any = parser.parse_args()

    provided_version = None
    if args.version:
        try:
            provided_version = next(
                version
                for version in UnRPA.provided_versions
                if args.version.lower() == version.name.lower()
            )
        except StopIteration:
            parser.error(
                "The archive version you gave isn’t one we recognise - it needs to be one of: "
                + ", ".join(version.name for version in UnRPA.provided_versions)
            )

    provided_offset_and_key: Optional[Tuple[int, int]] = None
    if args.key and args.offset:
        provided_offset_and_key = (args.offset, args.key)
    elif bool(args.key) != bool(args.offset):
        parser.error("If you set --key or --offset, you must set both.")

    if args.list and args.path:
        parser.error("Option -path: only valid when extracting.")

    if args.mkdir and not args.path:
        parser.error("Option --mkdir: only valid when --path is set.")

    if not args.mkdir and args.path and not os.path.isdir(args.path):
        parser.error(f"No such directory: “{args.path}”. Use --mkdir to create it.")

    if args.list and args.verbose == 0:
        parser.error("Option --list: can’t be silent while listing data.")

    if not os.path.isfile(args.filename):
        parser.error(f"No such file: “{args.filename}”.")

    try:
        extractor = UnRPA(
            args.filename,
            args.verbose,
            args.path,
            args.mkdir,
            provided_version,
            args.continue_on_error,
            provided_offset_and_key,
        )
        if args.list:
            extractor.list_files()
        else:
            extractor.extract_files()
    except UnRPAError as error:
        help_message = f"\n{error.cmd_line_help}" if error.cmd_line_help else ""
        sys.exit(f"\n\033[31m{error.message}{help_message}\033[30m")


if __name__ == "__main__":
    main()
