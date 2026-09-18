import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.app.mcp.client import create_mcp_client


CLINIC_ID = "f51477c4-fb11-4480-af11-edb70650475c"
PATIENT_ID = "3314a2bb-c40c-4114-a56e-d42c121813ae"


async def main() -> None:
    async with create_mcp_client() as client:

        print("Calling MCP tool: get_patient_appointments")

        patient_appointments = await client.call_tool(
            "get_patient_appointments",
            {
                "clinic_id": CLINIC_ID,
                "patient_id": PATIENT_ID,
            },
        )

        print()
        print("Patient appointments result:")
        print(patient_appointments)

        print()
        print("=" * 60)
        print()

        print("Calling MCP tool: get_today_appointments")

        today_appointments = await client.call_tool(
            "get_today_appointments",
            {
                "clinic_id": CLINIC_ID,
            },
        )

        print()
        print("Today's appointments result:")
        print(today_appointments)


if __name__ == "__main__":
    asyncio.run(main())