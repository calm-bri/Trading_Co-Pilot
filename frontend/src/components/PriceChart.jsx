import React, { useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";
import api from "../services/api";

const PriceChart = ({ symbol = "AAPL" }) => {
  const chartContainerRef = useRef(null);

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: "#FFFFFF" }, textColor: "#000" },
      grid: {
        vertLines: { color: "#f0f3fa" },
        horzLines: { color: "#f0f3fa" },
      },
    });

    const candleSeries = chart.addCandlestickSeries();

    // Fetch OHLC Data
    const fetchOHLC = async () => {
      try {
        const res = await api.get(`/prices/ohlc?symbol=${symbol}`);
        candleSeries.setData(res.data);
      } catch (error) {
        console.error("Failed to load OHLC:", error);
      }
    };

    fetchOHLC();

    // Resize chart on window resize
    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [symbol]);

  return (
    <div className="w-full h-auto">
      <h2 className="text-xl font-bold mb-2">{symbol} Price Chart</h2>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default PriceChart;
