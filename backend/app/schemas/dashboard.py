from pydantic import BaseModel


class DashboardResponse(BaseModel):
    clinic_name: str

    total_doctors: int
    total_patients: int
    total_appointments: int

    today_appointments: int

    scheduled_appointments: int
    confirmed_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int