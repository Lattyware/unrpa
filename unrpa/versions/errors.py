from typing import Optional

from unrpa.errors import UnRPAError


class VersionSpecificRequirementUnmetError(UnRPAError):
    """An error where the version of the archive has a special need that is unmet."""

    def __init__(self, message: str, cmd_line_help: Optional[str] = None) -> None:
        super().__init__(message, cmd_line_help)


class MissingPackageError(VersionSpecificRequirementUnmetError):
    """An error where the version of the archive requires a Python package that isn't installed."""

    def __init__(self, package: str) -> None:
        super().__init__(
            f"Extracting from this archive requires the package “{package}”.",
            f'You can do this by running “pip install "{package}"”. See '
            f"https://packaging.python.org/tutorials/installing-packages for more help on installing python packages.",
        )
