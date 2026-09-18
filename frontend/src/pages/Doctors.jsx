import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Doctors() {
  const navigate = useNavigate();

  const [doctors, setDoctors] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [search, setSearch] =
    useState("");


  useEffect(() => {
    const loadDoctors = async () => {
      try {
        setLoading(true);
        setError("");

        const response =
          await apiClient.get(
            "/doctors",
            {
              params: {
                search:
                  search.trim() || undefined,
              },
            }
          );

        setDoctors(
          response.data.doctors || []
        );

      } catch (err) {
        console.error(
          "Doctors error:",
          err
        );

        if (
          err.response?.status === 401
        ) {
          navigate("/login");
          return;
        }

        setError(
          "Unable to load doctors."
        );

      } finally {
        setLoading(false);
      }
    };


    loadDoctors();

  }, [navigate, search]);


  const getInitials = (name) => {
    if (!name) {
      return "D";
    }

    const parts =
      name.trim().split(/\s+/);

    if (parts.length === 1) {
      return parts[0]
        .charAt(0)
        .toUpperCase();
    }

    return (
      parts[0].charAt(0) +
      parts[parts.length - 1].charAt(0)
    ).toUpperCase();
  };


  return (
    <div className="page">

      {/* ====================================================
          PAGE HEADER
          ==================================================== */}

      <div className="page-heading">

        <div>

          <h2>
            Doctors
          </h2>

          <p>
            Manage doctors working at your clinic.
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
            placeholder="Search by name, specialization or license..."
          />

        </div>


        <div className="patient-count">

          {loading
            ? "Loading..."
            : `${doctors.length} doctor${
                doctors.length === 1
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
            Loading doctors...
          </div>

        </div>

      ) : doctors.length === 0 ? (

        <div className="empty-page-card">

          <div className="empty-icon">
            Doctors
          </div>

          <h3>
            No Doctors Found
          </h3>

          <p>
            {search
              ? "No doctors match your search."
              : "There are no active doctors registered in this clinic."}
          </p>

        </div>

      ) : (

        /* ==================================================
           DOCTOR TABLE
           ================================================== */

        <div className="patients-table-card">

          <div className="patients-table-wrapper">

            <table className="patients-table">

              <thead>

                <tr>

                  <th>
                    Doctor
                  </th>

                  <th>
                    Specialization
                  </th>

                  <th>
                    License Number
                  </th>

                  <th>
                    Phone
                  </th>

                  <th>
                    Bio
                  </th>

                  <th>
                    Status
                  </th>

                </tr>

              </thead>


              <tbody>

                {doctors.map(
                  (doctor) => (
                    <tr
                      key={doctor.id}
                    >

                      <td>

                        <div className="patient-name-cell">

                          <div className="patient-avatar">
                            {getInitials(
                              doctor.name
                            )}
                          </div>

                          <div>

                            <strong>
                              {doctor.name}
                            </strong>

                            <span>
                              Doctor ID:{" "}
                              {doctor.id.slice(
                                0,
                                8
                              )}
                            </span>

                          </div>

                        </div>

                      </td>


                      <td>
                        {doctor.specialization}
                      </td>


                      <td>
                        {doctor.license_number}
                      </td>


                      <td>
                        {doctor.phone || "—"}
                      </td>


                      <td>
                        {doctor.bio || "—"}
                      </td>


                      <td>

                        <span
                          className={
                            doctor.is_active
                              ? "status-badge active"
                              : "status-badge inactive"
                          }
                        >
                          {doctor.is_active
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


export default Doctors;