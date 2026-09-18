import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function WorkflowHistory() {
  const navigate = useNavigate();

  const [history, setHistory] = useState([]);

  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(1);

  const [totalPages, setTotalPages] =
    useState(1);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("");

  const [triggerFilter, setTriggerFilter] =
    useState("");

  const [workflowFilter, setWorkflowFilter] =
    useState("");


  const pageSize = 10;


  /* ==========================================================
     LOAD HISTORY
     ========================================================== */

  const loadHistory = async (
    requestedPage = page
  ) => {
    try {
      setLoading(true);
      setError("");

      const params = {
        page: requestedPage,
        page_size: pageSize,
      };


      if (statusFilter) {
        params.status = statusFilter;
      }


      if (triggerFilter) {
        params.trigger_type =
          triggerFilter;
      }


      if (workflowFilter.trim()) {
        params.workflow_name =
          workflowFilter.trim();
      }


      const response =
        await apiClient.get(
          "/workflows/history",
          {
            params,
          }
        );


      setHistory(
        response.data?.items || []
      );

      setTotal(
        response.data?.total || 0
      );

      setPage(
        response.data?.page ||
          requestedPage
      );

      setTotalPages(
        response.data?.total_pages ||
          1
      );

    } catch (err) {
      console.error(
        "Workflow history loading error:",
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
          "Unable to load workflow history."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  /* ==========================================================
     INITIAL LOAD
     ========================================================== */

  useEffect(() => {
    loadHistory(1);
  }, [
    statusFilter,
    triggerFilter,
    workflowFilter,
  ]);


  /* ==========================================================
     FORMATTERS
     ========================================================== */

  const formatWorkflowName = (
    workflowName
  ) => {
    if (
      workflowName ===
      "daily_clinic_summary"
    ) {
      return "Daily Clinic Summary";
    }


    return workflowName
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };


  const formatStatus = (
    status
  ) => {
    switch (status) {
      case "completed":
        return "Completed";

      case "failed":
        return "Failed";

      case "running":
        return "Running";

      case "pending":
        return "Pending";

      default:
        return status;
    }
  };


  const formatTriggerType = (
    triggerType
  ) => {
    switch (triggerType) {
      case "manual":
        return "Manual";

      case "scheduled":
        return "Scheduled";

      case "event":
        return "Event";

      default:
        return triggerType;
    }
  };


  const formatDateTime = (
    value
  ) => {
    if (!value) {
      return "—";
    }


    const date =
      new Date(value);


    if (
      Number.isNaN(
        date.getTime()
      )
    ) {
      return "—";
    }


    return date.toLocaleString(
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


  const calculateDuration = (
    execution
  ) => {
    if (
      !execution.started_at ||
      !execution.completed_at
    ) {
      return "—";
    }


    const start =
      new Date(
        execution.started_at
      ).getTime();


    const end =
      new Date(
        execution.completed_at
      ).getTime();


    if (
      Number.isNaN(start) ||
      Number.isNaN(end) ||
      end < start
    ) {
      return "—";
    }


    const duration =
      end - start;


    if (
      duration < 1000
    ) {
      return `${duration} ms`;
    }


    const seconds =
      duration / 1000;


    if (
      seconds < 60
    ) {
      return `${seconds.toFixed(1)} sec`;
    }


    const minutes =
      Math.floor(
        seconds / 60
      );

    const remainingSeconds =
      Math.round(
        seconds % 60
      );


    return `${minutes}m ${remainingSeconds}s`;
  };


  const getSummary = (
    execution
  ) => {
    if (
      execution.status ===
      "completed"
    ) {
      const summary =
        execution.output_data?.summary;


      if (
        typeof summary === "string" &&
        summary.trim()
      ) {
        return summary;
      }


      return "Workflow completed successfully.";
    }


    if (
      execution.status ===
      "failed"
    ) {
      return (
        execution.error_message ||
        "Workflow execution failed."
      );
    }


    if (
      execution.status ===
      "running"
    ) {
      return "Workflow is currently running.";
    }


    return "Workflow is waiting to run.";
  };


  /* ==========================================================
     PAGE NAVIGATION
     ========================================================== */

  const goToPage = (
    nextPage
  ) => {
    if (
      nextPage < 1 ||
      nextPage > totalPages ||
      nextPage === page
    ) {
      return;
    }


    loadHistory(
      nextPage
    );
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
            Workflow History
          </h2>

          <p>
            View previous workflow executions and their results.
          </p>

        </div>


        <button
          className="secondary-button"
          onClick={() =>
            loadHistory(page)
          }
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>

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
          FILTERS
          ==================================================== */}

      <div className="history-filters">

        <div className="history-filter-group">

          <label htmlFor="history-workflow">
            Workflow
          </label>

          <input
            id="history-workflow"
            type="text"
            value={
              workflowFilter
            }
            onChange={(event) => {
              setPage(1);

              setWorkflowFilter(
                event.target.value
              );
            }}
            placeholder="Search workflow..."
          />

        </div>


        <div className="history-filter-group">

          <label htmlFor="history-status">
            Status
          </label>

          <select
            id="history-status"
            value={
              statusFilter
            }
            onChange={(event) => {
              setPage(1);

              setStatusFilter(
                event.target.value
              );
            }}
          >

            <option value="">
              All statuses
            </option>

            <option value="completed">
              Completed
            </option>

            <option value="failed">
              Failed
            </option>

            <option value="running">
              Running
            </option>

            <option value="pending">
              Pending
            </option>

          </select>

        </div>


        <div className="history-filter-group">

          <label htmlFor="history-trigger">
            Trigger
          </label>

          <select
            id="history-trigger"
            value={
              triggerFilter
            }
            onChange={(event) => {
              setPage(1);

              setTriggerFilter(
                event.target.value
              );
            }}
          >

            <option value="">
              All triggers
            </option>

            <option value="manual">
              Manual
            </option>

            <option value="scheduled">
              Scheduled
            </option>

            <option value="event">
              Event
            </option>

          </select>

        </div>


        <div className="history-count">

          {total}{" "}
          {total === 1
            ? "execution"
            : "executions"}

        </div>

      </div>


      {/* ====================================================
          CONTENT
          ==================================================== */}

      {loading ? (

        <div className="history-loading-card">

          <div className="history-loading">
            Loading workflow history...
          </div>

        </div>

      ) : history.length === 0 ? (

        <div className="empty-page-card">

          <div className="empty-icon">
            History
          </div>

          <h3>
            No Workflow Executions
          </h3>

          <p>
            Workflow executions will appear here after a workflow is run.
          </p>

          <button
            className="primary-button"
            onClick={() =>
              navigate("/workflows")
            }
          >
            Go to Workflows
          </button>

        </div>

      ) : (

        <div className="history-list">

          {history.map(
            (execution) => (

              <div
                className="history-card"
                key={
                  execution.id
                }
              >

                {/* ======================================
                    CARD HEADER
                    ====================================== */}

                <div className="history-card-header">

                  <div className="history-title">

                    <div className="history-icon">
                      AI
                    </div>

                    <div>

                      <h3>
                        {formatWorkflowName(
                          execution.workflow_name
                        )}
                      </h3>

                      <span>
                        ID:{" "}
                        {execution.id.slice(
                          0,
                          8
                        )}
                      </span>

                    </div>

                  </div>


                  <span
                    className={`history-status ${execution.status}`}
                  >
                    {formatStatus(
                      execution.status
                    )}
                  </span>

                </div>


                {/* ======================================
                    EXECUTION DETAILS
                    ====================================== */}

                <div className="history-details">

                  <div className="history-detail">

                    <span>
                      Trigger
                    </span>

                    <strong>
                      {formatTriggerType(
                        execution.trigger_type
                      )}
                    </strong>

                  </div>


                  <div className="history-detail">

                    <span>
                      Started
                    </span>

                    <strong>
                      {formatDateTime(
                        execution.started_at
                      )}
                    </strong>

                  </div>


                  <div className="history-detail">

                    <span>
                      Completed
                    </span>

                    <strong>
                      {formatDateTime(
                        execution.completed_at
                      )}
                    </strong>

                  </div>


                  <div className="history-detail">

                    <span>
                      Duration
                    </span>

                    <strong>
                      {calculateDuration(
                        execution
                      )}
                    </strong>

                  </div>

                </div>


                {/* ======================================
                    RESULT
                    ====================================== */}

                <div className="history-result">

                  <span>
                    {execution.status ===
                    "failed"
                      ? "Error"
                      : "Result"}
                  </span>

                  <p>
                    {getSummary(
                      execution
                    )}
                  </p>

                </div>


                {/* ======================================
                    CREATED TIME
                    ====================================== */}

                <div className="history-footer">

                  <span>
                    Created{" "}
                    {formatDateTime(
                      execution.created_at
                    )}
                  </span>

                </div>

              </div>

            )
          )}

        </div>

      )}


      {/* ====================================================
          PAGINATION
          ==================================================== */}

      {!loading &&
        history.length > 0 && (
          <div className="history-pagination">

            <button
              className="secondary-button"
              onClick={() =>
                goToPage(
                  page - 1
                )
              }
              disabled={
                page <= 1
              }
            >
              ← Previous
            </button>


            <div className="history-page-info">

              Page{" "}
              <strong>
                {page}
              </strong>{" "}
              of{" "}
              <strong>
                {totalPages}
              </strong>

            </div>


            <button
              className="secondary-button"
              onClick={() =>
                goToPage(
                  page + 1
                )
              }
              disabled={
                page >=
                totalPages
              }
            >
              Next →
            </button>

          </div>
        )}

    </div>
  );
}


export default WorkflowHistory;