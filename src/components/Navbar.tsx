import { Link, useLocation } from "react-router-dom";

interface NavbarProps {
  onLoginClick: () => void;
  onLogout?: () => void;
}

export default function Navbar({ onLoginClick, onLogout }: NavbarProps) {
  const location = useLocation();
  const isLoggedIn = !!localStorage.getItem("token");

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/events" style={{ textDecoration: "none", color: "inherit" }}>
          PenguWave 🐧
        </Link>
      </div>
      <div className="navbar-links">
        {isLoggedIn && (
          <>
            <Link
              to="/events"
              className={location.pathname.startsWith("/events") ? "active" : ""}
            >
              Events
            </Link>
            <Link
              to="/users"
              className={location.pathname === "/users" ? "active" : ""}
            >
              Users
            </Link>
          </>
        )}
        {isLoggedIn && onLogout ? (
          <button onClick={onLogout} className="navbar-login-btn">
            Logout
          </button>
        ) : (
          <button onClick={onLoginClick} className="navbar-login-btn">
            Login
          </button>
        )}
      </div>
    </nav>
  );
}
