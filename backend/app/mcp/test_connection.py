import asyncio

from backend.app.mcp.client import (
    create_mcp_client,
    extract_tool_result,
)


CLINIC_ID = "f51477c4-fb11-4480-af11-edb70650475c"


async def main() -> None:
    print("Connecting to MCP server...")

    async with create_mcp_client() as client:
        print("Connected to MCP server.")

        result = await client.call_tool(
            "get_active_patient_count",
            {
                "clinic_id": CLINIC_ID,
            },
        )

        print("MCP result:")
        print(extract_tool_result(result))


if __name__ == "__main__":
    asyncio.run(main())