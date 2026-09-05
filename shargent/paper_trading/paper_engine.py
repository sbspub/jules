from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time
import json

class PaperPosition(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    product: str = "MIS"  # MIS for day trade, CNC for long term
    pnl: float = 0.0

class PaperTradeRecord(BaseModel):
    trade_id: str
    symbol: str
    action: str  # BUY or SELL
    quantity: int
    price: float
    timestamp: float
    product: str
    pnl_realized: float = 0.0
    strategy: str = "DAY_TRADE"
    reasoning: str = ""

class PaperEngine:
    def __init__(self, initial_balance: float = 100000.0):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: Dict[str, PaperPosition] = {}
        self.trade_history: List[PaperTradeRecord] = []
        self._trade_counter = 0

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Returns account balance, total portfolio value, and unrealized/realized PnL."""
        unrealized_pnl = sum(pos.pnl for pos in self.positions.values())
        realized_pnl = sum(trade.pnl_realized for trade in self.trade_history)
        total_equity = self.balance + sum(pos.quantity * pos.current_price for pos in self.positions.values())

        return {
            "cash_balance": round(self.balance, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "realized_pnl": round(realized_pnl, 2),
            "total_portfolio_value": round(total_equity, 2),
            "net_return_pct": round(((total_equity - self.initial_balance) / self.initial_balance) * 100.0, 2),
            "open_positions_count": len(self.positions),
            "total_trades_count": len(self.trade_history)
        }

    def execute_paper_trade(
        self,
        symbol: str,
        action: str,
        quantity: int,
        price: float,
        product: str = "MIS",
        strategy: str = "DAY_TRADE",
        reasoning: str = ""
    ) -> Dict[str, Any]:
        """Executes a virtual trade in the paper trading engine."""
        action = action.upper()
        if action not in ["BUY", "SELL"]:
            return {"status": "ERROR", "message": f"Invalid action: {action}"}

        trade_cost = quantity * price
        self._trade_counter += 1
        trade_id = f"PT_{int(time.time())}_{self._trade_counter}"

        realized_pnl = 0.0

        if action == "BUY":
            if self.balance < trade_cost:
                return {"status": "ERROR", "message": f"Insufficient paper cash: required {trade_cost}, available {self.balance}"}

            self.balance -= trade_cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                new_qty = pos.quantity + quantity
                new_avg = ((pos.quantity * pos.average_price) + trade_cost) / new_qty
                pos.quantity = new_qty
                pos.average_price = new_avg
                pos.current_price = price
                pos.pnl = (price - new_avg) * new_qty
            else:
                self.positions[symbol] = PaperPosition(
                    symbol=symbol,
                    quantity=quantity,
                    average_price=price,
                    current_price=price,
                    product=product,
                    pnl=0.0
                )

        elif action == "SELL":
            if symbol not in self.positions or self.positions[symbol].quantity < quantity:
                return {"status": "ERROR", "message": f"Cannot sell {quantity} of {symbol}; position size insufficient."}

            pos = self.positions[symbol]
            cost_basis = pos.average_price * quantity
            realized_pnl = (price * quantity) - cost_basis
            self.balance += (price * quantity)

            pos.quantity -= quantity
            if pos.quantity == 0:
                del self.positions[symbol]
            else:
                pos.pnl = (price - pos.average_price) * pos.quantity

        trade_record = PaperTradeRecord(
            trade_id=trade_id,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            timestamp=time.time(),
            product=product,
            pnl_realized=realized_pnl,
            strategy=strategy,
            reasoning=reasoning
        )
        self.trade_history.append(trade_record)

        return {
            "status": "SUCCESS",
            "trade_id": trade_id,
            "realized_pnl": round(realized_pnl, 2),
            "remaining_cash": round(self.balance, 2)
        }


class LearningMode:
    def __init__(self, paper_engine: PaperEngine):
        self.paper_engine = paper_engine

    def evaluate_performance(self) -> Dict[str, Any]:
        """Analyzes historical trades to output key statistics and insights for agent learning."""
        trades = self.paper_engine.trade_history
        if not trades:
            return {
                "total_trades": 0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0,
                "insights": ["No trades recorded yet in learning mode."]
            }

        winning_trades = [t for t in trades if t.pnl_realized > 0]
        losing_trades = [t for t in trades if t.pnl_realized < 0]

        total_wins = sum(t.pnl_realized for t in winning_trades)
        total_losses = abs(sum(t.pnl_realized for t in losing_trades))

        win_rate = (len(winning_trades) / len(trades)) * 100.0 if trades else 0.0
        profit_factor = round(total_wins / total_losses, 2) if total_losses > 0 else float("inf")

        insights = []
        if win_rate >= 60.0:
            insights.append("High win-rate strategy detected; model entry/exit timing is strong.")
        else:
            insights.append("Win rate is below 60%. Consider tightening technical indicator confirmation signals.")

        if total_losses > total_wins and len(losing_trades) > 0:
            insights.append("Losses exceed gains; enforce stricter stop-loss limits on day trading strategies.")

        return {
            "total_trades": len(trades),
            "winning_trades_count": len(winning_trades),
            "losing_trades_count": len(losing_trades),
            "win_rate_pct": round(win_rate, 2),
            "total_realized_profit": round(total_wins - total_losses, 2),
            "profit_factor": profit_factor,
            "insights": insights
        }
