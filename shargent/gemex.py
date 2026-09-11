from pathlib import Path
import os
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from kiteconnect.exceptions import TokenException, KiteException

# 1. Load environment variables directly from ~/.env
env_path = Path.home() / ".env"

if not env_path.exists():
    print(f"Error: Environment file not found at {env_path}")
    exit(1)

load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("ZERODHA_API_KEY")
ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

if not API_KEY or not ACCESS_TOKEN:
    print("Error: ZERODHA_API_KEY or ZERODHA_ACCESS_TOKEN missing in ~/.env")
    exit(1)


def main():
    # 2. Initialize KiteConnect SDK
    kite = KiteConnect(api_key=API_KEY)
    kite.set_access_token(ACCESS_TOKEN)

    try:
        print("=" * 50)
        print("ZERODHA KITE CONNECT SAMPLE APP")
        print("=" * 50)

        # A. Fetch User Profile
        profile = kite.profile()
        print(f"\nUser ID    : {profile.get('user_id')}")
        print(f"User Name  : {profile.get('user_name')}")
        print(f"Email      : {profile.get('email')}")
        print(f"Broker     : {profile.get('broker')}")

        # B. Fetch Margins / Available Funds
        margins = kite.margins(segment="equity")
        available_cash = margins.get("available", {}).get("cash", 0)
        net_balance = margins.get("net", 0)
        print(f"\nEquity Net Balance    : ₹{net_balance:,.2f}")
        print(f"Equity Available Cash : ₹{available_cash:,.2f}")

        # C. Fetch Account Holdings
        holdings = kite.holdings()
        print(f"\nTotal Portfolio Holdings: {len(holdings)}")
        if holdings:
            print("\nSample Holdings Breakdown:")
            for item in holdings[:5]:  # Display top 5 holdings
                tradingsymbol = item.get("tradingsymbol")
                qty = item.get("quantity")
                avg_price = item.get("average_price")
                last_price = item.get("last_price")
                pnl = item.get("pnl")
                print(
                    f" - {tradingsymbol:12s} | Qty: {qty:4d} | Avg: ₹{avg_price:8.2f} | LTP: ₹{last_price:8.2f} | P&L: ₹{pnl:,.2f}"
                )

        # D. Fetch Live Market Quote
        symbols = ["NSE:INFY", "NSE:RELIANCE"]
        quotes = kite.quote(symbols)
        print(f"\nLive Quotes:")
        for symbol, data in quotes.items():
            ltp = data.get("last_price")
            ohlc = data.get("ohlc", {})
            close = ohlc.get("close", 0)
            change = ltp - close if close else 0
            pct_change = (change / close * 100) if close else 0
            print(
                f" - {symbol:14s} | LTP: ₹{ltp:8.2f} | Change: {change:+.2f} ({pct_change:+.2f}%)"
            )

        print("\n" + "=" * 50)
        print("API test completed successfully!")
        print("=" * 50)

    except TokenException:
        print("\nToken Error: Your ZERODHA_ACCESS_TOKEN is invalid or expired.")
        print(
            "Access tokens expire daily at 6:00 AM IST. Please regenerate it."
        )

    except KiteException as e:
        print(f"\nKite API Error: {e.message} (Code: {e.code})")

    except Exception as e:
        print(f"\nUnexpected Error: {e}")


if __name__ == "__main__":
    main()
