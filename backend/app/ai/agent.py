import ast
import re
from datetime import datetime

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from backend.app.ai.state import AgentState
from backend.app.ai.tools import (
    get_active_patient_count,
    get_patient_appointments,
    get_today_appointments,
    search_patients,
)


# ==========================================================
# PATIENT NAME EXTRACTION
# ==========================================================


def extract_patient_name(
    message: str,
) -> str | None:
    """
    Extract a likely patient name from a natural-language
    patient-specific request.

    Examples:
        Show Rahul Kumar's appointments
        Show Rahul Kumar appointments
        Find Rahul Kumar
        Find patient Rahul Kumar
        Search patient Rahul Kumar
        What are Rahul Kumar's appointments?
    """

    text = message.strip()

    # Remove common sentence-ending punctuation.
    text = re.sub(
        r"[.!?,;:]+$",
        "",
        text,
    ).strip()

    patterns = [
        r"show\s+me\s+(.+?)(?:'s|s)?\s+appointments?$",
        r"show\s+(.+?)(?:'s|s)?\s+appointments?$",
        r"what\s+are\s+(.+?)(?:'s|s)?\s+appointments?$",
        r"what\s+is\s+(.+?)(?:'s|s)?\s+appointment?$",
        r"find\s+patient\s+(.+)$",
        r"find\s+(.+)$",
        r"search\s+patient\s+(.+)$",
        r"search\s+for\s+patient\s+(.+)$",
        r"search\s+for\s+(.+)$",
        r"show\s+patient\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            name = match.group(1).strip()

            # Remove possessive apostrophe if it remains.
            name = (
                name.rstrip("'")
                .strip()
            )

            # Remove any remaining sentence punctuation.
            name = re.sub(
                r"[.!?,;:]+$",
                "",
                name,
            ).strip()

            if name:
                return name

    return None


# ==========================================================
# INTENT DETECTION
# ==========================================================


def detect_intent(message: str) -> str:
    """
    Determine which operational information the user wants.

    Intent priority:

        1. Clinic summary
        2. Today's appointments
        3. Active patient count
        4. Patient-specific appointments
        5. Patient-specific search
        6. Default clinic summary

    Important distinction:

        "Show today's appointments"
            -> today_appointments

        "Show Rahul Kumar appointments"
            -> patient_search

        "Show Rahul Kumar's appointments"
            -> patient_appointments

    This preserves the existing application behavior while
    supporting explicit patient appointment requests.
    """

    text = message.lower().strip()

    # ------------------------------------------------------
    # 1. Clinic summary
    #
    # Check summary requests first because a summary can
    # contain words such as "patient" and "appointments".
    # ------------------------------------------------------

    summary_keywords = [
        "clinic summary",
        "daily summary",
        "daily clinic summary",
        "today's summary",
        "todays summary",
        "today summary",
        "overall summary",
        "clinic overview",
        "clinic status",
    ]

    if any(
        keyword in text
        for keyword in summary_keywords
    ):
        return "clinic_summary"

    # ------------------------------------------------------
    # 2. Today's appointments
    #
    # IMPORTANT:
    # Check this BEFORE extracting a patient name.
    #
    # Otherwise:
    #
    #     "Show today's appointments"
    #
    # could extract "today" as a patient name.
    # ------------------------------------------------------

    appointment_keywords = [
        "appointments today",
        "today's appointments",
        "todays appointments",
        "today appointment",
        "appointments for today",
        "appointments scheduled today",
        "what appointments",
        "show appointments",
        "list appointments",
    ]

    if any(
        keyword in text
        for keyword in appointment_keywords
    ):
        return "today_appointments"

    # ------------------------------------------------------
    # 3. Active patient count
    # ------------------------------------------------------

    patient_count_keywords = [
        "how many patients",
        "how many active patients",
        "active patient count",
        "number of patients",
        "patient count",
        "total patients",
        "active patients",
    ]

    if any(
        keyword in text
        for keyword in patient_count_keywords
    ):
        return "active_patient_count"

    # ------------------------------------------------------
    # 4. Patient-specific request
    # ------------------------------------------------------

    patient_name = extract_patient_name(
        message
    )

    if patient_name:

        # --------------------------------------------------
        # Explicit patient appointment request
        #
        # Only classify as patient_appointments when the
        # request clearly uses a possessive form:
        #
        #     Rahul Kumar's appointments
        #
        # This is intentionally NOT triggered by:
        #
        #     Rahul Kumar appointments
        #
        # because the existing tests expect that request
        # to remain a patient_search intent.
        # --------------------------------------------------

        patient_appointment_patterns = [
            r"\bwhat\s+are\s+.+?'s\s+appointments?\b",
            r"\bwhat\s+is\s+.+?'s\s+appointment\b",
            r"\bshow\s+me\s+.+?'s\s+appointments?\b",
            r"\bshow\s+.+?'s\s+appointments?\b",
        ]

        if any(
            re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
            for pattern in patient_appointment_patterns
        ):
            return "patient_appointments"

        # --------------------------------------------------
        # Normal patient search
        # --------------------------------------------------

        return "patient_search"

    # ------------------------------------------------------
    # 5. Default
    # ------------------------------------------------------

    return "clinic_summary"


# ==========================================================
# MCP DATA PARSING
# ==========================================================


def parse_list_data(
    data,
) -> list:
    """
    Convert MCP output into a Python list.

    MCP responses can arrive either as an actual list
    or as a string representation of a Python list.
    """

    if isinstance(data, list):
        return data

    if isinstance(data, str):
        text = data.strip()

        if not text:
            return []

        try:
            parsed = ast.literal_eval(
                text
            )

            if isinstance(
                parsed,
                list,
            ):
                return parsed

        except (
            ValueError,
            SyntaxError,
        ):
            pass

    return []


# ==========================================================
# APPOINTMENT FORMATTING
# ==========================================================


def format_appointment(
    appointment: dict,
    patient_name: str | None = None,
) -> str:
    """
    Format an appointment into a human-readable sentence.

    patient_name is supplied for patient-specific appointment
    results because that MCP response does not contain the
    patient name.
    """

    patient = (
        patient_name
        or appointment.get(
            "patient",
            "Unknown patient",
        )
    )

    doctor = appointment.get(
        "doctor",
        "Unknown doctor",
    )

    status = appointment.get(
        "status",
        "unknown",
    )

    scheduled_at = appointment.get(
        "scheduled_at",
    )

    time_text = (
        "scheduled time unavailable"
    )

    date_text = ""

    if scheduled_at:
        try:
            appointment_datetime = (
                datetime.fromisoformat(
                    str(scheduled_at)
                )
            )

            date_text = (
                appointment_datetime.strftime(
                    "%d %b %Y"
                )
            )

            time_text = (
                appointment_datetime.strftime(
                    "%I:%M %p"
                ).lstrip("0")
            )

        except ValueError:
            time_text = str(
                scheduled_at
            )

    if date_text:
        return (
            f"{patient} is scheduled with "
            f"{doctor} at {time_text} "
            f"on {date_text}. "
            f"Status: {status}."
        )

    return (
        f"{patient} is scheduled with "
        f"{doctor} at {time_text}. "
        f"Status: {status}."
    )


# ==========================================================
# PATIENT COUNT FORMATTING
# ==========================================================


def format_patient_count(
    result: str,
) -> str:
    """
    Convert the MCP patient count into
    grammatically correct text.
    """

    text = str(
        result
    ).strip()

    match = re.search(
        r"\b(\d+)\b",
        text,
    )

    if not match:
        return text

    count = int(
        match.group(1)
    )

    if count == 1:
        return (
            "There is 1 active patient "
            "registered in the clinic."
        )

    return (
        f"There are {count} active patients "
        f"registered in the clinic."
    )


# ==========================================================
# PATIENT FIELD HELPERS
# ==========================================================


def get_patient_id(
    patient: dict,
):
    """
    Support common patient ID field names.
    """

    return (
        patient.get("patient_id")
        or patient.get("id")
    )


def get_patient_name(
    patient: dict,
) -> str:
    """
    Support common patient name field names.
    """

    name = (
        patient.get("name")
        or patient.get("full_name")
    )

    if name:
        return str(name)

    first_name = patient.get(
        "first_name",
        "",
    )

    last_name = patient.get(
        "last_name",
        "",
    )

    full_name = (
        f"{first_name} {last_name}"
    ).strip()

    return (
        full_name
        or "Unknown patient"
    )


# ==========================================================
# ACTIVE PATIENT COUNT
# ==========================================================


async def handle_active_patient_count(
    clinic_id: str,
) -> str:
    result = (
        await get_active_patient_count.ainvoke(
            {
                "clinic_id": clinic_id,
            }
        )
    )

    return format_patient_count(
        result
    )


# ==========================================================
# TODAY'S APPOINTMENTS
# ==========================================================


async def handle_today_appointments(
    clinic_id: str,
) -> str:
    result = (
        await get_today_appointments.ainvoke(
            {
                "clinic_id": clinic_id,
            }
        )
    )

    appointments = parse_list_data(
        result
    )

    if not appointments:
        return (
            "There are no appointments "
            "scheduled for today."
        )

    count = len(
        appointments
    )

    appointment_word = (
        "appointment"
        if count == 1
        else "appointments"
    )

    formatted = [
        format_appointment(
            appointment
        )
        for appointment in appointments
    ]

    return (
        f"There {'is' if count == 1 else 'are'} "
        f"{count} {appointment_word} "
        f"scheduled for today.\n\n"
        + "\n".join(
            formatted
        )
    )


# ==========================================================
# CLINIC SUMMARY
# ==========================================================


async def handle_clinic_summary(
    clinic_id: str,
) -> str:
    print(
        "[Workflow] Collecting summary data..."
    )

    active_patient_count = (
        await get_active_patient_count.ainvoke(
            {
                "clinic_id": clinic_id,
            }
        )
    )

    today_appointments = (
        await get_today_appointments.ainvoke(
            {
                "clinic_id": clinic_id,
            }
        )
    )

    appointments = parse_list_data(
        today_appointments
    )

    summary = []

    summary.append(
        format_patient_count(
            active_patient_count
        )
    )

    if appointments:
        count = len(
            appointments
        )

        formatted = [
            format_appointment(
                appointment
            )
            for appointment in appointments
        ]

        summary.append(
            f"Today's appointments "
            f"({count}):\n"
            + "\n".join(
                formatted
            )
        )

    else:
        summary.append(
            "There are no appointments "
            "scheduled for today."
        )

    return "\n\n".join(
        summary
    )


# ==========================================================
# PATIENT SEARCH
# ==========================================================


async def handle_patient_search(
    message: str,
    clinic_id: str,
) -> str:
    patient_name = (
        extract_patient_name(
            message
        )
    )

    if not patient_name:
        return (
            "Please provide the patient's "
            "name so I can search for them."
        )

    print(
        f"[Workflow] Searching patient: "
        f"{patient_name!r}"
    )

    search_result = (
        await search_patients.ainvoke(
            {
                "clinic_id": clinic_id,
                "search_term": patient_name,
            }
        )
    )

    print(
        f"[Workflow] Patient search result: "
        f"{search_result!r}"
    )

    patients = parse_list_data(
        search_result
    )

    if not patients:
        return (
            f"No patient matching "
            f"'{patient_name}' was found."
        )

    # ------------------------------------------------------
    # One patient found
    # ------------------------------------------------------

    if len(patients) == 1:
        patient = patients[0]

        found_name = get_patient_name(
            patient
        )

        patient_id = get_patient_id(
            patient
        )

        if not patient_id:
            return (
                f"Patient found: "
                f"{found_name}."
            )

        print(
            f"[Workflow] Getting appointments "
            f"for patient: {patient_id}"
        )

        appointment_result = (
            await get_patient_appointments.ainvoke(
                {
                    "clinic_id": clinic_id,
                    "patient_id": str(
                        patient_id
                    ),
                }
            )
        )

        print(
            f"[Workflow] Patient appointment result: "
            f"{appointment_result!r}"
        )

        appointments = parse_list_data(
            appointment_result
        )

        response = (
            f"Patient found: "
            f"{found_name}."
        )

        if appointments:
            count = len(
                appointments
            )

            appointment_word = (
                "appointment"
                if count == 1
                else "appointments"
            )

            formatted = [
                format_appointment(
                    appointment,
                    patient_name=found_name,
                )
                for appointment in appointments
            ]

            response += (
                f"\n\n{count} "
                f"{appointment_word} found:\n"
                + "\n".join(
                    formatted
                )
            )

        else:
            response += (
                "\n\nNo appointments were "
                "found for this patient."
            )

        return response

    # ------------------------------------------------------
    # Multiple patients found
    # ------------------------------------------------------

    patient_lines = []

    for patient in patients:
        name = get_patient_name(
            patient
        )

        patient_lines.append(
            f"- {name}"
        )

    count = len(
        patients
    )

    return (
        f"I found {count} patients "
        f"matching '{patient_name}':\n\n"
        + "\n".join(
            patient_lines
        )
        + "\n\nPlease provide the full "
          "patient name to view their appointments."
    )


# ==========================================================
# PATIENT-SPECIFIC APPOINTMENTS
# ==========================================================


async def handle_patient_appointments(
    message: str,
    clinic_id: str,
) -> str:
    """
    Find a patient and return only that patient's appointments.

    This handler intentionally performs:

        patient search
            ↓
        patient ID extraction
            ↓
        patient appointment lookup

    so the AI does not accidentally return the entire
    clinic's appointment list.
    """

    patient_name = (
        extract_patient_name(
            message
        )
    )

    if not patient_name:
        return (
            "Please provide the patient's "
            "name so I can find their appointments."
        )

    print(
        f"[Workflow] Finding patient for appointments: "
        f"{patient_name!r}"
    )

    search_result = (
        await search_patients.ainvoke(
            {
                "clinic_id": clinic_id,
                "search_term": patient_name,
            }
        )
    )

    print(
        f"[Workflow] Patient search result: "
        f"{search_result!r}"
    )

    patients = parse_list_data(
        search_result
    )

    if not patients:
        return (
            f"No patient matching "
            f"'{patient_name}' was found."
        )

    # ------------------------------------------------------
    # Multiple patients
    # ------------------------------------------------------

    if len(patients) > 1:
        patient_lines = []

        for patient in patients:
            name = get_patient_name(
                patient
            )

            patient_lines.append(
                f"- {name}"
            )

        count = len(
            patients
        )

        return (
            f"I found {count} patients "
            f"matching '{patient_name}':\n\n"
            + "\n".join(
                patient_lines
            )
            + "\n\nPlease provide the full "
              "patient name."
        )

    # ------------------------------------------------------
    # One patient
    # ------------------------------------------------------

    patient = patients[0]

    found_name = get_patient_name(
        patient
    )

    patient_id = get_patient_id(
        patient
    )

    if not patient_id:
        return (
            f"Patient found: "
            f"{found_name}, but their patient ID "
            f"could not be retrieved."
        )

    print(
        f"[Workflow] Getting appointments "
        f"for patient: {patient_id}"
    )

    appointment_result = (
        await get_patient_appointments.ainvoke(
            {
                "clinic_id": clinic_id,
                "patient_id": str(
                    patient_id
                ),
            }
        )
    )

    print(
        f"[Workflow] Patient appointment result: "
        f"{appointment_result!r}"
    )

    appointments = parse_list_data(
        appointment_result
    )

    if not appointments:
        return (
            f"{found_name} has no appointments "
            f"recorded in the clinic."
        )

    count = len(
        appointments
    )

    appointment_word = (
        "appointment"
        if count == 1
        else "appointments"
    )

    formatted = [
        format_appointment(
            appointment,
            patient_name=found_name,
        )
        for appointment in appointments
    ]

    return (
        f"{found_name} has "
        f"{count} {appointment_word}:\n\n"
        + "\n".join(
            formatted
        )
    )


# ==========================================================
# LANGGRAPH NODE
# ==========================================================


async def process_request(
    state: AgentState,
) -> dict:
    message = (
        state["messages"][-1].content
    )

    clinic_id = str(
        state["clinic_id"]
    )

    intent = detect_intent(
        message
    )

    print(
        f"[Agent] Detected intent: "
        f"{intent}"
    )

    if intent == "active_patient_count":
        response = (
            await handle_active_patient_count(
                clinic_id
            )
        )

    elif intent == "today_appointments":
        response = (
            await handle_today_appointments(
                clinic_id
            )
        )

    elif intent == "clinic_summary":
        response = (
            await handle_clinic_summary(
                clinic_id
            )
        )

    elif intent == "patient_search":
        response = (
            await handle_patient_search(
                message,
                clinic_id,
            )
        )

    elif intent == "patient_appointments":
        response = (
            await handle_patient_appointments(
                message,
                clinic_id,
            )
        )

    else:
        response = (
            "I can help with clinic "
            "operations such as active "
            "patients, today's appointments, "
            "clinic summaries, and patient "
            "appointments."
        )

    print(
        f"[Agent] Final response: "
        f"{response!r}"
    )

    return {
        "messages": [
            HumanMessage(
                content=response
            )
        ]
    }


# ==========================================================
# LANGGRAPH
# ==========================================================


workflow = StateGraph(
    AgentState
)

workflow.add_node(
    "process_request",
    process_request,
)

workflow.add_edge(
    START,
    "process_request",
)

workflow.add_edge(
    "process_request",
    END,
)

agent_graph = workflow.compile()


# ==========================================================
# PUBLIC AGENT FUNCTION
# ==========================================================


async def run_agent(
    message: str,
    clinic_id: str,
) -> str:
    print(
        f"[Agent] User request: "
        f"{message!r}"
    )

    result = await agent_graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=message
                )
            ],
            "clinic_id": clinic_id,
            "clinic_data": {},
        }
    )

    final_message = result[
        "messages"
    ][-1]

    return final_message.content