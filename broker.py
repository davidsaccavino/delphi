import os
from dotenv import load_dotenv
import delphi
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))



obv = delphi.getOBV()
smma = delphi.getOBVSMMA()
stochK, stochD = delphi.getStochastic()
macdLine, signalLine = delphi.getMACD()
supertrend = delphi.getSuperTrend()
eightSMA = delphi.get8BarSMA()


# Start of: Logic gates for determining bullish or bearish sentiment

# OBV Bullish/Bearish logic gates
bullishOBV = obv[-1] > smma[-1]
bearishOBV = obv[-1] < smma[-1]

# MACD Bullish/Bearish logic gates
bullishMACD = macdLine.iloc[-1] > signalLine.iloc[-1] + 0.25
bearishMACD = macdLine.iloc[-1] < signalLine.iloc[-1] - .05

# Stochastic Bullish/Bearish logic gates
bullishStochastic = stochK.iloc[-1] > 60 and stochK.iloc[-1] > (stochD.iloc[-1] + 1.5)
bearishStochastic = (stochK.iloc[-1] < 60 and stochD.iloc[-1] > (stochK.iloc[-1] + 1.5)) or stochK.iloc[-1] < 40

# Aggregated Oscillator Bullish/Bearish logic gates
bullishOscillators = bullishOBV and bullishStochastic and bullishMACD
bearishOscillators = bearishOBV and bearishStochastic and bearishMACD

# Volume-Oscillator-weighted SuperTrend buy and sell signals
VOSTbuySignal = (supertrend.iloc[-1]["SUPERTd_11_3.0"] == 1 and bullishOscillators and delphi.storedDataframe['close'].iloc[-1] > eightSMA.iloc[-1])
VOSTsellSignal = (supertrend.iloc[-1]["SUPERTd_11_3.0"] == -1 and supertrend.iloc[-2]["SUPERTd_11_3.0"] == 1 and bearishOscillators and delphi.storedDataframe['close'].iloc[-1]  < eightSMA.iloc[-1])

# print(supertrend[:-1])
# Determine if currently in a "De-Risk Zone"
deRisk = (not VOSTsellSignal) and (stochK.iloc[-1] < 55 or delphi.storedDataframe['close'].iloc[-1] < eightSMA)

# End of: Logic gates for determining bullish or bearish sentiment


# preparing order data
if VOSTbuySignal and not deRisk:
    market_order_data = MarketOrderRequest(
        symbol="QQQ",
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

        # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
        )



if VOSTsellSignal:
    market_order_data = MarketOrderRequest(
        symbol="QQQ",
        qty=1,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
        )


if deRisk:
    market_order_data = MarketOrderRequest(
        symbol="QQQ",
        qty=1,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
        )