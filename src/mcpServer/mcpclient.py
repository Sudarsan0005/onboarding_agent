import asyncio
import json
import logging
import os
from typing import Optional,List,Dict,Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logging.info(msg=f"\nConnected to server with tools: {[tool.name for tool in tools]}")

    def convert_schema_format(self, input_schema: dict) -> dict:
        """Convert MCP schema format to OpenAI function calling format"""
        if not input_schema or "properties" not in input_schema:
            return {"type": "object", "properties": {}, "required": []}

        converted_properties = {}
        for prop_name, prop_details in input_schema["properties"].items():
            converted_properties[prop_name] = {
                "type": prop_details.get("type", "string"),
                "description": prop_details.get("title", prop_name)
            }

        return {
            "type": input_schema.get("properties",{}).get("type","object"),
            "properties": converted_properties,
            "required": input_schema.get("required", [])
        }

    async def return_toolconfig(self) -> List[Dict[str,Any]]:
        """return available tools"""

        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": self.convert_schema_format(tool.inputSchema)
            }
        } for tool in response.tools]
        return available_tools
    async def calling_tool(self,tool_name,tool_args):
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            return result.content
        except Exception:
            pass
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def tool_configuration():
    client = MCPClient()
    try:
        base_dir = os.path.dirname(os.path.dirname(os.getcwd()))
        server_path = os.path.join(base_dir, "src", "mcpServer", "doc_validator.py")
        await client.connect_to_server(server_path)

        tool_config = await client.return_toolconfig()
    finally:
        await client.cleanup()
    return tool_config
async def call_mcp_tools(tool_name,tool_args):
    client = MCPClient()
    try:
        base_dir = os.path.dirname(os.path.dirname(os.getcwd()))  # Go up two levels
        server_path = os.path.join(base_dir, "src", "mcpServer", "doc_validator.py")
        await client.connect_to_server(server_path)

        tool_response = await client.calling_tool(tool_name=tool_name,tool_args=tool_args)
    finally:
        await client.cleanup()
    tool_response = tool_response[0].text
    # tool_response = json.loads(tool_response)
    return tool_response
# if __name__ == "__main__":
#     import sys
#     tool_con = asyncio.run(call_mcp_tools(tool_name="validate_dealer",tool_args={"dealer_code":"56436"}))
#     print(tool_con)
    # tool_con = asyncio.run(tool_configuration())
#     print(tool_con)
#     print(type(tool_con))
#     from openai import OpenAI
#     from constant import (DB_Manager, doc_extraction_prompt)
#     # from src.mcpServer.get_toolConfig import tool_configuration
#     import os
#     import time
#
#     client = OpenAI()
#     assistant = client.beta.assistants.create(
#         name="test",
#         model="gpt-4o-mini",
#         tools=tool_con
#     )
#     print(assistant.id)
#     print(assistant.tools)