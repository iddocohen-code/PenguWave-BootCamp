import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import LoginModal from "./components/LoginModal";
import EventsPage from "./pages/EventsPage";
import UsersPage from "./pages/UsersPage";
import NotFound from "./pages/NotFound";

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for valid token on mount and show login if missing
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setShowLogin(true);
      setIsLoggedIn(false);
    } else {
      setIsLoggedIn(true);
    }
  }, []);

  const handleCloseLogin = () => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsLoggedIn(true);
    }
    setShowLogin(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setIsLoggedIn(false);
    setShowLogin(true);
  };

  // Guard /users route: only admins can access
  const isAdmin = localStorage.getItem("role") === "admin";

  return (
    <>
      <Navbar onLoginClick={() => setShowLogin(true)} onLogout={isLoggedIn ? handleLogout : undefined} />
      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/events" replace />} />
          <Route path="/events" element={isLoggedIn ? <EventsPage /> : <Navigate to="/" replace />} />
          <Route path="/users" element={isLoggedIn && isAdmin ? <UsersPage /> : <NotFound />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      {showLogin && <LoginModal onClose={handleCloseLogin} />}
    </>
  );
}

export default App;
