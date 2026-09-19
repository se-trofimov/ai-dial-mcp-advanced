from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "delete_users"

    @property
    def description(self) -> str:
        return "Delete a user by their ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"id": {"type": "integer", "description": "User ID."}},
            "required": ["id"],
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        return await self.user_client.delete_user(int(arguments["id"]))