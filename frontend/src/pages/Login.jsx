import { useState } from "react";
import { useNavigate } from "react-router-dom";

import apiClient from "../api/client";


function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      /*
       * The backend /auth/login endpoint expects
       * JSON matching the UserLogin schema:
       *
       * {
       *   "email": "...",
       *   "password": "..."
       * }
       */

      const response = await apiClient.post(
        "/auth/login",
        {
          email: email,
          password: password,
        }
      );

      const token = response.data.access_token;

      /*
       * Store the JWT so authenticated API
       * requests can use it.
       */

      localStorage.setItem(
        "clinicflow_token",
        token
      );


      /*
       * Get the authenticated user's information.
       */

      const userResponse = await apiClient.get(
        "/protected"
      );

      localStorage.setItem(
        "clinicflow_user",
        JSON.stringify(userResponse.data)
      );


      /*
       * Login successful.
       */

      navigate("/dashboard");

    } catch (err) {
      console.error(
        "Login error:",
        err
      );

      const detail =
        err.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else if (
        Array.isArray(detail)
      ) {
        setError(
          "Please enter a valid email and password."
        );
      } else {
        setError(
          "Login failed. Please check your credentials."
        );
      }

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-page">

      <div className="login-card">

        <div className="login-header">

          <div className="brand-icon">
            CF
          </div>

          <h1>
            ClinicFlow
          </h1>

          <p>
            AI-Powered Clinic Operations
          </p>

        </div>


        <form
          className="login-form"
          onSubmit={handleSubmit}
        >

          <div className="form-group">

            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
              placeholder="Enter your email"
              autoComplete="email"
              required
            />

          </div>


          <div className="form-group">

            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              placeholder="Enter your password"
              autoComplete="current-password"
              required
            />

          </div>


          {error && (
            <div className="login-error">
              {error}
            </div>
          )}


          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>

        </form>

      </div>

    </div>
  );
}


export default Login;