import React, { useState, useEffect, useCallback } from "react";
import Plot from "react-plotly.js";
import api from "../services/api";

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ---- Symbol Chart States ----
  const [selectedSymbol, setSelectedSymbol] = useState("AAPL");
  const [symbolSeries, setSymbolSeries] = useState([]);
  const [symbolLoading, setSymbolLoading] = useState(false);

  // ---- Fetch Summary + Risk Metrics ----
  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");

      if (!token) {
        setError("Not authenticated. Please login again.");
        return;
      }

      const [summaryRes, riskRes] = await Promise.allSettled([
        api.get("/analytics/summary"),
        api.get("/analytics/risk-metrics"),
      ]);

      if (summaryRes.status === "fulfilled") {
        setAnalytics(summaryRes.value.data);
      } else {
        setError("Failed to fetch analytics summary.");
      }

      if (riskRes.status === "fulfilled") {
        setRiskMetrics(riskRes.value.data);
      }

    } catch (e) {
      setError("Unexpected error fetching analytics.");
    } finally {
      setLoading(false);
    }
  }, []);

  // ---- Fetch Symbol Series ----
  const fetchSymbolData = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      console.log("❌ No token found. Skipping symbol request.");
      return;
    }

    if (!selectedSymbol) return;

    setSymbolLoading(true);
    try {
      const res = await api.get(`/analytics/series/${selectedSymbol}`);
      console.log("🔥 SERIES:", res.data);
      setSymbolSeries(res.data.series || []);
    } catch (err) {
      console.log("❌ SERIES ERROR:", err.response?.data || err.message);
      setSymbolSeries([]);
    }
    setSymbolLoading(false);
  };

  // ---- INITIAL PAGE LOAD ----
  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // ---- Load Symbol Chart AFTER token is available ----
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      console.log("Token not ready yet.");
      return;
    }

    // slight delay ensures axios interceptor loads
    setTimeout(() => {
      fetchSymbolData();
    }, 300);
  }, []);

  const formatCurrency = (n) => {
    if (n === null || n === undefined || Number.isNaN(n)) return "--";
    return `$${Number(n).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 font-semibold mb-4">{error}</p>
        <button
          onClick={fetchAll}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No analytics data available.</p>
        <button
          onClick={fetchAll}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>
    );
  }

  const {
    total_trades = 0,
    total_value = 0,
    win_rate = 0,
    total_pnl = 0,
    sharpe_ratio = null,
    performance_data = null,
  } = analytics;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Portfolio Analytics</h1>
        <button
          onClick={fetchAll}
          className="px-3 py-1 border rounded hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Total Trades</h3>
          <p className="text-2xl font-bold text-blue-600">{total_trades}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Win Rate</h3>
          <p className="text-2xl font-bold text-green-600">
            {Number(win_rate).toFixed(2)}%
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Total P&L</h3>
          <p className={`text-2xl font-bold ${total_pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
            {formatCurrency(total_pnl)}
          </p>
          <p className="text-xs text-gray-400">
            Value: {formatCurrency(total_value)}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Sharpe Ratio</h3>
          <p className="text-2xl font-bold text-purple-600">
            {sharpe_ratio !== null ? sharpe_ratio.toFixed(4) : "N/A"}
          </p>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Performance Chart</h2>

        {performance_data?.length > 0 ? (
          <Plot
            data={[
              {
                x: performance_data.map((d) => d.date),
                y: performance_data.map((d) => d.pnl),
                type: "scatter",
                mode: "lines+markers",
              },
            ]}
            layout={{
              title: "Portfolio Performance Over Time",
              margin: { t: 50, r: 25, b: 60, l: 60 },
            }}
            style={{ width: "100%", height: "420px" }}
          />
        ) : (
          <p>No performance data.</p>
        )}
      </div>

      {/* Risk & Price Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Card */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-3">Risk Metrics</h3>
          {riskMetrics ? (
            <ul className="text-sm space-y-1">
              <li>Max Drawdown: {riskMetrics.max_drawdown}</li>
              <li>Sharpe Ratio: {riskMetrics.sharpe_ratio}</li>
              <li>Volatility: {riskMetrics.volatility}</li>
              <li>VaR 95%: {riskMetrics.var_95}</li>
            </ul>
          ) : (
            <p>No risk data available.</p>
          )}
        </div>

        {/* Symbol Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-3">Price Chart</h3>

          <div className="flex items-center gap-3 mb-4">
            <input
              type="text"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
              placeholder="AAPL, TSLA, BTC, NIFTY"
              className="border px-3 py-2 rounded w-40"
            />
            <button
              onClick={fetchSymbolData}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Load
            </button>
          </div>

          {symbolLoading ? (
            <p>Loading chart...</p>
          ) : symbolSeries.length === 0 ? (
            <p>Enter symbol and click Load.</p>
          ) : (
            <Plot
              data={[
                {
                  x: symbolSeries.map((d) => d.date),
                  open: symbolSeries.map((d) => d.open),
                  high: symbolSeries.map((d) => d.high),
                  low: symbolSeries.map((d) => d.low),
                  close: symbolSeries.map((d) => d.close),
                  type: "candlestick",
                },
              ]}
              layout={{
                height: 350,
                margin: { t: 40, r: 40, b: 40, l: 50 },
                xaxis: { title: "Date" },
                yaxis: { title: "Price" },
              }}
              style={{ width: "100%" }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
