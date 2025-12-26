import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import api from '../services/api';

const Dashboard = () => {
  const [trades, setTrades] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [sentiment, setSentiment] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [tradesRes, alertsRes, sentimentRes] = await Promise.all([
        api.get('/trades/'),
        api.get('/alerts/active'),
        // api.get('/sentiment/latest')
      ]);
      setTrades(tradesRes.data);
      setAlerts(alertsRes.data);
      setSentiment(sentimentRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center">Loading dashboard...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Trading Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Recent Trades */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          {trades.length > 0 ? (
            <div className="space-y-2">
              {trades.slice(0, 5).map((trade) => (
                <div key={trade.id} className="flex justify-between items-center p-2 border-b">
                  <div>
                    <span className="font-medium">{trade.symbol}</span>
                    <span className={`ml-2 px-2 py-1 text-xs rounded ${
                      trade.trade_type === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.trade_type}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">${trade.price}</div>
                    <div className="text-sm text-gray-500">{trade.quantity} shares</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No trades yet</p>
          )}
        </div>

        {/* Active Alerts */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Active Alerts</h2>
          {alerts.length > 0 ? (
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div key={alert.id} className="p-2 border-b">
                  <div className="font-medium">{alert.symbol}</div>
                  <div className="text-sm text-gray-600">{alert.condition}: ${alert.target_price}</div>
                </div>
              ))}
            </div>
          ) : (
            <p>No active alerts</p>
          )}
        </div>
      </div>

      {/* Sentiment Chart */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Market Sentiment</h2>
        {sentiment.length > 0 ? (
          <Plot
            data={[
              {
                x: sentiment.map(s => s.timestamp),
                y: sentiment.map(s => s.sentiment_score),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Sentiment Score',
                line: { color: 'orange' }
              }
            ]}
            layout={{
              title: 'Market Sentiment Over Time',
              xaxis: { title: 'Time' },
              yaxis: { title: 'Sentiment Score', range: [-1, 1] },
              margin: { t: 50, r: 50, b: 50, l: 50 }
            }}
            style={{ width: '100%', height: '400px' }}
          />
        ) : (
          <p>No sentiment data available</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
