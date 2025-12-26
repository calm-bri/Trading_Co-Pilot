import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="text-xl font-bold">
            Trading Copilot
          </Link>
          <div className="flex space-x-4">
            <Link to="/" className="hover:text-blue-200">Home</Link>
            {user ? (
              <>
                <Link to="/dashboard" className="hover:text-blue-200">Dashboard</Link>
                <Link to="/journal" className="hover:text-blue-200">Journal</Link>
                <Link to="/analytics" className="hover:text-blue-200">Analytics</Link>
                <Link to="/charts" className="hover:text-blue-200">Charts</Link>
                <Link to="/alerts" className="hover:text-blue-200">Alerts</Link>
                <Link to="/sentiment" className="hover:text-blue-200">Sentiment</Link>
                <Link to="/copilot">🤖 Copilot</Link>
                <button onClick={handleLogout} className="hover:text-blue-200">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-blue-200">Login</Link>
                <Link to="/register" className="hover:text-blue-200">Register</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
