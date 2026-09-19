from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Search users by optional name, surname, email, or gender."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "surname": {"type": "string"},
                "email": {"type": "string"},
                "gender": {"type": "string"},
            },
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        return await self.user_client.search_users(**arguments)