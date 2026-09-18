import { NavLink, useNavigate } from "react-router-dom";


function Sidebar() {
  const navigate = useNavigate();

  const navigationItems = [
    {
      path: "/dashboard",
      icon: "D",
      label: "Dashboard",
    },
    {
      path: "/patients",
      icon: "P",
      label: "Patients",
    },
    {
      path: "/doctors",
      icon: "D",
      label: "Doctors",
    },
    {
      path: "/appointments",
      icon: "A",
      label: "Appointments",
    },
    {
      path: "/workflows",
      icon: "W",
      label: "Workflows",
    },
    {
      path: "/ai",
      icon: "AI",
      label: "AI Assistant",
    },
    {
      path: "/workflow-history",
      icon: "H",
      label: "Workflow History",
    },
  ];

  const handleLogout = () => {
    localStorage.removeItem("clinicflow_token");
    localStorage.removeItem("clinicflow_user");

    navigate("/login");
  };

  return (
    <aside className="sidebar">

      <div className="sidebar-brand">

        <div className="sidebar-brand-icon">
          CF
        </div>

        <div>
          <h1>
            ClinicFlow
          </h1>

          <span>
            Clinic Operations
          </span>
        </div>

      </div>


      <nav className="sidebar-navigation">

        <div className="sidebar-section-title">
          MAIN
        </div>

        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive
                ? "sidebar-link active"
                : "sidebar-link"
            }
          >
            <span className="sidebar-icon">
              {item.icon}
            </span>

            <span>
              {item.label}
            </span>
          </NavLink>
        ))}

      </nav>


      <div className="sidebar-bottom">

        <button
          className="sidebar-logout"
          onClick={handleLogout}
        >
          <span className="sidebar-icon">
            L
          </span>

          <span>
            Logout
          </span>
        </button>

      </div>

    </aside>
  );
}


export default Sidebar;
