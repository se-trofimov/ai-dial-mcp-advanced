import uuid
import asyncio

from mcp_server.models.request import MCPRequest
from mcp_server.models.response import MCPResponse, ErrorResponse
from mcp_server.tools.users.create_user_tool import CreateUserTool
from mcp_server.tools.users.delete_user_tool import DeleteUserTool
from mcp_server.tools.users.get_user_by_id_tool import GetUserByIdTool
from mcp_server.tools.users.search_users_tool import SearchUsersTool
from mcp_server.tools.users.update_user_tool import UpdateUserTool
from mcp_server.tools.users.user_client import UserClient


class MCPSession:
    """Represents an MCP session with state management"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.ready_for_operation = False
        self.created_at = asyncio.get_event_loop().time()
        self.last_activity = self.created_at


class MCPServer:

    def __init__(self):
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "custom-ums-mcp-server",
            "version": "1.0.0"
        }

        # Session management
        self.sessions: dict[str, MCPSession] = {}
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available tools"""
        user_client = UserClient()
        tools = [
            GetUserByIdTool(user_client),
            SearchUsersTool(user_client),
            CreateUserTool(user_client),
            UpdateUserTool(user_client),
            DeleteUserTool(user_client),
        ]
        self.tools = {tool.name: tool for tool in tools}

    def _validate_protocol_version(self, client_version: str) -> str:
        """Validate and negotiate protocol version"""
        supported_versions = ["2024-11-05"]
        if client_version in supported_versions:
            return client_version
        return self.protocol_version

    def get_session(self, session_id: str) -> MCPSession | None:
        """Get an existing session"""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = asyncio.get_event_loop().time()
        return session

    def handle_initialize(self, request: MCPRequest) -> tuple[MCPResponse, str]:
        """Handle initialization request with session creation"""
        session_id = str(uuid.uuid4()).replace("-", "")
        self.sessions[session_id] = MCPSession(session_id)
        client_version = request.params.get("protocolVersion") if request.params else self.protocol_version
        protocol_version = self._validate_protocol_version(client_version)
        mcp_response = MCPResponse(
            id=request.id,
            result={
                "protocolVersion": protocol_version,
                "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                "serverInfo": self.server_info,
            },
        )
        return mcp_response, session_id

    def handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request"""
        tools_list = [tool.to_mcp_tool() for tool in self.tools.values()]
        return MCPResponse(id=request.id, result={"tools": tools_list})

    async def handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request with proper MCP-compliant response format"""
        if not request.params:
            return MCPResponse(id=request.id, error=ErrorResponse(code=-32602, message="Missing parameters"))

        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        if not tool_name:
            return MCPResponse(
                id=request.id,
                error=ErrorResponse(code=-32602, message="Missing required parameter: name"),
            )
        if tool_name not in self.tools:
            return MCPResponse(
                id=request.id,
                error=ErrorResponse(code=-32601, message=f"Tool '{tool_name}' not found"),
            )

        try:
            result_text = await self.tools[tool_name].execute(arguments)
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result_text}]},
            )
        except Exception as tool_error:
            return MCPResponse(
                id=request.id,
                result={
                    "content": [{"type": "text", "text": f"Tool execution error: {tool_error}"}],
                    "isError": True,
                },
            )
