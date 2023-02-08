import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd


from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))
data_client = StockHistoricalDataClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))


request_params = StockBarsRequest(
                        symbol_or_symbols=["QQQ"],
                        timeframe=TimeFrame.Day,
                        start=(datetime.now() + timedelta(days=-50)),
                        end=datetime.now(),
                        limit=26
                        )

bars = data_client.get_stock_bars(request_params).df



def getClosingPrices():
    
    closing_prices = pd.DataFrame({"Timestamps": [], "Closing Prices": []})
    i = 0

    for bar in bars.iloc[:,3]:
        
        # append new bars to "closing_prices" dataframe
        currentData = pd.DataFrame({'Timestamps': [bars.index[i][1].date()], 'Closing Prices': [bar]})
        closing_prices = pd.concat([closing_prices, currentData])

        i += 1

    return closing_prices



# Define Moving Average Convergence Divergence
def getMACD():
    closing_prices = getClosingPrices()

    # Calculate fast and slow exponential moving averages (EMAs)
    fast_ema = closing_prices[["Closing Prices"]].ewm(span=12, adjust=False).mean(numeric_only=True)
    slow_ema = closing_prices[["Closing Prices"]].ewm(span=26, adjust=False).mean(numeric_only=True)
    macd = fast_ema - slow_ema

    # Caclulate the signal line and MACD spread
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macdSpread = macd - signal_line


    return macd, signal_line, macdSpread






# preparing order data
# market_order_data = MarketOrderRequest(
#                       symbol="AAPL",
#                       qty=1,
#                       side=OrderSide.BUY,
#                       time_in_force=TimeInForce.DAY
#                   )

# # Market order
# market_order = trading_client.submit_order(
#                 order_data=market_order_data
#                 )
