from typing import Dict, Any, List, Optional, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END

from shargent.news_analyser.analyser import NewsAnalyser, NewsAnalysisResult
from shargent.company_analyser.analyser import CompanyAnalyser, CompanyAnalysisResult
from shargent.technical_analyser.analyser import TechnicalAnalyser, TechnicalAnalysisResult
from shargent.zerodha_trading.zerodha_client import ZerodhaClient
from shargent.paper_trading.paper_engine import PaperEngine, LearningMode
from shargent.config import settings
from shargent.real_data import fetch_fundamentals, fetch_news

class AgentState(TypedDict):
    symbol: str
    strategy_mode: str  # AUTO_DAY_TRADE, SHORT_TERM_TRADE, LONG_TERM_INVESTMENT
    trading_mode: str   # PAPER or LIVE
    quantity: int
    news_items: List[Dict[str, Any]]
    financials: Dict[str, Any]
    price_history: List[Dict[str, Any]]

    # Analysis outputs
    news_result: Optional[Dict[str, Any]]
    company_result: Optional[Dict[str, Any]]
    technical_result: Optional[Dict[str, Any]]

    # Decision output
    final_decision: Optional[str]  # BUY, SELL, or HOLD
    decision_reasoning: Optional[str]

    # Order execution output
    execution_result: Optional[Dict[str, Any]]

class TradingOrchestrator:
    def __init__(self, zerodha_client: Optional[ZerodhaClient] = None, paper_engine: Optional[PaperEngine] = None):
        self.zerodha_client = zerodha_client or ZerodhaClient()
        self.paper_engine = paper_engine or PaperEngine()
        self.learning_mode = LearningMode(self.paper_engine)

        self.news_analyser = NewsAnalyser(api_key=settings.openai_api_key, model=settings.openai_model)
        self.company_analyser = CompanyAnalyser(api_key=settings.openai_api_key, model=settings.openai_model)
        self.technical_analyser = TechnicalAnalyser()

        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)

        # Add Nodes
        builder.add_node("analyze_news", self._analyze_news_node)
        builder.add_node("analyze_company", self._analyze_company_node)
        builder.add_node("analyze_technical", self._analyze_technical_node)
        builder.add_node("synthesize_decision", self._synthesize_decision_node)
        builder.add_node("execute_trade", self._execute_trade_node)

        # Graph Edges
        builder.set_entry_point("analyze_news")
        builder.add_edge("analyze_news", "analyze_company")
        builder.add_edge("analyze_company", "analyze_technical")
        builder.add_edge("analyze_technical", "synthesize_decision")
        builder.add_edge("synthesize_decision", "execute_trade")
        builder.add_edge("execute_trade", END)

        return builder.compile()

    def _analyze_news_node(self, state: AgentState) -> Dict[str, Any]:
        symbol = state.get("symbol", "RELIANCE")
        news_items = state.get("news_items", [])
        result = self.news_analyser.analyze(symbol, news_items)
        return {"news_result": result.model_dump()}

    def _analyze_company_node(self, state: AgentState) -> Dict[str, Any]:
        symbol = state.get("symbol", "RELIANCE")
        financials = state.get("financials", {})
        result = self.company_analyser.analyze(symbol, financials)
        return {"company_result": result.model_dump()}

    def _analyze_technical_node(self, state: AgentState) -> Dict[str, Any]:
        symbol = state.get("symbol", "RELIANCE")
        price_history = state.get("price_history", [])
        result = self.technical_analyser.analyze(symbol, price_history)
        return {"technical_result": result.model_dump()}

    def _synthesize_decision_node(self, state: AgentState) -> Dict[str, Any]:
        strategy = state.get("strategy_mode", "AUTO_DAY_TRADE")
        news = state.get("news_result") or {}
        company = state.get("company_result") or {}
        tech = state.get("technical_result") or {}

        decision = "HOLD"
        reasoning = []

        if strategy in ["AUTO_DAY_TRADE", "SHORT_TERM_TRADE"]:
            # Prioritize Technical analysis and Short term news
            st_tech = tech.get("short_term_signal", "HOLD")
            news_sent = news.get("overall_sentiment", "NEUTRAL")

            if st_tech == "BUY" and news_sent in ["BULLISH", "NEUTRAL"]:
                decision = "BUY"
                reasoning.append(f"Short term technical buy signal (RSI: {tech.get('rsi_14')}, MACD: {tech.get('macd_signal')}) aligned with {news_sent} news sentiment.")
            elif st_tech == "SELL" or news_sent == "BEARISH":
                decision = "SELL"
                reasoning.append(f"Bearish signal triggered (Tech: {st_tech}, News: {news_sent}).")
            else:
                decision = "HOLD"
                reasoning.append("Mixed or neutral indicators for day/short-term trade.")

        elif strategy == "LONG_TERM_INVESTMENT":
            # Prioritize Fundamental analysis and Long term technical trend
            health = company.get("financial_health", "MODERATE")
            score = company.get("fundamental_score", 50.0)
            lt_tech = tech.get("long_term_signal", "HOLD")

            if score >= 65 and health == "STRONG" and lt_tech in ["BUY", "HOLD"]:
                decision = "BUY"
                reasoning.append(f"Strong company fundamentals (Score: {score}/100, Health: {health}) and favourable long-term trend.")
            elif score < 40 or health == "WEAK":
                decision = "SELL"
                reasoning.append(f"Weak fundamental metrics (Score: {score}/100, Health: {health}).")
            else:
                decision = "HOLD"
                reasoning.append("Fundamental metrics acceptable but not at top buy conviction threshold.")

        return {
            "final_decision": decision,
            "decision_reasoning": " | ".join(reasoning)
        }

    def _execute_trade_node(self, state: AgentState) -> Dict[str, Any]:
        decision = state.get("final_decision", "HOLD")
        symbol = state.get("symbol", "RELIANCE")
        qty = state.get("quantity", 10)
        mode = state.get("trading_mode", settings.trading_mode)
        strategy = state.get("strategy_mode", "AUTO_DAY_TRADE")
        reasoning = state.get("decision_reasoning", "")
        tech = state.get("technical_result") or {}
        price = tech.get("current_price", 2500.0)

        product = "CNC" if strategy == "LONG_TERM_INVESTMENT" else "MIS"

        if decision not in ["BUY", "SELL"]:
            return {
                "execution_result": {
                    "status": "SKIPPED",
                    "message": f"No order placed since decision is {decision}"
                }
            }

        if mode.upper() == "LIVE":
            exec_res = self.zerodha_client.place_order(
                symbol=symbol,
                transaction_type=decision,
                quantity=qty,
                order_type="MARKET",
                product=product
            )
        else:
            exec_res = self.paper_engine.execute_paper_trade(
                symbol=symbol,
                action=decision,
                quantity=qty,
                price=price,
                product=product,
                strategy=strategy,
                reasoning=reasoning
            )

        return {"execution_result": exec_res}

    def run_strategy(
        self,
        symbol: str,
        strategy_mode: str = "AUTO_DAY_TRADE",
        trading_mode: str = "PAPER",
        quantity: int = 10,
        news_items: Optional[List[Dict[str, Any]]] = None,
        financials: Optional[Dict[str, Any]] = None,
        price_history: Optional[List[Dict[str, Any]]] = None
    ) -> AgentState:
        """Runs the agentic graph end-to-end."""
        formatted_key = symbol if ":" in symbol else f"NSE:{symbol}"
        quotes = self.zerodha_client.get_quote([symbol])
        q_data = quotes.get(formatted_key) or quotes.get(symbol) or (list(quotes.values())[0] if quotes else {})
        current_price = float(q_data.get("last_price", 0.0))

        if price_history is None:
            price_history = self.zerodha_client.get_daily_history(symbol)

        # Mock clients are explicit test fixtures. Normal paper and live modes
        # must acquire news and fundamental inputs rather than inventing them.
        is_mock_client = getattr(self.zerodha_client, "api_key", "").startswith("mock")
        if news_items is None:
            news_items = [] if is_mock_client else fetch_news(symbol)
        if financials is None:
            financials = {} if is_mock_client else fetch_fundamentals(symbol, current_price)

        initial_state: AgentState = {
            "symbol": symbol,
            "strategy_mode": strategy_mode,
            "trading_mode": trading_mode,
            "quantity": quantity,
            "news_items": news_items,
            "financials": financials,
            "price_history": price_history,
            "news_result": None,
            "company_result": None,
            "technical_result": None,
            "final_decision": None,
            "decision_reasoning": None,
            "execution_result": None
        }

        output_state = self.graph.invoke(initial_state)
        return output_state
