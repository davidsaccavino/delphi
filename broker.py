import os, json, delphi
from dotenv import load_dotenv


from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))

with open('./json/QQQ_Historical_Values.json', 'r+') as f:
    storedValues = json.load(f)


stochK, stochD = delphi.getStochastic()
macdLine, signalLine = delphi.getMACD()
supertrend = delphi.getSuperTrend()
eightSMA = delphi.get8BarSMA()


# Start of: Logic gates for determining bullish or bearish sentiment

# OBV Bullish/Bearish logic gates
bullishOBV = storedValues[-1]['OnBalanceVolume'] > storedValues[-1]['Smoothing Line']
bearishOBV = storedValues[-1]['OnBalanceVolume'] < storedValues[-1]['Smoothing Line']

# MACD Bullish/Bearish logic gates
bullishMACD = macdLine['close'].iloc[-1] > signalLine['close'].iloc[-1] + 0.25
bearishMACD = macdLine['close'].iloc[-1] < signalLine['close'].iloc[-1] - .05


# Stochastic Bullish/Bearish logic gates
bullishStochastic = stochK.iloc[-1] > 60 and stochK.iloc[-1] > (stochD.iloc[-1] + 1.5)
bearishStochastic = (stochK.iloc[-1] < 60 and stochD.iloc[-1] > (stochK.iloc[-1] + 1.5)) or stochK.iloc[-1] < 40

# Aggregated Oscillator Bullish/Bearish logic gates
bullishOscillators = bullishOBV and bullishStochastic and bullishMACD
bearishOscillators = bearishOBV and bearishStochastic and bearishMACD

# SuperTrend Bullish/Bearish logic gates
bullishSuperTrend = supertrend.iloc[-1]["SUPERTd_10_2.0"] == 1 and (supertrend.iloc[-2]["SUPERTd_10_2.0"] == -1 or supertrend.iloc[-3]["SUPERTd_10_2.0"] == -1)
bearishSuperTrend = supertrend.iloc[-1]["SUPERTd_10_2.0"] == -1 and (supertrend.iloc[-2]["SUPERTd_10_2.0"] == 1 or supertrend.iloc[-3]["SUPERTd_10_2.0"] == 1)

# Volume-Oscillator-weighted SuperTrend buy and sell signals
VOSTbuySignal = (bullishSuperTrend and bullishOscillators and storedValues[-1]['close'] > eightSMA.iloc[-1])
VOSTsellSignal = (bearishSuperTrend and bearishOscillators and storedValues[-1]['close']  < eightSMA.iloc[-1])


# Determine if currently in a "De-Risk Zone"
deRisk = (not VOSTsellSignal) and (stochK.iloc[-1] < 55 or storedValues[-1]['close'] < eightSMA)

# End of: Logic gates for determining bullish or bearish sentiment


if VOSTbuySignal and not deRisk:
    try:
        if(trading_client.get_open_position("SQQQ")):
            market_order_data = MarketOrderRequest(
                symbol="SQQQ",
                qty=1,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            # Market order
            market_order = trading_client.submit_order(
                order_data=market_order_data
            )
        
    except:
        pass

    market_order_data = MarketOrderRequest(
        symbol="TQQQ",
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
    ) 



if VOSTsellSignal:
    try:
        if(trading_client.get_open_position("TQQQ")):
            market_order_data = MarketOrderRequest(
                symbol="TQQQ",
                qty=1,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            # Market order
            market_order = trading_client.submit_order(
                order_data=market_order_data
            )
        
    except:
        pass

    market_order_data = MarketOrderRequest(
        symbol="SQQQ",
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
    ) 


if deRisk:
    try:
        if(trading_client.get_open_position("TQQQ")):
            market_order_data = MarketOrderRequest(
                symbol="TQQQ",
                qty=1,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )

            # Market order
            market_order = trading_client.submit_order(
                order_data=market_order_data
            )
    except:
        pass