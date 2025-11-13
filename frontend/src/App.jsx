import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import ChartsPanel from './pages/ChartsPanel';
import TradeJournal from './components/TradeJournal';
import AlertsPanel from './components/AlertsPanel';
import SentimentFeed from './components/SentimentFeed';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Analytics from './pages/Analytics';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/charts" element={<ChartsPanel />} />
              <Route path="/journal" element={<TradeJournal />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/alerts" element={<AlertsPanel />} />
              <Route path="/sentiment" element={<SentimentFeed />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
