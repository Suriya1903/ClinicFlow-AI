from mcp import Client


class ClinicFlowMCPClient:
    """
    Client used by AgentForge to communicate with
    the ClinicFlow MCP server.
    """

    def __init__(
        self,
        server_url: str,
    ) -> None:
        self.server_url = server_url

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ) -> str:
        """
        Connect to the MCP server and execute a tool.
        """

        async with Client(
            self.server_url
        ) as client:

            result = await client.call_tool(
                tool_name,
                arguments,
            )

            return self._extract_text(result)

    @staticmethod
    def _extract_text(result) -> str:
        """
        Extract text returned by an MCP tool.
        """

        if hasattr(result, "content"):
            text_parts = []

            for item in result.content:
                if hasattr(item, "text"):
                    text_parts.append(
                        item.text
                    )

            if text_parts:
                return "\n".join(
                    text_parts
                )

        return str(result)