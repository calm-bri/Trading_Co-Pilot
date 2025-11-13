import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const LiveChart = ({ symbol }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const candleSeriesRef = useRef();

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: '#1E1E1E' }, textColor: '#DDD' },
      grid: { vertLines: { color: '#2B2B2B' }, horzLines: { color: '#2B2B2B' } },
    });
    const candleSeries = chart.addCandlestickSeries();
    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    const ws = new WebSocket('ws://localhost:8000/ws/prices');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.s === symbol) {
        const price = data.p;
        const time = Math.floor(Date.now() / 1000);
        candleSeries.update({ time, open: price, high: price, low: price, close: price });
      }
    };

    return () => {
      ws.close();
      chart.remove();
    };
  }, [symbol]);

  return <div ref={chartContainerRef} className="w-full h-[400px]" />;
};

export default LiveChart;
