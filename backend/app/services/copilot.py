import google.generativeai as genai
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.data_fetcher import DataFetcher
from app.services.technical_analysis import TechnicalAnalysis
from app.services.sentiment_analysis import SentimentAnalysis
from app.services.risk_management import RiskManagement

class TradingCopilot:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.data_fetcher = DataFetcher()
        self.technical_analysis = TechnicalAnalysis()
        self.sentiment_analysis = SentimentAnalysis()
        self.risk_management = RiskManagement()

    async def get_insights(self, symbol: str, user_context: Optional[Dict] = None) -> Dict:
        """Get AI-powered trading insights for a symbol."""
        try:
            # Gather data
            current_price = await self.data_fetcher.get_current_price(symbol)
            historical_data = await self.data_fetcher.get_historical_data(symbol)
            news_data = await self.data_fetcher.get_news_data(symbol)

            insights = {
                "symbol": symbol,
                "current_price": current_price,
                "recommendation": "HOLD",
                "confidence": 0.5,
                "analysis": {},
                "risk_assessment": {},
                "suggestions": []
            }

            if historical_data is not None and not historical_data.empty:
                # Technical analysis
                technical_indicators = self.technical_analysis.calculate_indicators(historical_data)
                insights["analysis"]["technical"] = {
                    "rsi": technical_indicators['rsi'].iloc[-1] if not technical_indicators['rsi'].empty else None,
                    "macd_signal": "BUY" if technical_indicators['macd'].iloc[-1] > technical_indicators['macd_signal'].iloc[-1] else "SELL",
                    "bollinger_position": "ABOVE" if current_price > technical_indicators['bollinger_upper'].iloc[-1] else "BELOW" if current_price < technical_indicators['bollinger_lower'].iloc[-1] else "MIDDLE"
                }

            # Sentiment analysis
            if news_data:
                sentiment = self.sentiment_analysis.analyze_text(news_data)
                insights["analysis"]["sentiment"] = sentiment

            # Risk assessment
            if historical_data is not None and not historical_data.empty:
                returns = historical_data['Close'].pct_change().dropna().tolist()
                risk_metrics = self.risk_management.calculate_risk_metrics(returns)
                insights["risk_assessment"] = risk_metrics

            # Generate AI recommendation using Gemini
            prompt = self._build_insights_prompt(symbol, insights, user_context)
            response = self.model.generate_content(prompt)
            ai_insights = self._parse_ai_response(response.text)

            insights.update(ai_insights)

            return insights

        except Exception as e:
            return {
                "symbol": symbol,
                "error": f"Failed to generate insights: {str(e)}",
                "recommendation": "HOLD",
                "confidence": 0.0
            }

    async def answer_question(self, question: str, context: Optional[Dict] = None) -> str:
        """Answer trading-related questions using AI."""
        try:
            prompt = self._build_qa_prompt(question, context)
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Sorry, I couldn't process your question: {str(e)}"

    async def generate_strategy(self, user_profile: Dict) -> Dict:
        """Generate personalized trading strategy based on user profile."""
        try:
            prompt = self._build_strategy_prompt(user_profile)
            response = self.model.generate_content(prompt)
            strategy = self._parse_strategy_response(response.text)

            return strategy
        except Exception as e:
            return {
                "strategy_name": "Conservative Hold",
                "description": "Hold current positions and wait for better opportunities",
                "risk_level": "LOW",
                "time_horizon": "LONG",
                "error": str(e)
            }

    def _build_insights_prompt(self, symbol: str, insights: Dict, user_context: Optional[Dict]) -> str:
        """Build prompt for AI insights generation."""
        prompt = f"""
        As a trading copilot AI, analyze the following data for {symbol} and provide trading insights:

        Current Price: ${insights.get('current_price', 'N/A')}

        Technical Analysis:
        - RSI: {insights.get('analysis', {}).get('technical', {}).get('rsi', 'N/A')}
        - MACD Signal: {insights.get('analysis', {}).get('technical', {}).get('macd_signal', 'N/A')}
        - Bollinger Position: {insights.get('analysis', {}).get('technical', {}).get('bollinger_position', 'N/A')}

        Sentiment Analysis:
        - Score: {insights.get('analysis', {}).get('sentiment', {}).get('sentiment_score', 'N/A')}
        - Label: {insights.get('analysis', {}).get('sentiment', {}).get('sentiment_label', 'N/A')}

        Risk Metrics:
        - Sharpe Ratio: {insights.get('risk_assessment', {}).get('sharpe_ratio', 'N/A')}
        - Max Drawdown: {insights.get('risk_assessment', {}).get('max_drawdown', 'N/A')}

        {f"User Context: {user_context}" if user_context else ""}

        Provide a JSON response with:
        - recommendation: "BUY", "SELL", or "HOLD"
        - confidence: 0.0 to 1.0
        - reasoning: brief explanation
        - suggestions: array of actionable advice
        """

        return prompt

    def _build_qa_prompt(self, question: str, context: Optional[Dict]) -> str:
        """Build prompt for question answering."""
        prompt = f"""
        You are a trading copilot AI assistant. Answer the following trading-related question helpfully and accurately.

        Question: {question}

        {f"Additional Context: {context}" if context else ""}

        Provide a clear, concise answer focusing on trading concepts, strategies, and market analysis.
        """

        return prompt

    def _build_strategy_prompt(self, user_profile: Dict) -> str:
        """Build prompt for strategy generation."""
        prompt = f"""
        As a trading copilot, create a personalized trading strategy based on this user profile:

        Risk Tolerance: {user_profile.get('risk_tolerance', 'MEDIUM')}
        Investment Amount: ${user_profile.get('investment_amount', 'N/A')}
        Time Horizon: {user_profile.get('time_horizon', 'MEDIUM')}
        Experience Level: {user_profile.get('experience', 'INTERMEDIATE')}
        Preferred Sectors: {user_profile.get('sectors', 'DIVERSIFIED')}

        Generate a JSON response with:
        - strategy_name: catchy name for the strategy
        - description: brief overview
        - risk_level: "LOW", "MEDIUM", "HIGH"
        - time_horizon: "SHORT", "MEDIUM", "LONG"
        - key_principles: array of main strategy rules
        - suggested_allocations: object with sector/asset allocations
        """

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format."""
        try:
            # Simple JSON extraction (in production, use proper JSON parsing)
            import json
            # Clean the response to extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass

        # Fallback parsing
        return {
            "recommendation": "HOLD",
            "confidence": 0.5,
            "reasoning": response_text[:200] + "...",
            "suggestions": ["Monitor price movements", "Check news regularly"]
        }

    def _parse_strategy_response(self, response_text: str) -> Dict:
        """Parse strategy response."""
        try:
            import json
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            pass

        return {
            "strategy_name": "Balanced Growth",
            "description": "A balanced approach to growth investing",
            "risk_level": "MEDIUM",
            "time_horizon": "MEDIUM",
            "key_principles": ["Diversify across sectors", "Focus on fundamentals"],
            "suggested_allocations": {"stocks": 60, "bonds": 30, "cash": 10}
        }
