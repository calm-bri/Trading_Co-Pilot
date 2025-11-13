import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";
import api from "../services/api";

const ChartsPanel = () => {
  const [symbol, setSymbol] = useState("AAPL");
  const [series, setSeries] = useState([]);
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchChartData = async () => {
    setLoading(true);

    try {
      const [seriesRes, techRes] = await Promise.all([
        api.get(`/analytics/series/${symbol}`),
        api.get(`/analytics/technical/${symbol}`),
      ]);

      setSeries(seriesRes.data.series);
      setIndicators(techRes.data.indicators);
    } catch (err) {
      console.error("Error fetching chart data:", err);
    }

    setLoading(false);
  };

  useEffect(() => {
    fetchChartData();
  }, [symbol]);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Charts Dashboard</h1>

      {/* Symbol Selector */}
      <div className="mb-4 flex gap-4 items-center">
        <input
          className="border px-3 py-2 rounded"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter Symbol"
        />
        <button
          onClick={fetchChartData}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Load Chart
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading chart...</p>}

      {!loading && series.length > 0 && (
        <div className="space-y-10">
          {/* Candlestick Chart */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">{symbol} Price Chart</h2>

            <Plot
              data={[
                {
                  x: series.map((d) => d.date),
                  open: series.map((d) => d.open),
                  high: series.map((d) => d.high),
                  low: series.map((d) => d.low),
                  close: series.map((d) => d.close),
                  type: "candlestick",
                  name: "Candles",
                },
              ]}
              layout={{
                height: 500,
                dragmode: "zoom",
                margin: { t: 40, r: 40, b: 40, l: 50 },
              }}
              style={{ width: "100%" }}
              useResizeHandler
            />
          </div>

          {/* Volume Chart */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Volume</h2>

            <Plot
              data={[
                {
                  x: series.map((d) => d.date),
                  y: series.map((d) => d.volume),
                  type: "bar",
                  name: "Volume",
                },
              ]}
              layout={{
                height: 300,
                margin: { t: 30, r: 40, b: 40, l: 50 },
              }}
              style={{ width: "100%" }}
              useResizeHandler
            />
          </div>

          {/* Indicators Chart */}
          {indicators && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">Technical Indicators</h2>

              <Plot
                data={[
                  {
                    x: indicators.date,
                    y: indicators.rsi,
                    type: "scatter",
                    mode: "lines",
                    name: "RSI",
                },
                  {
                    x: indicators.date,
                    y: indicators.macd,
                    type: "scatter",
                    mode: "lines",
                    name: "MACD",
                },
                  {
                    x: indicators.date,
                    y: indicators.bollinger_upper,
                    type: "scatter",
                    mode: "lines",
                    name: "Bollinger Upper",
                    line: { dash: "dot" },
                },
                  {
                    x: indicators.date,
                    y: indicators.bollinger_lower,
                    type: "scatter",
                    mode: "lines",
                    name: "Bollinger Lower",
                    line: { dash: "dot" },
                },
                ]}
                layout={{
                  height: 400,
                  margin: { t: 40, r: 40, b: 40, l: 50 },
                }}
                style={{ width: "100%" }}
                useResizeHandler
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChartsPanel;
