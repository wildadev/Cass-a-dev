"""Sandboxed file manager service."""

import asyncio
from pathlib import Path


class FileManagerService:
    """Provides sandboxed file read/write/list operations within allowed directories."""

    def __init__(self, allowed_dirs: list[Path]):
        self.allowed_dirs = [d.resolve() for d in allowed_dirs]

    def _validate_path(self, path: str) -> Path:
        """Resolve a path and verify it falls within an allowed directory.

        Raises ValueError if the path is outside all allowed directories.
        """
        resolved = Path(path).expanduser().resolve()
        for allowed in self.allowed_dirs:
            try:
                resolved.relative_to(allowed)
                return resolved
            except ValueError:
                continue
        raise ValueError(
            f"Path '{path}' is outside allowed directories: "
            f"{[str(d) for d in self.allowed_dirs]}"
        )

    async def read_file(self, path: str) -> str:
        """Read and return the text content of a file."""
        validated = self._validate_path(path)

        def _read():
            return validated.read_text(encoding="utf-8")

        return await asyncio.to_thread(_read)

    async def write_file(self, path: str, content: str) -> None:
        """Write text content to a file, creating parent directories if needed."""
        validated = self._validate_path(path)

        def _write():
            validated.parent.mkdir(parents=True, exist_ok=True)
            validated.write_text(content, encoding="utf-8")

        await asyncio.to_thread(_write)

    async def list_files(self, directory: str, pattern: str = "*") -> list[str]:
        """List files in a directory matching a glob pattern.

        Returns a list of absolute path strings.
        """
        validated = self._validate_path(directory)

        def _list():
            if not validated.is_dir():
                raise ValueError(f"'{directory}' is not a directory.")
            return [str(p) for p in sorted(validated.glob(pattern)) if p.is_file()]

        return await asyncio.to_thread(_list)
