import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Appointments() {
  const navigate = useNavigate();


  const [appointments, setAppointments] =
    useState([]);

  const [doctors, setDoctors] =
    useState([]);

  const [patients, setPatients] =
    useState([]);


  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const [search, setSearch] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("all");


  const [showForm, setShowForm] =
    useState(false);

  const [saving, setSaving] =
    useState(false);


  const [form, setForm] =
    useState({
      doctor_id: "",
      patient_id: "",
      scheduled_at: "",
      reason: "",
      notes: "",
    });


  /* ==========================================================
     LOAD DATA
     ========================================================== */

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [
        appointmentsResponse,
        doctorsResponse,
        patientsResponse,
      ] = await Promise.all([
        apiClient.get(
          "/appointments"
        ),

        apiClient.get(
          "/doctors"
        ),

        apiClient.get(
          "/patients"
        ),
      ]);


      setAppointments(
        appointmentsResponse.data || []
      );

      setDoctors(
        doctorsResponse.data.doctors || []
      );

      setPatients(
        patientsResponse.data.patients || []
      );

    } catch (err) {
      console.error(
        "Appointments loading error:",
        err
      );

      if (
        err.response?.status === 401
      ) {
        navigate("/login");
        return;
      }

      setError(
        "Unable to load appointment data."
      );

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadData();
  }, []);


  /* ==========================================================
     LOOKUP HELPERS
     ========================================================== */

  const doctorMap = useMemo(() => {
    const map = {};

    doctors.forEach(
      (doctor) => {
        map[doctor.id] =
          doctor.name;
      }
    );

    return map;
  }, [doctors]);


  const patientMap = useMemo(() => {
    const map = {};

    patients.forEach(
      (patient) => {
        map[patient.id] =
          [
            patient.first_name,
            patient.last_name,
          ]
            .filter(Boolean)
            .join(" ");
      }
    );

    return map;
  }, [patients]);


  /* ==========================================================
     FILTER APPOINTMENTS
     ========================================================== */

  const filteredAppointments =
    useMemo(() => {
      const searchValue =
        search.trim().toLowerCase();

      return appointments.filter(
        (appointment) => {

          const doctorName =
            doctorMap[
              appointment.doctor_id
            ] || "";

          const patientName =
            patientMap[
              appointment.patient_id
            ] || "";

          const reason =
            appointment.reason || "";

          const status =
            appointment.status || "";


          const matchesSearch =
            !searchValue ||
            doctorName
              .toLowerCase()
              .includes(searchValue) ||
            patientName
              .toLowerCase()
              .includes(searchValue) ||
            reason
              .toLowerCase()
              .includes(searchValue);


          const matchesStatus =
            statusFilter === "all" ||
            status === statusFilter;


          return (
            matchesSearch &&
            matchesStatus
          );
        }
      );
    }, [
      appointments,
      doctors,
      patients,
      doctorMap,
      patientMap,
      search,
      statusFilter,
    ]);


  /* ==========================================================
     FORM HANDLING
     ========================================================== */

  const handleFormChange = (
    event
  ) => {
    const {
      name,
      value,
    } = event.target;

    setForm(
      (previous) => ({
        ...previous,
        [name]: value,
      })
    );
  };


  const resetForm = () => {
    setForm({
      doctor_id: "",
      patient_id: "",
      scheduled_at: "",
      reason: "",
      notes: "",
    });

    setShowForm(false);
  };


  const handleCreateAppointment =
    async (event) => {
      event.preventDefault();

      setError("");
      setSuccess("");
      setSaving(true);


      try {
        /*
         * datetime-local does not include
         * timezone information.
         *
         * Converting it through Date()
         * produces an ISO timestamp that
         * FastAPI can parse correctly.
         */

        const scheduledAt =
          new Date(
            form.scheduled_at
          ).toISOString();


        await apiClient.post(
          "/appointments",
          {
            doctor_id:
              form.doctor_id,

            patient_id:
              form.patient_id,

            scheduled_at:
              scheduledAt,

            reason:
              form.reason.trim() ||
              null,

            notes:
              form.notes.trim() ||
              null,
          }
        );


        setSuccess(
          "Appointment created successfully."
        );


        resetForm();

        await loadData();

      } catch (err) {
        console.error(
          "Appointment creation error:",
          err
        );


        if (
          err.response?.status === 401
        ) {
          navigate("/login");
          return;
        }


        const detail =
          err.response?.data?.detail;


        if (
          typeof detail === "string"
        ) {
          setError(detail);
        } else {
          setError(
            "Unable to create appointment."
          );
        }

      } finally {
        setSaving(false);
      }
    };


  /* ==========================================================
     FORMATTERS
     ========================================================== */

  const formatDateTime = (
    dateValue
  ) => {
    if (!dateValue) {
      return "—";
    }

    return new Date(
      dateValue
    ).toLocaleString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  };


  const formatStatus = (
    status
  ) => {
    if (!status) {
      return "Unknown";
    }

    return status
      .replaceAll("_", " ")
      .replace(
        /\b\w/g,
        (character) =>
          character.toUpperCase()
      );
  };


  const getStatusClass = (
    status
  ) => {
    if (
      status === "confirmed"
    ) {
      return "appointment-status confirmed";
    }

    if (
      status === "completed"
    ) {
      return "appointment-status completed";
    }

    if (
      status === "cancelled"
    ) {
      return "appointment-status cancelled";
    }

    if (
      status === "no_show"
    ) {
      return "appointment-status no-show";
    }

    return "appointment-status scheduled";
  };


  /* ==========================================================
     RENDER
     ========================================================== */

  return (
    <div className="page">

      {/* ====================================================
          HEADER
          ==================================================== */}

      <div className="page-heading">

        <div>

          <h2>
            Appointments
          </h2>

          <p>
            Schedule and manage clinic appointments.
          </p>

        </div>


        <button
          className="primary-button appointment-add-button"
          onClick={() => {
            setError("");
            setSuccess("");
            setShowForm(true);
          }}
        >
          + New Appointment
        </button>

      </div>


      {/* ====================================================
          SUCCESS / ERROR
          ==================================================== */}

      {success && (
        <div className="page-success">
          {success}
        </div>
      )}


      {error && (
        <div className="page-error">
          {error}
        </div>
      )}


      {/* ====================================================
          CREATE APPOINTMENT FORM
          ==================================================== */}

      {showForm && (

        <div className="appointment-form-card">

          <div className="appointment-form-header">

            <div>

              <h3>
                Create Appointment
              </h3>

              <p>
                Schedule a new appointment for a patient.
              </p>

            </div>

          </div>


          <form
            className="appointment-form"
            onSubmit={
              handleCreateAppointment
            }
          >

            <div className="appointment-form-grid">

              <div className="form-group">

                <label htmlFor="patient_id">
                  Patient
                </label>

                <select
                  id="patient_id"
                  name="patient_id"
                  value={
                    form.patient_id
                  }
                  onChange={
                    handleFormChange
                  }
                  required
                >

                  <option value="">
                    Select patient
                  </option>

                  {patients.map(
                    (patient) => (
                      <option
                        key={patient.id}
                        value={patient.id}
                      >
                        {[
                          patient.first_name,
                          patient.last_name,
                        ]
                          .filter(Boolean)
                          .join(" ")}
                      </option>
                    )
                  )}

                </select>

              </div>


              <div className="form-group">

                <label htmlFor="doctor_id">
                  Doctor
                </label>

                <select
                  id="doctor_id"
                  name="doctor_id"
                  value={
                    form.doctor_id
                  }
                  onChange={
                    handleFormChange
                  }
                  required
                >

                  <option value="">
                    Select doctor
                  </option>

                  {doctors.map(
                    (doctor) => (
                      <option
                        key={doctor.id}
                        value={doctor.id}
                      >
                        {doctor.name}
                        {" — "}
                        {doctor.specialization}
                      </option>
                    )
                  )}

                </select>

              </div>


              <div className="form-group">

                <label htmlFor="scheduled_at">
                  Date & Time
                </label>

                <input
                  id="scheduled_at"
                  name="scheduled_at"
                  type="datetime-local"
                  value={
                    form.scheduled_at
                  }
                  onChange={
                    handleFormChange
                  }
                  required
                />

              </div>


              <div className="form-group">

                <label htmlFor="reason">
                  Reason
                </label>

                <input
                  id="reason"
                  name="reason"
                  type="text"
                  value={
                    form.reason
                  }
                  onChange={
                    handleFormChange
                  }
                  placeholder="e.g. General consultation"
                  maxLength={255}
                />

              </div>


              <div className="form-group appointment-notes-group">

                <label htmlFor="notes">
                  Notes
                </label>

                <textarea
                  id="notes"
                  name="notes"
                  value={
                    form.notes
                  }
                  onChange={
                    handleFormChange
                  }
                  placeholder="Additional appointment notes..."
                  rows="4"
                />

              </div>

            </div>


            <div className="appointment-form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={resetForm}
                disabled={saving}
              >
                Cancel
              </button>


              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving
                  ? "Creating..."
                  : "Create Appointment"}
              </button>

            </div>

          </form>

        </div>

      )}


      {/* ====================================================
          SEARCH / FILTER
          ==================================================== */}

      <div className="appointments-toolbar">

        <div className="appointment-search">

          <input
            type="text"
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search by patient, doctor or reason..."
          />

        </div>


        <select
          className="appointment-status-filter"
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value
            )
          }
        >

          <option value="all">
            All statuses
          </option>

          <option value="scheduled">
            Scheduled
          </option>

          <option value="confirmed">
            Confirmed
          </option>

          <option value="completed">
            Completed
          </option>

          <option value="cancelled">
            Cancelled
          </option>

          <option value="no_show">
            No-show
          </option>

        </select>


        <div className="appointment-count">

          {loading
            ? "Loading..."
            : `${filteredAppointments.length} appointment${
                filteredAppointments.length === 1
                  ? ""
                  : "s"
              }`}

        </div>

      </div>


      {/* ====================================================
          APPOINTMENT LIST
          ==================================================== */}

      {loading ? (

        <div className="appointments-table-card">

          <div className="appointments-loading">
            Loading appointments...
          </div>

        </div>

      ) : filteredAppointments.length === 0 ? (

        <div className="empty-page-card">

          <div className="empty-icon">
            Appointments
          </div>

          <h3>
            No Appointments Found
          </h3>

          <p>
            {search ||
            statusFilter !== "all"
              ? "No appointments match your current filters."
              : "There are no appointments scheduled for this clinic yet."}
          </p>


          {!search &&
            statusFilter ===
              "all" && (
              <button
                className="primary-button"
                onClick={() => {
                  setError("");
                  setSuccess("");
                  setShowForm(true);
                }}
              >
                Create First Appointment
              </button>
            )}

        </div>

      ) : (

        <div className="appointments-table-card">

          <div className="appointments-table-wrapper">

            <table className="appointments-table">

              <thead>

                <tr>

                  <th>
                    Patient
                  </th>

                  <th>
                    Doctor
                  </th>

                  <th>
                    Date & Time
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Reason
                  </th>

                </tr>

              </thead>


              <tbody>

                {filteredAppointments.map(
                  (appointment) => (
                    <tr
                      key={
                        appointment.id
                      }
                    >

                      <td>

                        <strong>
                          {patientMap[
                            appointment.patient_id
                          ] ||
                            "Unknown patient"}
                        </strong>

                      </td>


                      <td>

                        <strong>
                          {doctorMap[
                            appointment.doctor_id
                          ] ||
                            "Unknown doctor"}
                        </strong>

                      </td>


                      <td>
                        {formatDateTime(
                          appointment.scheduled_at
                        )}
                      </td>


                      <td>

                        <span
                          className={getStatusClass(
                            appointment.status
                          )}
                        >
                          {formatStatus(
                            appointment.status
                          )}
                        </span>

                      </td>


                      <td>
                        {appointment.reason ||
                          "—"}
                      </td>

                    </tr>
                  )
                )}

              </tbody>

            </table>

          </div>

        </div>

      )}

    </div>
  );
}


export default Appointments;