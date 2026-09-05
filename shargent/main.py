import sys
import os
import argparse
import json

from shargent.orchestrator.graph import TradingOrchestrator
from shargent.config import settings

def main():
    parser = argparse.ArgumentParser(description="Shargent Zerodha Agentic Trading System")
    parser.add_argument("--symbol", type=str, default="RELIANCE", help="Stock ticker symbol (e.g., RELIANCE, TCS, INFYS)")
    parser.add_argument("--strategy", type=str, default="AUTO_DAY_TRADE", choices=["AUTO_DAY_TRADE", "SHORT_TERM_TRADE", "LONG_TERM_INVESTMENT"], help="Trading strategy mode")
    parser.add_argument("--mode", type=str, default="PAPER", choices=["PAPER", "LIVE"], help="Execution mode (PAPER or LIVE)")
    parser.add_argument("--qty", type=int, default=10, help="Order quantity")

    args = parser.parse_args()

    print("=" * 60)
    print("      SHARGENT - ZERODHA AGENTIC TRADING SYSTEM")
    print("=" * 60)
    print(f"Target Symbol : {args.symbol}")
    print(f"Strategy Mode : {args.strategy}")
    print(f"Trading Mode  : {args.mode}")
    print(f"Order Quantity: {args.qty}")
    print("-" * 60)

    orchestrator = TradingOrchestrator()
    print("Running LangGraph agentic workflow...")

    result = orchestrator.run_strategy(
        symbol=args.symbol,
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
