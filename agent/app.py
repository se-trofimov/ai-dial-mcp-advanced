import asyncio
import os

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.mcp_client import MCPClient
from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role


async def main():
    tools = []
    tool_name_client_map: dict[str, MCPClient | CustomMCPClient] = {}

    ums_client = await CustomMCPClient.create("http://localhost:8006/mcp")
    fetch_client = await MCPClient.create("https://remote.mcpservers.org/fetch/mcp")

    for client in (ums_client, fetch_client):
        client_tools = await client.get_tools()
        tools.extend(client_tools)
        tool_name_client_map.update({tool["function"]["name"]: client for tool in client_tools})

    api_key = os.getenv("DIAL_API_KEY")
    if not api_key:
        raise RuntimeError("Set the DIAL_API_KEY environment variable before starting the agent.")

    dial_client = DialClient(
        api_key=api_key,
        endpoint="https://ai-proxy.lab.epam.com",
        tools=tools,
        tool_name_client_map=tool_name_client_map,
    )
    messages = [
        Message(
            role=Role.SYSTEM,
            content="Help the user with their request. Use the available tools when they provide needed information.",
        )
    ]

    print("Agent ready. Type 'exit' to finish.")
    while user_input := input("You: ").strip():
        if user_input.lower() == "exit":
            break
        messages.append(Message(role=Role.USER, content=user_input))
        messages.append(await dial_client.get_completion(messages))

if __name__ == "__main__":
    asyncio.run(main())


# Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him