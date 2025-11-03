# Trading Copilot Web App

A production-ready AI-assisted Trading Copilot Web Application that helps traders analyze markets, journal trades, and receive AI-based insights and alerts.

## Tech Stack

- **Frontend**: React (Vite) + Tailwind CSS
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL + ChromaDB
- **ORM**: SQLAlchemy + Alembic
- **Visualization**: TradingView Lightweight Charts
- **Authentication**: JWT-based auth
- **APIs & Data Sources**: Yahoo Finance, Alpha Vantage, Twitter, RSS Feeds
- **AI Copilot**: Gemini API
- **DevOps**: Docker
- **Hosting**: Vercel (FE) + Render (BE)

## Features

- User authentication and authorization
- Trade journaling with CRUD operations
- Market analytics and performance metrics
- Real-time sentiment analysis from Twitter and RSS feeds
- Technical indicators (RSI, MACD, EMA, Bollinger Bands)
- Risk management calculations (Max Drawdown, Sharpe Ratio)
- AI Copilot for natural language Q&A
- Interactive charts and dashboards
- Alerts for price triggers and market events
- CSV upload for personal data

## Project Structure

```
trading-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   └── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── assets/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.11 (for local development)
- Node.js 18+ (for local development)

### Quick Start with Docker

1. Clone the repository
2. Create a `.env` file in the root directory with your API keys:
   ```
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=postgresql://postgres:password@db/trading_copilot
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80
   YAHOO_FINANCE_API_KEY=your-yahoo-key
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
   TWITTER_API_KEY=your-twitter-key
   GEMINI_API_KEY=your-gemini-key
   ```
3. Run the application:
   ```bash
   docker-compose up --build
   ```
4. Access the application at `http://localhost`

### Local Development

#### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   alembic upgrade head
   ```

5. Run the backend:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the frontend:
   ```bash
   npm run dev
   ```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

## Deployment

The application is configured for production deployment using Docker Compose with Nginx as a reverse proxy.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
