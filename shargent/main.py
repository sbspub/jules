import sys
import os
import argparse
import json

from shargent.orchestrator.graph import TradingOrchestrator
from shargent.config import settings

def main():
    parser = argparse.ArgumentParser(description="Shargent Zerodha Agentic Trading System")
    parser.add_argument("ticker_pos", nargs="?", default=None, metavar="TICKER", help="Stock ticker symbol (e.g., SBIN, RELIANCE, TCS)")
    parser.add_argument("--symbol", "-s", type=str, default=None, help="Stock ticker symbol (e.g., RELIANCE, TCS, SBIN)")
    parser.add_argument("--ticker", "-t", type=str, default=None, help="Stock ticker symbol (e.g., RELIANCE, TCS, SBIN)")
    parser.add_argument("--strategy", type=str, default="AUTO_DAY_TRADE", choices=["AUTO_DAY_TRADE", "SHORT_TERM_TRADE", "LONG_TERM_INVESTMENT"], help="Trading strategy mode")
    parser.add_argument("--mode", type=str, default="PAPER", choices=["PAPER", "LIVE"], help="Execution mode (PAPER or LIVE)")
    parser.add_argument("--qty", type=int, default=10, help="Order quantity")

    args = parser.parse_args()
    symbol = (args.ticker_pos or args.ticker or args.symbol or "RELIANCE").upper()

    print("=" * 60)
    print("      SHARGENT - ZERODHA AGENTIC TRADING SYSTEM")
    print("=" * 60)
    print(f"Target Symbol : {symbol}")
    print(f"Strategy Mode : {args.strategy}")
    print(f"Trading Mode  : {args.mode}")
    print(f"Order Quantity: {args.qty}")
    print("-" * 60)

    orchestrator = TradingOrchestrator()

    # Fetch and print live or mock market quote / OHLC data for the symbol
    quote_res = orchestrator.zerodha_client.get_quote([symbol])
    formatted_key = symbol if ":" in symbol else f"NSE:{symbol}"
    quote_data = quote_res.get(formatted_key) or quote_res.get(symbol) or (list(quote_res.values())[0] if quote_res else {})
    ohlc = quote_data.get("ohlc", {})

    print("\n[0] MARKET QUOTE / DAY'S OHLC:")
    print(f"    Symbol    : {symbol}")
    print(f"    Open      : {ohlc.get('open', 'N/A')}")
    print(f"    High      : {ohlc.get('high', 'N/A')}")
    print(f"    Low       : {ohlc.get('low', 'N/A')}")
    print(f"    Close     : {ohlc.get('close', 'N/A')}")
    print(f"    Last Price: {quote_data.get('last_price', 'N/A')}")
    print(f"    Volume    : {quote_data.get('volume', 'N/A')}")

    print("\nRunning LangGraph agentic workflow...")

    result = orchestrator.run_strategy(
        symbol=symbol,
        strategy_mode=args.strategy,
        trading_mode=args.mode,
        quantity=args.qty
    )

    print("\n[1] NEWS ANALYSIS SUMMARY:")
    news_res = result.get("news_result") or {}
    print(f"    Sentiment: {news_res.get('overall_sentiment')} (Score: {news_res.get('sentiment_score')})")
    print(f"    Recommendation: {news_res.get('trading_recommendation')}")

    print("\n[2] COMPANY FUNDAMENTAL ANALYSIS:")
    comp_res = result.get("company_result") or {}
    print(f"    Health: {comp_res.get('financial_health')} (Score: {comp_res.get('fundamental_score')}/100)")
    print(f"    P/E Ratio: {comp_res.get('pe_ratio')}, ROE: {comp_res.get('roe_pct')}%")

    print("\n[3] TECHNICAL ANALYSIS:")
    tech_res = result.get("technical_result") or {}
    print(f"    Price: {tech_res.get('current_price')} | RSI: {tech_res.get('rsi_14')} | MACD: {tech_res.get('macd_signal')}")
    print(f"    Short Term Signal: {tech_res.get('short_term_signal')} | Long Term Signal: {tech_res.get('long_term_signal')}")

    print("\n[4] FINAL AGENT DECISION:")
    print(f"    Decision : {result.get('final_decision')}")
    print(f"    Reasoning: {result.get('decision_reasoning')}")

    print("\n[5] EXECUTION RESULT:")
    print(f"    Details: {json.dumps(result.get('execution_result'), indent=2)}")

    print("\n[6] PAPER PORTFOLIO & LEARNING SUMMARY:")
    p_summary = orchestrator.paper_engine.get_portfolio_summary()
    print(f"    Cash Balance: {p_summary.get('cash_balance')}")
    print(f"    Total Portfolio Value: {p_summary.get('total_portfolio_value')}")

    perf = orchestrator.learning_mode.evaluate_performance()
    print(f"    Win Rate: {perf.get('win_rate_pct')}% | Insights: {perf.get('insights')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
