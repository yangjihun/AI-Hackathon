import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  getCurrentUser,
  isAuthenticated,
  logout,
  refreshMe,
  subscribeAuthChanged,
  type User,
} from "../../../shared/lib/auth";

export function Header() {
  const [user, setUser] = useState<User | null>(getCurrentUser());
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const sync = () => setUser(getCurrentUser());
    const unsubscribe = subscribeAuthChanged(sync);

    if (isAuthenticated() && !getCurrentUser()) {
      void refreshMe().finally(sync);
    } else {
      sync();
    }

    return unsubscribe;
  }, []);

  const handleLogout = () => {
    logout();
    setShowMenu(false);
    navigate("/login", { replace: true });
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <Link to="/browse" className="header-logo">
          NetPlus
        </Link>
      </div>
      <div className="header-right">
        {isAuthenticated() && user ? (
          <div className="header-user-menu">
            <button
              className="header-profile-btn"
              onClick={() => setShowMenu((prev) => !prev)}
              aria-label="Profile menu"
            >
              <span className="header-profile-icon">U</span>
              <span className="header-profile-name">{user.name}</span>
            </button>
            {showMenu && (
              <div className="header-dropdown">
                <div className="header-dropdown-item">
                  <span className="header-dropdown-email">{user.email}</span>
                </div>
                <button
                  className="header-dropdown-item header-dropdown-button"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <Link to="/login" className="header-login-btn">
            Login
          </Link>
        )}
      </div>
    </header>
  );
}
