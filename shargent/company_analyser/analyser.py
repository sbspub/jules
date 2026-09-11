from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os

class CompanyAnalysisResult(BaseModel):
    symbol: str
    pe_ratio: Optional[float] = Field(description="Price to Earnings ratio")
    pb_ratio: Optional[float] = Field(description="Price to Book ratio")
    debt_to_equity: Optional[float] = Field(description="Debt to Equity ratio")
    roe_pct: Optional[float] = Field(description="Return on Equity in percentage")
    revenue_growth_yo_y: Optional[float] = Field(description="YoY Revenue Growth %")
    profit_margin_pct: Optional[float] = Field(description="Net profit margin %")
    fundamental_score: float = Field(description="Score between 0 (very weak) and 100 (exceptionally strong)")
    financial_health: str = Field(description="STRONG, MODERATE, or WEAK")
    short_term_outlook: str = Field(description="BULLISH, NEUTRAL, or BEARISH")
    long_term_outlook: str = Field(description="BULLISH, NEUTRAL, or BEARISH")
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    summary: str

class CompanyAnalyser:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def analyze(self, symbol: str, financials: Dict[str, Any]) -> CompanyAnalysisResult:
        """
        Analyzes fundamental company financials, valuation ratios, and market performance.
        """
        pe = financials.get("pe_ratio")
        pb = financials.get("pb_ratio")
        de = financials.get("debt_to_equity")
        roe = financials.get("roe_pct")
        rev_growth = financials.get("revenue_growth_yo_y")
        profit_margin = financials.get("profit_margin_pct")

        # Fundamental score calculation algorithm
        score = 50.0
        strengths = []
        risks = []

        # ROE check
        if roe is not None and roe > 18:
            score += 15
            strengths.append(f"High Return on Equity ({roe}%)")
        elif roe is not None and roe < 8:
            score -= 15
            risks.append(f"Low Return on Equity ({roe}%)")

        # Debt to Equity check
        if de is not None and de < 0.5:
            score += 15
            strengths.append(f"Low Debt-to-Equity ratio ({de})")
        elif de is not None and de > 1.5:
            score -= 20
            risks.append(f"High Leverage / Debt-to-Equity ({de})")

        # Revenue growth
        if rev_growth is not None and rev_growth > 15:
            score += 10
            strengths.append(f"Strong YoY Revenue Growth ({rev_growth}%)")
        elif rev_growth is not None and rev_growth < 0:
            score -= 15
            risks.append(f"Declining Revenue Growth ({rev_growth}%)")

        # Valuation PE check
        if pe is not None and pe < 20:
            score += 10
            strengths.append(f"Attractive P/E ratio ({pe})")
        elif pe is not None and pe > 60:
            score -= 10
            risks.append(f"High P/E valuation multiple ({pe})")

        score = max(0.0, min(100.0, score))

        if score >= 70:
            health = "STRONG"
            long_outlook = "BULLISH"
            short_outlook = "BULLISH" if rev_growth is not None and rev_growth > 10 else "NEUTRAL"
        elif score >= 45:
            health = "MODERATE"
            long_outlook = "NEUTRAL"
            short_outlook = "NEUTRAL"
        else:
            health = "WEAK"
            long_outlook = "BEARISH"
            short_outlook = "BEARISH"

        summary = (
            f"{symbol} exhibits {health.lower()} financial health with a fundamental score of {score}/100. "
            f"Key metrics: P/E {pe}, Debt/Equity {de}, ROE {roe}%, Revenue Growth {rev_growth}%."
        )

        return CompanyAnalysisResult(
            symbol=symbol,
            pe_ratio=pe,
            pb_ratio=pb,
            debt_to_equity=de,
            roe_pct=roe,
            revenue_growth_yo_y=rev_growth,
            profit_margin_pct=profit_margin,
            fundamental_score=round(score, 1),
            financial_health=health,
            short_term_outlook=short_outlook,
            long_term_outlook=long_outlook,
            strengths=strengths or ["Stable core metrics"],
            risks=risks or ["No immediate major financial risks"],
            summary=summary
        )
