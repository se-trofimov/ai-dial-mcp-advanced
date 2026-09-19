from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class GetUserByIdTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "get_user_by_id"

    @property
    def description(self) -> str:
        return "Get a user by their ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"id": {"type": "integer", "description": "User ID."}},
            "required": ["id"],
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        return await self.user_client.get_user(int(arguments["id"]))