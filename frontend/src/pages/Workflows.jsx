import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Workflows() {
  const navigate = useNavigate();

  const [workflows, setWorkflows] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [running, setRunning] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const [editingId, setEditingId] =
    useState(null);

  const [showCreateForm, setShowCreateForm] =
    useState(false);


  const [form, setForm] =
    useState({
      workflow_name: "daily_clinic_summary",
      display_name: "Daily Clinic Summary",
      description:
        "Generate the clinic's daily operational summary.",
      is_enabled: true,
      schedule_type: "daily",
      schedule_hour: "08",
      schedule_minute: "00",
    });


  /* ==========================================================
     LOAD WORKFLOWS
     ========================================================== */

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      setError("");

      const response =
        await apiClient.get(
          "/workflows/configurations"
        );

      setWorkflows(
        response.data || []
      );

    } catch (err) {
      console.error(
        "Workflow loading error:",
        err
      );

      if (
        err.response?.status === 401
      ) {
        navigate("/login");
        return;
      }

      setError(
        "Unable to load workflow configurations."
      );

    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    loadWorkflows();
  }, []);


  /* ==========================================================
     FORM HELPERS
     ========================================================== */

  const openCreateForm = () => {
    setError("");
    setSuccess("");

    setEditingId(null);

    setForm({
      workflow_name:
        "daily_clinic_summary",

      display_name:
        "Daily Clinic Summary",

      description:
        "Generate the clinic's daily operational summary.",

      is_enabled: true,

      schedule_type:
        "daily",

      schedule_hour:
        "08",

      schedule_minute:
        "00",
    });

    setShowCreateForm(true);
  };


  const openEditForm = (
    workflow
  ) => {
    setError("");
    setSuccess("");

    setShowCreateForm(false);

    setEditingId(
      workflow.id
    );

    setForm({
      workflow_name:
        workflow.workflow_name,

      display_name:
        workflow.display_name,

      description:
        workflow.description || "",

      is_enabled:
        workflow.is_enabled,

      schedule_type:
        workflow.schedule_type,

      schedule_hour:
        workflow.schedule_hour !== null
          ? String(
              workflow.schedule_hour
            ).padStart(2, "0")
          : "08",

      schedule_minute:
        workflow.schedule_minute !== null
          ? String(
              workflow.schedule_minute
            ).padStart(2, "0")
          : "00",
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };


  const closeForm = () => {
    setEditingId(null);
    setShowCreateForm(false);

    setError("");
  };


  const handleFormChange = (
    event
  ) => {
    const {
      name,
      value,
      type,
      checked,
    } = event.target;

    setForm(
      (previous) => ({
        ...previous,

        [name]:
          type === "checkbox"
            ? checked
            : value,
      })
    );
  };


  /* ==========================================================
     SAVE WORKFLOW
     ========================================================== */

  const handleSave = async (
    event
  ) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSaving(true);


    try {
      const payload = {
        display_name:
          form.display_name.trim(),

        description:
          form.description.trim() ||
          null,

        is_enabled:
          form.is_enabled,

        schedule_type:
          form.schedule_type,
      };


      if (
        form.schedule_type ===
        "daily"
      ) {
        payload.schedule_hour =
          Number(
            form.schedule_hour
          );

        payload.schedule_minute =
          Number(
            form.schedule_minute
          );
      } else {
        payload.schedule_hour =
          null;

        payload.schedule_minute =
          null;
      }


      if (editingId) {

        await apiClient.put(
          `/workflows/configurations/${editingId}`,
          payload
        );

        setSuccess(
          "Workflow configuration updated successfully."
        );

      } else {

        await apiClient.post(
          "/workflows/configurations",
          {
            workflow_name:
              form.workflow_name.trim(),

            ...payload,
          }
        );

        setSuccess(
          "Workflow configuration created successfully."
        );
      }


      closeForm();

      await loadWorkflows();

    } catch (err) {
      console.error(
        "Workflow save error:",
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
          "Unable to save workflow configuration."
        );
      }

    } finally {
      setSaving(false);
    }
  };


  /* ==========================================================
     RUN DAILY SUMMARY
     ========================================================== */

  const handleRunNow = async () => {
    setError("");
    setSuccess("");
    setRunning(true);


    try {
      const response =
        await apiClient.post(
          "/workflows/daily-summary"
        );

      setSuccess(
        response.data?.response ||
        "Daily clinic summary completed successfully."
      );

      /*
       * Give the backend a moment to
       * finish committing the execution
       * before refreshing the page data.
       */

      await new Promise(
        (resolve) =>
          setTimeout(
            resolve,
            500
          )
      );

    } catch (err) {
      console.error(
        "Workflow execution error:",
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
          "Workflow execution failed."
        );
      }

    } finally {
      setRunning(false);
    }
  };


  /* ==========================================================
     FORMATTERS
     ========================================================== */

  const formatSchedule = (
    workflow
  ) => {
    if (
      workflow.schedule_type ===
      "manual"
    ) {
      return "Manual";
    }


    if (
      workflow.schedule_hour ===
        null ||
      workflow.schedule_minute ===
        null
    ) {
      return "Daily";
    }


    const hour =
      workflow.schedule_hour;

    const minute =
      String(
        workflow.schedule_minute
      ).padStart(2, "0");


    const period =
      hour >= 12
        ? "PM"
        : "AM";

    const displayHour =
      hour % 12 || 12;


    return `Daily at ${displayHour}:${minute} ${period}`;
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
            Workflows
          </h2>

          <p>
            Configure and automate clinic workflows.
          </p>

        </div>


        <button
          className="primary-button"
          onClick={
            openCreateForm
          }
        >
          + New Workflow
        </button>

      </div>


      {/* ====================================================
          SUCCESS / ERROR
          ==================================================== */}

      {success && (
        <div className="page-success workflow-message">
          {success}
        </div>
      )}


      {error && (
        <div className="page-error workflow-message">
          {error}
        </div>
      )}


      {/* ====================================================
          CREATE / EDIT FORM
          ==================================================== */}

      {(showCreateForm ||
        editingId) && (

        <div className="workflow-form-card">

          <div className="workflow-form-header">

            <div>

              <h3>
                {editingId
                  ? "Edit Workflow"
                  : "Create Workflow"}
              </h3>

              <p>
                Configure how this clinic workflow should operate.
              </p>

            </div>

          </div>


          <form
            className="workflow-form"
            onSubmit={
              handleSave
            }
          >

            <div className="workflow-form-grid">

              {/* ==========================================
                  WORKFLOW NAME
                  ========================================== */}

              <div className="form-group">

                <label>
                  Workflow Name
                </label>

                <input
                  type="text"
                  value={
                    form.workflow_name
                  }
                  disabled
                />

                <small className="field-help">
                  Internal workflow identifier.
                </small>

              </div>


              {/* ==========================================
                  DISPLAY NAME
                  ========================================== */}

              <div className="form-group">

                <label htmlFor="display_name">
                  Display Name
                </label>

                <input
                  id="display_name"
                  name="display_name"
                  type="text"
                  value={
                    form.display_name
                  }
                  onChange={
                    handleFormChange
                  }
                  required
                  minLength={2}
                  maxLength={150}
                />

              </div>


              {/* ==========================================
                  DESCRIPTION
                  ========================================== */}

              <div className="form-group workflow-description-group">

                <label htmlFor="description">
                  Description
                </label>

                <textarea
                  id="description"
                  name="description"
                  value={
                    form.description
                  }
                  onChange={
                    handleFormChange
                  }
                  maxLength={1000}
                  rows="3"
                  placeholder="Describe what this workflow does..."
                />

              </div>


              {/* ==========================================
                  SCHEDULE TYPE
                  ========================================== */}

              <div className="form-group">

                <label htmlFor="schedule_type">
                  Schedule
                </label>

                <select
                  id="schedule_type"
                  name="schedule_type"
                  value={
                    form.schedule_type
                  }
                  onChange={
                    handleFormChange
                  }
                >

                  <option value="daily">
                    Daily
                  </option>

                  <option value="manual">
                    Manual
                  </option>

                </select>

              </div>


              {/* ==========================================
                  ENABLED
                  ========================================== */}

              <div className="form-group workflow-toggle-group">

                <label>
                  Workflow Status
                </label>

                <label className="workflow-toggle">

                  <input
                    type="checkbox"
                    name="is_enabled"
                    checked={
                      form.is_enabled
                    }
                    onChange={
                      handleFormChange
                    }
                  />

                  <span className="workflow-toggle-slider"></span>

                  <span className="workflow-toggle-label">

                    {form.is_enabled
                      ? "Enabled"
                      : "Disabled"}

                  </span>

                </label>

              </div>


              {/* ==========================================
                  DAILY TIME
                  ========================================== */}

              {form.schedule_type ===
                "daily" && (

                <>

                  <div className="form-group">

                    <label htmlFor="schedule_hour">
                      Hour
                    </label>

                    <select
                      id="schedule_hour"
                      name="schedule_hour"
                      value={
                        form.schedule_hour
                      }
                      onChange={
                        handleFormChange
                      }
                    >

                      {Array.from(
                        {
                          length: 24,
                        },
                        (_, hour) => (
                          <option
                            key={hour}
                            value={String(
                              hour
                            ).padStart(
                              2,
                              "0"
                            )}
                          >
                            {String(
                              hour
                            ).padStart(
                              2,
                              "0"
                            )}
                          </option>
                        )
                      )}

                    </select>

                  </div>


                  <div className="form-group">

                    <label htmlFor="schedule_minute">
                      Minute
                    </label>

                    <select
                      id="schedule_minute"
                      name="schedule_minute"
                      value={
                        form.schedule_minute
                      }
                      onChange={
                        handleFormChange
                      }
                    >

                      {Array.from(
                        {
                          length: 60,
                        },
                        (_, minute) => (
                          <option
                            key={minute}
                            value={String(
                              minute
                            ).padStart(
                              2,
                              "0"
                            )}
                          >
                            {String(
                              minute
                            ).padStart(
                              2,
                              "0"
                            )}
                          </option>
                        )
                      )}

                    </select>

                  </div>

                </>
              )}

            </div>


            {/* ==================================================
                FORM ACTIONS
                ================================================== */}

            <div className="workflow-form-actions">

              <button
                type="button"
                className="secondary-button"
                onClick={
                  closeForm
                }
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
                  ? "Saving..."
                  : editingId
                    ? "Save Changes"
                    : "Create Workflow"}
              </button>

            </div>

          </form>

        </div>
      )}


      {/* ====================================================
          WORKFLOW LIST
          ==================================================== */}

      {loading ? (

        <div className="workflow-loading-card">

          <div className="appointments-loading">
            Loading workflows...
          </div>

        </div>

      ) : workflows.length === 0 ? (

        <div className="empty-page-card">

          <div className="empty-icon">
            Workflows
          </div>

          <h3>
            No Workflows Configured
          </h3>

          <p>
            Create a workflow configuration to automate clinic operations.
          </p>


          <button
            className="primary-button"
            onClick={
              openCreateForm
            }
          >
            Create Daily Summary Workflow
          </button>

        </div>

      ) : (

        <div className="workflow-list">

          {workflows.map(
            (workflow) => (

              <div
                className="workflow-card"
                key={
                  workflow.id
                }
              >

                {/* ========================================
                    WORKFLOW CARD HEADER
                    ======================================== */}

                <div className="workflow-card-header">

                  <div className="workflow-card-title">

                    <div className="workflow-icon">
                      AI
                    </div>

                    <div>

                      <h3>
                        {
                          workflow.display_name
                        }
                      </h3>

                      <span>
                        {
                          workflow.workflow_name
                        }
                      </span>

                    </div>

                  </div>


                  <span
                    className={
                      workflow.is_enabled
                        ? "workflow-status enabled"
                        : "workflow-status disabled"
                    }
                  >
                    {workflow.is_enabled
                      ? "Enabled"
                      : "Disabled"}
                  </span>

                </div>


                {/* ========================================
                    DESCRIPTION
                    ======================================== */}

                <div className="workflow-description">

                  <p>
                    {workflow.description ||
                      "No description provided."}
                  </p>

                </div>


                {/* ========================================
                    DETAILS
                    ======================================== */}

                <div className="workflow-details">

                  <div className="workflow-detail">

                    <span>
                      Schedule
                    </span>

                    <strong>
                      {formatSchedule(
                        workflow
                      )}
                    </strong>

                  </div>


                  <div className="workflow-detail">

                    <span>
                      Type
                    </span>

                    <strong>
                      {workflow.schedule_type ===
                      "daily"
                        ? "Automatic"
                        : "Manual"}
                    </strong>

                  </div>


                  <div className="workflow-detail">

                    <span>
                      Workflow
                    </span>

                    <strong>
                      Daily Clinic Summary
                    </strong>

                  </div>

                </div>


                {/* ========================================
                    ACTIONS
                    ======================================== */}

                <div className="workflow-card-actions">

                  <button
                    className="secondary-button"
                    onClick={() =>
                      openEditForm(
                        workflow
                      )
                    }
                  >
                    Edit
                  </button>


                  {workflow.workflow_name ===
                    "daily_clinic_summary" && (

                    <button
                      className="primary-button"
                      onClick={
                        handleRunNow
                      }
                      disabled={
                        running
                      }
                    >
                      {running
                        ? "Running..."
                        : "Run Now"}
                    </button>

                  )}

                </div>

              </div>

            )
          )}

        </div>

      )}

    </div>
  );
}


export default Workflows;