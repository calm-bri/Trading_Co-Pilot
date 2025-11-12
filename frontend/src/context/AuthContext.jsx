import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';


const AuthContext = createContext();

const API_BASE_URL = "http://localhost:8000";

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // TODO: Validate token with backend
      setUser({ token });
    }
    setLoading(false);
  }, []);
  const login = async (email, password) => {
    try {
      // Convert to URL-encoded form data
      const formData = new URLSearchParams();
      formData.append("username", email); // backend expects "username"
      formData.append("password", password);
  
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
  
      const { access_token } = response.data;
      localStorage.setItem("token", access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      setUser({ token: access_token });
  
      return true;
    } catch (error) {
      console.error("Login failed:", error.response?.data || error);
      return false;
    }
  };

  const register = async (username, email, password) => {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/register`, { username, email, password });
      return true;
    } catch (error) {
      console.error('Registration failed:', error.response?.data || error);
      return false;
    }
  };


  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
