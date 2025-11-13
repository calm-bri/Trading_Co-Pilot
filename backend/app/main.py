from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routes import users, trades, analytics, sentiment, alerts, copilot
from app.routes import prices
import structlog

# Create database tables (commented out for now to avoid connection issues during testing)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading Copilot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = structlog.get_logger()
    logger.info("Request started", method=request.method, url=str(request.url), headers=dict(request.headers))
    response = await call_next(request)
    logger.info("Request completed", status_code=response.status_code)
    return response

# @app.middleware("http")
# async def log_requests(request, call_next):
#     try:
#         response = await call_next(request)
#         return response
#     except Exception as e:
#         print("\n🔥🔥🔥 BACKEND ERROR 🔥🔥🔥")
#         print("URL:", request.url)
#         print("ERROR TYPE:", type(e))
#         print("ERROR:", e)
#         raise e
  





# Include routers
app.include_router(users, prefix="/api/auth", tags=["Authentication"])
app.include_router(trades, prefix="/api/trades", tags=["Trades"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sentiment, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(alerts, prefix="/api/alerts", tags=["Alerts"])
app.include_router(copilot, prefix="/api/copilot", tags=["Copilot"])
app.include_router(prices.router, prefix="/api/prices", tags=["prices"])

@app.get("/")
async def root():
    return {"message": "Welcome to Trading Copilot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
