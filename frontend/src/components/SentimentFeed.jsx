import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import api from '../services/api';

const SentimentFeed = () => {
  const [sentimentData, setSentimentData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSentiment();
  }, []);

  const fetchSentiment = async () => {
    try {
      const response = await api.get('/sentiment/latest');
      const data = response.data;

      // Wrap single object into array
      setSentimentData(response.data.data || []);


    } catch (error) {
      console.error('Failed to fetch sentiment data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center">Loading sentiment data...</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Market Sentiment Feed</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sentiment Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Sentiment Trend</h2>
          {sentimentData.length > 0 ? (
            <Plot
              data={[
                {
                  x: sentimentData.map(s => new Date(s.timestamp).toLocaleString()),
                  y: sentimentData.map(s => s.sentiment_score),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Sentiment Score',
                  line: { color: 'orange' },
                  marker: { size: 6 }
                }
              ]}
              layout={{
                title: 'Market Sentiment Over Time',
                xaxis: {
                  title: 'Time',
                  tickangle: -45
                },
                yaxis: {
                  title: 'Sentiment Score',
                  range: [-1, 1]
                },
                margin: { t: 50, r: 50, b: 100, l: 50 },
                height: 400
              }}
              style={{ width: '100%' }}
            />
          ) : (
            <p>No sentiment data available</p>
          )}
        </div>

        {/* Sentiment Summary */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Sentiment Summary</h2>
          {sentimentData.length > 0 ? (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-medium">Current Sentiment:</span>
                <span className={`px-3 py-1 rounded text-sm font-medium ${sentimentData[sentimentData.length - 1]?.sentiment_score > 0.1
                    ? 'bg-green-100 text-green-800'
                    : sentimentData[sentimentData.length - 1]?.sentiment_score < -0.1
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                  {sentimentData[sentimentData.length - 1]?.sentiment_score > 0.1
                    ? 'Positive'
                    : sentimentData[sentimentData.length - 1]?.sentiment_score < -0.1
                      ? 'Negative'
                      : 'Neutral'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium">Average Sentiment:</span>
                <span className="text-gray-600">
                  {(sentimentData.reduce((sum, s) => sum + s.sentiment_score, 0) / sentimentData.length).toFixed(3)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium">Data Points:</span>
                <span className="text-gray-600">{sentimentData.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium">Last Updated:</span>
                <span className="text-gray-600 text-sm">
                  {sentimentData.length > 0 ? new Date(sentimentData[sentimentData.length - 1].timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
            </div>
          ) : (
            <p>No sentiment data available</p>
          )}
        </div>
      </div>

      {/* Recent Sentiment Items */}
      <div className="bg-white p-6 rounded-lg shadow-md mt-8">
        <h2 className="text-xl font-semibold mb-4">Recent Sentiment Analysis</h2>
        {sentimentData.length > 0 ? (
          <div className="space-y-4">
            {sentimentData.slice(-10).reverse().map((item, index) => (
              <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-gray-800 mb-2">{item.text || 'Market sentiment analysis'}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>Source: {item.source || 'Twitter'}</span>
                      <span>Score: {item.sentiment_score?.toFixed(3)}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className={`px-2 py-1 text-xs rounded ${item.sentiment_score > 0.1 ? 'bg-green-100 text-green-800' :
                        item.sentiment_score < -0.1 ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                      }`}>
                      {item.sentiment_score > 0.1 ? 'Positive' :
                        item.sentiment_score < -0.1 ? 'Negative' : 'Neutral'}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(item.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No recent sentiment data</p>
        )}
      </div>
    </div>
  );
};

export default SentimentFeed;
