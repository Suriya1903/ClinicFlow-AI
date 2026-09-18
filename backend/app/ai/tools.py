from typing import Any

from langchain_core.tools import tool

from backend.app.mcp.client import (
    create_mcp_client,
    extract_tool_result,
)


async def _run_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    """
    Execute an MCP tool asynchronously and print
    diagnostic information for development.
    """

    print(
        f"[AI → MCP] Calling tool: {tool_name}"
    )

    print(
        f"[AI → MCP] Arguments: {arguments}"
    )

    try:
        async with create_mcp_client() as client:
            print(
                "[AI → MCP] MCP connection established."
            )

            result = await client.call_tool(
                tool_name,
                arguments,
                read_timeout_seconds=30.0,
            )

            print(
                f"[AI → MCP] Tool completed: {tool_name}"
            )

            response = extract_tool_result(result)

            print(
                f"[AI → MCP] Tool result: {response}"
            )

            return response

    except Exception as exc:
        print(
            f"[AI → MCP] Tool failed: {tool_name}"
        )
        print(
            f"[AI → MCP] Error: {exc!r}"
        )

        raise


@tool
async def get_active_patient_count(
    clinic_id: str,
) -> str:
    """
    Get the number of active patients registered
    in the clinic.
    """

    return await _run_mcp_tool(
        "get_active_patient_count",
        {
            "clinic_id": clinic_id,
        },
    )


@tool
async def search_patients(
    clinic_id: str,
    search_term: str,
) -> str:
    """
    Search active patients by name, phone number,
    or email.
    """

    return await _run_mcp_tool(
        "search_patients",
        {
            "clinic_id": clinic_id,
            "search_term": search_term,
        },
    )


@tool
async def get_patient_appointments(
    clinic_id: str,
    patient_id: str,
) -> str:
    """
    Get appointments belonging to a patient
    in the clinic.
    """

    return await _run_mcp_tool(
        "get_patient_appointments",
        {
            "clinic_id": clinic_id,
            "patient_id": patient_id,
        },
    )


@tool
async def get_today_appointments(
    clinic_id: str,
) -> str:
    """
    Get today's appointments for the clinic.
    """

    return await _run_mcp_tool(
        "get_today_appointments",
        {
            "clinic_id": clinic_id,
        },
    )