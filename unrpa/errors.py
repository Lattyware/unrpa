from typing import Set, Optional

from unrpa.versions.version import Version


class UnRPAError(Exception):
    """Any error specific to unrpa."""

    def __init__(self, message: str, cmd_line_help: Optional[str] = None):
        self.message = message
        self.cmd_line_help = cmd_line_help
        super().__init__(message)


class OutputDirectoryNotFoundError(UnRPAError):
    """An error for when the given output directory doesn’t exist."""

    def __init__(self, path: str) -> None:
        super().__init__(
            f"The given output directory ({path}) does not exist.",
            "If you want to create it, use --mkdir.",
        )


class UnknownArchiveError(UnRPAError):
    """An error for when auto-detection of archive version gives no result."""

    def __init__(self, header: bytes) -> None:
        self.header = header
        decoded = header.decode("utf-8", "replace")
        super().__init__(
            "Auto-detection of the version for this archived failed—it is likely this archive is a version not "
            "supported. Try updating unrpa, or submitting a request for support at "
            "https://github.com/Lattyware/unrpa/issues/new?template=new-archive-version.md"
            f"Header: “{decoded.strip()}”",
            "You can try using --force to force a specific version rather than relying on auto-detection.",
        )


class AmbiguousArchiveError(UnRPAError):
    """An error for when auto-detection of archive version gives an ambiguous result."""

    def __init__(self, detected: Set[Version]) -> None:
        self.versions = detected
        detected_list = ", ".join(str(version) for version in detected)
        super().__init__(
            f"Auto-detection of the version for this archive failed because it is ambiguous. It could be any one of: "
            f"{detected_list}.",
            "You can try using --force to force these versions and see what works.",
        )


class ErrorExtractingFile(UnRPAError):
    """A wrapping error for when something goes wrong while extracting a file."""

    def __init__(self, detail: str) -> None:
        super().__init__(
            "There was an error while trying to extract a file from the archive.",
            "If you wish to try and extract as much from the archive as possible, please use --continue-on-error.\n"
            f"Error Detail: {detail}",
        )
