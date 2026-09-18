from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.transport_security import (
    TransportSecuritySettings,
)

from mcp_server.server import mcp


# ==========================================================
# MCP TRANSPORT SECURITY
# ==========================================================

security = TransportSecuritySettings(
    allowed_hosts=[
        "mcp-server:8001",
        "localhost:*",
        "127.0.0.1:*",
    ],
    allowed_origins=[
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
)


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================


@asynccontextmanager
async def lifespan(
    app,
) -> AsyncIterator[None]:
    """
    Start the MCP session manager for the lifetime
    of the HTTP application.
    """

    async with mcp.session_manager.run():
        yield


# ==========================================================
# MCP STREAMABLE HTTP APPLICATION
# ==========================================================


app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    host="127.0.0.1",
    transport_security=security,
)

# The MCP application is mounted directly into Uvicorn,
# therefore its session manager must be started explicitly.
app.router.lifespan_context = lifespan