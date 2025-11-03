import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import api from '../services/api';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/analytics/summary');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="text-center">No analytics data available</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Portfolio Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Total Trades</h3>
          <p className="text-2xl font-bold text-blue-600">{analytics.total_trades || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Win Rate</h3>
          <p className="text-2xl font-bold text-green-600">{analytics.win_rate ? `${analytics.win_rate.toFixed(2)}%` : '0%'}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Total P&L</h3>
          <p className={`text-2xl font-bold ${analytics.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${analytics.total_pnl ? analytics.total_pnl.toFixed(2) : '0.00'}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-2">Sharpe Ratio</h3>
          <p className="text-2xl font-bold text-purple-600">{analytics.sharpe_ratio ? analytics.sharpe_ratio.toFixed(2) : 'N/A'}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Performance Chart</h2>
        {analytics.performance_data && analytics.performance_data.length > 0 ? (
          <Plot
            data={[
              {
                x: analytics.performance_data.map(d => d.date),
                y: analytics.performance_data.map(d => d.pnl),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'P&L',
                line: { color: 'blue' }
              }
            ]}
            layout={{
              title: 'Portfolio Performance Over Time',
              xaxis: { title: 'Date' },
              yaxis: { title: 'P&L ($)' },
              margin: { t: 50, r: 50, b: 50, l: 50 }
            }}
            style={{ width: '100%', height: '400px' }}
          />
        ) : (
          <p>No performance data available</p>
        )}
      </div>
    </div>
  );
};

export default Analytics;
