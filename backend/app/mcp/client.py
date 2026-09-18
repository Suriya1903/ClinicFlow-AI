from collections.abc import Mapping
from typing import Any

from mcp import Client

from backend.app.core.config import settings


MCP_READ_TIMEOUT_SECONDS = 30.0


def create_mcp_client() -> Client:
    """
    Create an MCP client connected to the ClinicFlow MCP server.
    """

    return Client(
        settings.mcp_server_url,
        raise_exceptions=True,
        read_timeout_seconds=MCP_READ_TIMEOUT_SECONDS,
    )


def extract_tool_result(result: Any) -> str:
    """
    Convert an MCP CallToolResult into a clean text response.

    The installed MCP SDK returns structured result objects
    containing content and structured_content.
    """

    if getattr(result, "is_error", False):
        return "MCP tool execution failed."

    structured_content = getattr(
        result,
        "structured_content",
        None,
    )

    if isinstance(structured_content, Mapping):
        value = structured_content.get("result")

        if value is not None:
            return str(value)

    content = getattr(
        result,
        "content",
        None,
    )

    if content:
        text_parts: list[str] = []

        for item in content:
            text = getattr(
                item,
                "text",
                None,
            )

            if text is not None:
                text_parts.append(str(text))

        if text_parts:
            return "\n".join(text_parts)

    return str(result)