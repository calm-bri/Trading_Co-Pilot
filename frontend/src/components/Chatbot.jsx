import React, { useState, useRef, useEffect } from 'react';
import api from '../services/api';
import { TrendingUp, BarChart3, Brain, Send, Sparkles } from 'lucide-react';

const Chatbot = ({ symbols = [] }) => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: '👋 Hello! I\'m your Trading Copilot AI. I can help you understand market sentiment, analyze trends, and provide insights based on real-time data. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Quick action templates
  const quickActions = [
    {
      icon: TrendingUp,
      label: 'Market Sentiment',
      query: 'What is the current market sentiment?'
    },
    {
      icon: BarChart3,
      label: 'Price Analysis',
      query: symbols.length > 0 
        ? `Analyze the price movement for ${symbols.join(', ')}`
        : 'What are the major market trends today?'
    },
    {
      icon: Brain,
      label: 'Market Bias',
      query: 'What is the overall market bias right now?'
    }
  ];

const handleSendMessage = async (messageText = null) => {
  const textToSend = messageText || inputMessage;
  if (!textToSend.trim() || isLoading) return;

  const userMessage = {
    type: 'user',
    content: textToSend,
    timestamp: new Date(),
  };

  setMessages(prev => [...prev, userMessage]);
  setInputMessage('');
  setIsLoading(true);

  try {
    const response = await api.post('/copilot/ask', {
      question: textToSend,
      symbols,
    });

    const botMessage = {
      type: 'bot',
      content: response.data.answer,
      marketData: {
        bias: response.data.market_bias,
        score: response.data.sentiment_score,
      },
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, botMessage]);
  } catch (error) {
    console.error('Copilot error:', error);

    setMessages(prev => [
      ...prev,
      {
        type: 'bot',
        content: '⚠️ Copilot failed to respond.',
        timestamp: new Date(),
      },
    ]);
  } finally {
    setIsLoading(false);
  }
};


  const handleQuickAction = (query) => {
    setInputMessage(query);
    // Auto-send after a brief delay to show the user what's being asked
    setTimeout(() => {
      handleSendMessage(query);
    }, 300);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getBiasColor = (bias) => {
    if (bias === 'bullish') return 'text-green-600 font-semibold';
    if (bias === 'bearish') return 'text-red-600 font-semibold';
    return 'text-gray-600 font-semibold';
  };

  const getBiasEmoji = (bias) => {
    if (bias === 'bullish') return '📈';
    if (bias === 'bearish') return '📉';
    return '➡️';
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-xl shadow-2xl overflow-hidden border border-gray-700">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 flex items-center gap-3">
        <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <h2 className="text-white font-bold text-lg">Trading Copilot AI</h2>
          <p className="text-blue-100 text-sm">Market insights powered by sentiment analysis</p>
        </div>
        {symbols.length > 0 && (
          <div className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
            <span className="text-white text-sm font-medium">
              {symbols.join(', ')}
            </span>
          </div>
        )}
      </div>

      {/* Quick Actions - Show only on first load */}
      {messages.length === 1 && (
        <div className="p-4 border-b border-gray-700 bg-gray-800/50">
          <p className="text-gray-400 text-sm mb-3">Quick Actions</p>
          <div className="grid grid-cols-3 gap-2">
            {quickActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => handleQuickAction(action.query)}
                className="flex flex-col items-center gap-2 p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-all border border-gray-700 hover:border-blue-500 group"
              >
                <action.icon className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform" />
                <span className="text-xs text-gray-300 text-center">{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.type === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white'
                  : 'bg-gray-800 text-gray-100 border border-gray-700'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
              
              {/* Market Data Badge */}
              {message.marketData && (
                <div className="mt-3 pt-3 border-t border-gray-700 flex flex-wrap gap-2 text-xs">
                  <div className="bg-gray-900 px-2 py-1 rounded-md flex items-center gap-1">
                    <span className="text-gray-400">Market Bias:</span>
                    <span className={getBiasColor(message.marketData.bias)}>
                      {getBiasEmoji(message.marketData.bias)} {message.marketData.bias.toUpperCase()}
                    </span>
                  </div>
                  <div className="bg-gray-900 px-2 py-1 rounded-md">
                    <span className="text-gray-400">Score: </span>
                    <span className="text-white font-medium">
                      {message.marketData.score?.toFixed(3)}
                    </span>
                  </div>
                  {message.marketData.symbols && message.marketData.symbols.length > 0 && (
                    <div className="bg-gray-900 px-2 py-1 rounded-md">
                      <span className="text-gray-400">Analyzed: </span>
                      <span className="text-blue-400 font-medium">
                        {message.marketData.symbols.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              )}
              
              <span className={`text-xs mt-2 block ${
                message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {formatTime(message.timestamp)}
              </span>
            </div>
          </div>
        ))}


        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-800/50 border-t border-gray-700 backdrop-blur-sm">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about market sentiment, price trends, or trading insights..."
            className="flex-1 bg-gray-800 text-gray-100 placeholder-gray-500 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-700"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-700 text-white rounded-xl px-6 py-3 transition-all disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-lg"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Powered by Gemini AI • Real-time market data • Press Enter to send
        </p>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default Chatbot;