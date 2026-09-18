import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Patients() {
  const navigate = useNavigate();

  const [patients, setPatients] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [search, setSearch] =
    useState("");


  useEffect(() => {
    const loadPatients = async () => {
      try {
        setLoading(true);
        setError("");

        const response =
          await apiClient.get(
            "/patients",
            {
              params: {
                search:
                  search.trim() || undefined,
              },
            }
          );

        setPatients(
          response.data.patients || []
        );

      } catch (err) {
        console.error(
          "Patients error:",
          err
        );

        if (
          err.response?.status === 401
        ) {
          navigate("/login");
          return;
        }

        setError(
          "Unable to load patients."
        );

      } finally {
        setLoading(false);
      }
    };


    loadPatients();

  }, [navigate, search]);


  const formatDate = (dateValue) => {
    if (!dateValue) {
      return "—";
    }

    return new Date(
      `${dateValue}T00:00:00`
    ).toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  };


  const getFullName = (patient) => {
    return [
      patient.first_name,
      patient.last_name,
    ]
      .filter(Boolean)
      .join(" ");
  };


  const getInitials = (patient) => {
    const first =
      patient.first_name?.charAt(0) || "";

    const last =
      patient.last_name?.charAt(0) || "";

    const initials =
      `${first}${last}`.toUpperCase();

    return initials || "P";
  };


  return (
    <div className="page">

      {/* ====================================================
          PAGE HEADER
          ==================================================== */}

      <div className="page-heading">

        <div>

          <h2>
            Patients
          </h2>

          <p>
            Manage patients registered in your clinic.
          </p>

        </div>

      </div>


      {/* ====================================================
          SEARCH TOOLBAR
          ==================================================== */}

      <div className="patients-toolbar">

        <div className="patient-search">

          <input
            type="text"
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search by name, phone or email..."
          />

        </div>


        <div className="patient-count">

          {loading
            ? "Loading..."
            : `${patients.length} patient${
                patients.length === 1
                  ? ""
                  : "s"
              }`}

        </div>

      </div>


      {/* ====================================================
          ERROR
          ==================================================== */}

      {error && (
        <div className="page-error">
          {error}
        </div>
      )}


      {/* ====================================================
          LOADING
          ==================================================== */}

      {loading ? (

        <div className="patients-table-card">

          <div className="patients-loading">
            Loading patients...
          </div>

        </div>

      ) : patients.length === 0 ? (

        <div className="empty-page-card">

          <div className="empty-icon">
            Patients
          </div>

          <h3>
            No Patients Found
          </h3>

          <p>
            {search
              ? "No patients match your search."
              : "There are no active patients registered in this clinic."}
          </p>

        </div>

      ) : (

        /* ==================================================
           PATIENT TABLE
           ================================================== */

        <div className="patients-table-card">

          <div className="patients-table-wrapper">

            <table className="patients-table">

              <thead>

                <tr>

                  <th>
                    Patient
                  </th>

                  <th>
                    Date of Birth
                  </th>

                  <th>
                    Gender
                  </th>

                  <th>
                    Phone
                  </th>

                  <th>
                    Email
                  </th>

                  <th>
                    Status
                  </th>

                </tr>

              </thead>


              <tbody>

                {patients.map(
                  (patient) => (
                    <tr
                      key={patient.id}
                    >

                      <td>

                        <div className="patient-name-cell">

                          <div className="patient-avatar">
                            {getInitials(
                              patient
                            )}
                          </div>

                          <div>

                            <strong>
                              {getFullName(
                                patient
                              )}
                            </strong>

                            <span>
                              Patient ID:{" "}
                              {patient.id.slice(
                                0,
                                8
                              )}
                            </span>

                          </div>

                        </div>

                      </td>


                      <td>
                        {formatDate(
                          patient.date_of_birth
                        )}
                      </td>


                      <td>
                        {patient.gender || "—"}
                      </td>


                      <td>
                        {patient.phone || "—"}
                      </td>


                      <td>
                        {patient.email || "—"}
                      </td>


                      <td>

                        <span
                          className={
                            patient.is_active
                              ? "status-badge active"
                              : "status-badge inactive"
                          }
                        >
                          {patient.is_active
                            ? "Active"
                            : "Inactive"}
                        </span>

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


export default Patients;
