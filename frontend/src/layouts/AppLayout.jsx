import { Outlet } from "react-router-dom";

import Sidebar from "../components/Sidebar";


function AppLayout() {
  const storedUser =
    localStorage.getItem("clinicflow_user");

  let user = null;

  if (storedUser) {
    try {
      user = JSON.parse(storedUser);
    } catch {
      user = null;
    }
  }

  return (
    <div className="app-layout">

      <Sidebar />

      <div className="app-main">

        <header className="app-header">

          <div>
            <span className="header-label">
              ClinicFlow
            </span>

            <h1>
              {user?.name || "Clinic User"}
            </h1>
          </div>


          <div className="header-user">

            <div className="header-avatar">
              {(user?.name || "U")
                .charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <strong>
                {user?.name || "User"}
              </strong>

              <span>
                {user?.role || ""}
              </span>
            </div>

          </div>

        </header>


        <main className="app-content">
          <Outlet />
        </main>

      </div>

    </div>
  );
}


export default AppLayout;
