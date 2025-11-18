import React, { useState, useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";
import api from "../services/api";

const ChartsPanel = () => {
  const [symbol, setSymbol] = useState("AAPL");
  const [timeframe, setTimeframe] = useState("D");
  const [series, setSeries] = useState([]);
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);

  const chartContainerRef = useRef(null);
  const volumeContainerRef = useRef(null);
  const chartRef = useRef(null);
  const volumeChartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const smaSeriesRef = useRef(null);
  const emaSeriesRef = useRef(null);

  const timeframes = [
    { label: "1D", value: "D" },
    { label: "1W", value: "W" },
    { label: "1M", value: "M" },
  ];

  const fetchChartData = async () => {
    setLoading(true);

    try {
      const [seriesRes, techRes] = await Promise.all([
        api.get(`/analytics/series/${symbol}?resolution=${timeframe}`),
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
  }, [symbol, timeframe]);

  useEffect(() => {
    if (!chartContainerRef.current || series.length === 0) return;

    // Cleanup previous chart
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // Create main chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: { background: { color: "#FFFFFF" }, textColor: "#000" },
      grid: {
        vertLines: { color: "#f0f3fa" },
        horzLines: { color: "#f0f3fa" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candleSeries = chart.addCandlestickSeries();
    const smaSeries = chart.addLineSeries({ color: "#2196F3", lineWidth: 2 });
    const emaSeries = chart.addLineSeries({ color: "#FF9800", lineWidth: 2 });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    smaSeriesRef.current = smaSeries;
    emaSeriesRef.current = emaSeries;

    // Set candlestick data
    const candleData = series.map((d) => ({
      time: new Date(d.date).getTime() / 1000,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(candleData);

    // Add moving averages if indicators available
    if (indicators && indicators.sma && indicators.ema) {
      const smaData = indicators.date.map((date, i) => ({
        time: new Date(date).getTime() / 1000,
        value: indicators.sma[i],
      }));
      const emaData = indicators.date.map((date, i) => ({
        time: new Date(date).getTime() / 1000,
        value: indicators.ema[i],
      }));
      smaSeries.setData(smaData);
      emaSeries.setData(emaData);
    }

    // Resize handler
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [series, indicators]);

  useEffect(() => {
    if (!volumeContainerRef.current || series.length === 0) return;

    // Cleanup previous volume chart
    if (volumeChartRef.current) {
      volumeChartRef.current.remove();
    }

    // Create volume chart
    const volumeChart = createChart(volumeContainerRef.current, {
      width: volumeContainerRef.current.clientWidth,
      height: 200,
      layout: { background: { color: "#FFFFFF" }, textColor: "#000" },
      grid: {
        vertLines: { color: "#f0f3fa" },
        horzLines: { color: "#f0f3fa" },
      },
    });

    const volumeSeries = volumeChart.addHistogramSeries({
      color: "#26a69a",
    });

    volumeChartRef.current = volumeChart;
    volumeSeriesRef.current = volumeSeries;

    // Set volume data
    const volumeData = series.map((d) => ({
      time: new Date(d.date).getTime() / 1000,
      value: d.volume,
    }));
    volumeSeries.setData(volumeData);

    // Sync time scale with main chart
    if (chartRef.current) {
      volumeChart.timeScale().subscribeVisibleTimeRangeChange(() => {
        const timeRange = volumeChart.timeScale().getVisibleRange();
        chartRef.current.timeScale().setVisibleRange(timeRange);
      });
      chartRef.current.timeScale().subscribeVisibleTimeRangeChange(() => {
        const timeRange = chartRef.current.timeScale().getVisibleRange();
        volumeChart.timeScale().setVisibleRange(timeRange);
      });
    }

    // Resize handler
    const handleResize = () => {
      volumeChart.applyOptions({ width: volumeContainerRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      volumeChart.remove();
    };
  }, [series]);

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Charts Dashboard</h1>

      {/* Symbol and Timeframe Selector */}
      <div className="mb-4 flex gap-4 items-center">
        <input
          className="border px-3 py-2 rounded"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter Symbol"
        />
        <select
          className="border px-3 py-2 rounded"
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
        >
          {timeframes.map((tf) => (
            <option key={tf.value} value={tf.value}>
              {tf.label}
            </option>
          ))}
        </select>
        <button
          onClick={fetchChartData}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Load Chart
        </button>
      </div>

      {loading && <p className="text-gray-500">Loading chart...</p>}

      {!loading && series.length > 0 && (
        <div className="space-y-4">
          {/* Candlestick Chart */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">{symbol} Price Chart ({timeframe})</h2>
            <div ref={chartContainerRef} />
            <div className="mt-2 text-sm text-gray-600">
              <span className="inline-block w-4 h-1 bg-blue-500 mr-2"></span>SMA
              <span className="inline-block w-4 h-1 bg-orange-500 ml-4 mr-2"></span>EMA
            </div>
          </div>

          {/* Volume Chart */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Volume</h2>
            <div ref={volumeContainerRef} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartsPanel;
