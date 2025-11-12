import React, { useState, useEffect } from 'react';
import api from '../services/api';
<<<<<<< HEAD
import axios from "axios";
=======
>>>>>>> 22d588f1441daecb5784d63a1f084b0589ead99c

const TradeJournal = () => {
  const [trades, setTrades] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    symbol: '',
    trade_type: 'BUY',
    quantity: '',
    price: '',
    notes: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    try {
      const response = await api.get('/trades/');
      setTrades(response.data);
    } catch (error) {
      console.error('Failed to fetch trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
<<<<<<< HEAD
  e.preventDefault();

  try {
    const token = localStorage.getItem("token"); // JWT stored at login

    await axios.post(
      "http://localhost:8000/api/trades/", // ✅ correct backend endpoint
      {
        symbol: formData.symbol,
        trade_type: formData.trade_type.toLowerCase(), // backend expects lowercase ('buy'/'sell')
        quantity: parseFloat(formData.quantity),
        price: parseFloat(formData.price),
        notes: formData.notes,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // ✅ required for FastAPI auth
        },
      }
    );

    // Reset form
    setFormData({
      symbol: "",
      trade_type: "BUY",
      quantity: "",
      price: "",
      notes: "",
    });

    setShowForm(false);
    fetchTrades(); // refresh the trade list
  } catch (error) {
    console.error("Failed to add trade:", error.response?.data || error);
  }
};

=======
    e.preventDefault();
    try {
      await api.post('/trades/add', formData);
      setFormData({
        symbol: '',
        trade_type: 'BUY',
        quantity: '',
        price: '',
        notes: ''
      });
      setShowForm(false);
      fetchTrades();
    } catch (error) {
      console.error('Failed to add trade:', error);
    }
  };
>>>>>>> 22d588f1441daecb5784d63a1f084b0589ead99c

  const handleCSVUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/trades/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      fetchTrades();
      alert('CSV uploaded successfully!');
    } catch (error) {
      console.error('Failed to upload CSV:', error);
      alert('Failed to upload CSV');
    }
  };

  if (loading) {
    return <div className="text-center">Loading trades...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Trade Journal</h1>
        <div className="space-x-4">
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            {showForm ? 'Cancel' : 'Add Trade'}
          </button>
          <label className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 cursor-pointer">
            Upload CSV
            <input
              type="file"
              accept=".csv"
              onChange={handleCSVUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-xl font-semibold mb-4">Add New Trade</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Trade Type</label>
                <select
                  value={formData.trade_type}
                  onChange={(e) => setFormData({...formData, trade_type: e.target.value})}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Quantity</label>
                <input
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Notes (Optional)</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                rows="3"
              />
            </div>
            <div className="mt-4">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Add Trade
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {trades.map((trade) => (
              <tr key={trade.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{trade.symbol}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span className={`px-2 py-1 text-xs rounded ${
                    trade.trade_type === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {trade.trade_type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.quantity}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${trade.price}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(trade.timestamp).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.notes || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {trades.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No trades recorded yet. Add your first trade above.
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeJournal;
