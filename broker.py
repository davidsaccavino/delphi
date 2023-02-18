import os
from dotenv import load_dotenv

from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))

# preparing order data
market_order_data = MarketOrderRequest(
                      symbol="AAPL",
                      qty=1,
                      side=OrderSide.BUY,
                      time_in_force=TimeInForce.DAY
                  )

# Market order
market_order = trading_client.submit_order(
                order_data=market_order_data
                )
