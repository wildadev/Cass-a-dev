import logging

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class FileTool(BaseTool):
    @property
    def name(self) -> str:
        return "files"

    @property
    def description(self) -> str:
        return (
            "Manage files: read file contents, write content to a file, "
            "or list files in a directory with an optional glob pattern."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read_file", "write_file", "list_files"],
                    "description": "The file action to perform.",
                },
                "path": {
                    "type": "string",
                    "description": "File path (for read_file, write_file) or directory path (for list_files).",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file (for write_file).",
                },
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from (for list_files).",
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter files (for list_files). Default '*'.",
                    "default": "*",
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "read_file":
                path = kwargs.get("path")
                if not path:
                    return {"error": "path is required for read_file"}
                return await self._read_file(path)
            elif action == "write_file":
                path = kwargs.get("path")
                content = kwargs.get("content")
                if not path or content is None:
                    return {"error": "path and content are required for write_file"}
                return await self._write_file(path, content)
            elif action == "list_files":
                directory = kwargs.get("directory")
                if not directory:
                    return {"error": "directory is required for list_files"}
                return await self._list_files(
                    directory=directory,
                    pattern=kwargs.get("pattern", "*"),
                )
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"FileTool.{action} failed")
            return {"error": str(e)}

    async def _read_file(self, path: str) -> dict:
        from cass.services.file_manager import FileManagerService

        service = FileManagerService()
        content = await service.read_file(path=path)
        return {"action": "read_file", "path": path, "content": content}

    async def _write_file(self, path: str, content: str) -> dict:
        from cass.services.file_manager import FileManagerService

        service = FileManagerService()
        await service.write_file(path=path, content=content)
        return {"action": "write_file", "path": path, "message": "File written successfully."}

    async def _list_files(self, directory: str, pattern: str) -> dict:
        from cass.services.file_manager import FileManagerService

        service = FileManagerService()
        files = await service.list_files(directory=directory, pattern=pattern)
        return {"action": "list_files", "directory": directory, "pattern": pattern, "files": files}
