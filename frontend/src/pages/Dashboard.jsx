import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Dashboard() {
  const navigate = useNavigate();

  const [dashboard, setDashboard] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response =
          await apiClient.get(
            "/dashboard"
          );

        setDashboard(
          response.data
        );

      } catch (err) {
        console.error(
          "Dashboard error:",
          err
        );

        if (
          err.response?.status === 401
        ) {
          navigate("/login");
          return;
        }

        setError(
          "Unable to load dashboard."
        );

      } finally {
        setLoading(false);
      }
    };


    loadDashboard();

  }, [navigate]);


  if (loading) {
    return (
      <div className="page-loading">
        Loading dashboard...
      </div>
    );
  }


  return (
    <div className="page">

      {/* ====================================================
          PAGE HEADER
          ==================================================== */}

      <div className="page-heading">

        <div>

          <h2>
            Dashboard
          </h2>

          <p>
            Overview of your clinic operations.
          </p>

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
          STATISTICS
          ==================================================== */}

      <section className="stats-grid">

        <div className="stat-card">

          <span>
            Total Doctors
          </span>

          <strong>
            {dashboard?.total_doctors ?? 0}
          </strong>

          <small>
            Registered doctors
          </small>

        </div>


        <div className="stat-card">

          <span>
            Total Patients
          </span>

          <strong>
            {dashboard?.total_patients ?? 0}
          </strong>

          <small>
            Active clinic patients
          </small>

        </div>


        <div className="stat-card">

          <span>
            Total Appointments
          </span>

          <strong>
            {dashboard?.total_appointments ?? 0}
          </strong>

          <small>
            All appointments
          </small>

        </div>


        <div className="stat-card">

          <span>
            Today's Appointments
          </span>

          <strong>
            {dashboard?.today_appointments ?? 0}
          </strong>

          <small>
            Scheduled for today
          </small>

        </div>

      </section>


      {/* ====================================================
          LOWER DASHBOARD
          ==================================================== */}

      <section className="dashboard-grid">


        {/* APPOINTMENT OVERVIEW */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <h3>
                Appointment Overview
              </h3>

              <p>
                Current appointment status counts.
              </p>

            </div>

          </div>


          <div className="appointment-summary">

            <div>

              <span>
                Scheduled
              </span>

              <strong>
                {dashboard?.scheduled_appointments ?? 0}
              </strong>

            </div>


            <div>

              <span>
                Confirmed
              </span>

              <strong>
                {dashboard?.confirmed_appointments ?? 0}
              </strong>

            </div>


            <div>

              <span>
                Completed
              </span>

              <strong>
                {dashboard?.completed_appointments ?? 0}
              </strong>

            </div>


            <div>

              <span>
                Cancelled
              </span>

              <strong>
                {dashboard?.cancelled_appointments ?? 0}
              </strong>

            </div>


            <div>

              <span>
                No-show
              </span>

              <strong>
                {dashboard?.no_show_appointments ?? 0}
              </strong>

            </div>

          </div>

        </div>


        {/* AI OPERATIONS */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <h3>
                AI Operations
              </h3>

              <p>
                Generate operational insights using ClinicFlow AI.
              </p>

            </div>

          </div>


          <div className="ai-card-content">

            <div className="ai-symbol">
              AI
            </div>


            <p>
              Use ClinicFlow AI to generate
              operational summaries and automate
              clinic workflows.
            </p>


            <button
              className="primary-button"
              onClick={() =>
                navigate("/ai")
              }
            >
              Open AI Assistant
            </button>

          </div>

        </div>


      </section>

    </div>
  );
}


export default Dashboard;