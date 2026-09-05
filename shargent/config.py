import os
from typing import Optional
from pydantic import BaseModel, Field

class Settings(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "mock_key"))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    # Zerodha settings
    zerodha_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ZERODHA_API_KEY", None))
    zerodha_api_secret: Optional[str] = Field(default_factory=lambda: os.getenv("ZERODHA_API_SECRET", None))
    zerodha_access_token: Optional[str] = Field(default_factory=lambda: os.getenv("ZERODHA_ACCESS_TOKEN", None))

    # Execution mode
    trading_mode: str = Field(default="PAPER", description="PAPER or LIVE")

    # Risk parameters
    max_capital_per_trade_pct: float = 0.10  # 10% max capital per position
    stop_loss_pct: float = 0.02              # 2% stop loss
    target_profit_pct: float = 0.05          # 5% profit target
    initial_paper_balance: float = 100000.0  # 1 Lakh INR starting paper balance

settings = Settings()
