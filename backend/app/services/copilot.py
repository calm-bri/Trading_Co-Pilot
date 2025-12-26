from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger()


class TradingCopilot:
    """Trading Copilot using direct Gemini REST API for maximum reliability"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"
        self.models = []
        self.current_model = None
        self._models_initialized = False
        
        if not self.api_key:
            logger.warning("❌ GEMINI_API_KEY missing")
        else:
            logger.info("✅ Trading Copilot initialized (models will load on first request)")
    
    async def _initialize_models(self):
        """Fetch and set available models from API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={"key": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract models that support generateContent
                    available_models = [
                        model["name"].replace("models/", "")
                        for model in data.get("models", [])
                        if "generateContent" in model.get("supportedGenerationMethods", [])
                    ]
                    
                    # Prioritize flash models for free tier
                    flash_models = [m for m in available_models if "flash" in m.lower()]
                    other_models = [m for m in available_models if "flash" not in m.lower()]
                    
                    self.models = flash_models + other_models
                    self.current_model = self.models[0] if self.models else None
                    
                    logger.info("✅ Available models fetched", 
                               count=len(self.models), 
                               current=self.current_model,
                               all_models=self.models[:5])  # Log first 5
                else:
                    logger.warning("Failed to fetch models", status=response.status_code)
                    self.models = ["gemini-1.5-flash-latest"]
                    self.current_model = self.models[0]
                    
        except Exception as e:
            logger.error("Error fetching models", error=str(e))
            self.models = ["gemini-1.5-flash-latest"]
            self.current_model = self.models[0]

    async def chat(
        self,
        query: str,
        symbols: List[str] = None,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to Gemini API
        
        Args:
            query: User's question/message
            symbols: Optional list of trading symbols for context
            conversation_history: Optional chat history for context
            
        Returns:
            Dict with answer, market_bias, sentiment_score, and timestamp
        """
        
        if not self.api_key:
            return self._error_response("Gemini API key is not configured.")
        
        # Lazy load models on first request
        if not self._models_initialized:
            await self._initialize_models()
            self._models_initialized = True
        
        if not self.models:
            return self._error_response("No models available. Please check your API key and region.")

        # Try each model until one works
        last_error = None
        for model in self.models:
            try:
                result = await self._generate_content(query, model)
                if result:
                    self.current_model = model  # Remember working model
                    return result
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ Model {model} failed, trying next", error=str(e))
                continue
        
        # All models failed
        return self._error_response(f"All models failed. Last error: {last_error}")

    async def _generate_content(self, query: str, model: str) -> Optional[Dict[str, Any]]:
        """Make the actual API call to Gemini"""
        
        url = f"{self.base_url}/{model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": query}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.json() if response.text else "Unknown error"
                raise Exception(f"{response.status_code} - {error_detail}")
            
            data = response.json()
            
            # Extract the answer
            if "candidates" not in data or not data["candidates"]:
                raise Exception("No candidates in response")
            
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            
            logger.info("✅ Copilot response generated", model=model, chars=len(answer))
            
            return {
                "answer": answer.strip(),
                "model": model,
                "market_bias": "neutral",  # TODO: Implement sentiment analysis
                "sentiment_score": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return a standardized error response"""
        logger.error("❌ Copilot error", error=error_message)
        return {
            "answer": "I'm having trouble connecting right now. Please try again in a moment.",
            "error": error_message,
            "market_bias": "neutral",
            "sentiment_score": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def list_available_models(self) -> List[str]:
        """Debug method: List all available models"""
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params={"key": self.api_key},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                models = [
                    model["name"].replace("models/", "")
                    for model in data.get("models", [])
                    if "generateContent" in model.get("supportedGenerationMethods", [])
                ]
                
                logger.info("📋 Available models", count=len(models), models=models)
                return models
                
        except Exception as e:
            logger.error("Failed to list models", error=str(e))
            return []


# Singleton instance
_trading_copilot: Optional[TradingCopilot] = None

def get_trading_copilot() -> TradingCopilot:
    """Get or create the singleton TradingCopilot instance"""
    global _trading_copilot
    if _trading_copilot is None:
        _trading_copilot = TradingCopilot()
    return _trading_copilot