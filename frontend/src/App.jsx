import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";

import AI from "./pages/AI";
import Appointments from "./pages/Appointments";
import Dashboard from "./pages/Dashboard";
import Doctors from "./pages/Doctors";
import Login from "./pages/Login";
import Patients from "./pages/Patients";
import WorkflowHistory from "./pages/WorkflowHistory";
import Workflows from "./pages/Workflows";


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/patients"
            element={<Patients />}
          />

          <Route
            path="/doctors"
            element={<Doctors />}
          />

          <Route
            path="/appointments"
            element={<Appointments />}
          />

          <Route
            path="/workflows"
            element={<Workflows />}
          />

          <Route
            path="/ai"
            element={<AI />}
          />

          <Route
            path="/workflow-history"
            element={<WorkflowHistory />}
          />

        </Route>

        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}


export default App;
