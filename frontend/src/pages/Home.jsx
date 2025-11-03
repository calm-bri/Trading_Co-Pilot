import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-8">
        Welcome to Trading Copilot
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        AI-assisted trading platform for market analysis, trade journaling, and insights.
      </p>
      {!user ? (
        <div className="space-x-4">
          <Link
            to="/login"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            Get Started
          </Link>
        </div>
      ) : (
        <div className="space-x-4">
          <Link
            to="/dashboard"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
        </div>
      )}
    </div>
  );
};

export default Home;
