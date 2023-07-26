import sys, os, json, delphi, datetime
from dotenv import load_dotenv


from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient

cwd = os.path.dirname(__file__)

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))
def broker(tickerName, indicators):
    with open(cwd + f'/json/{tickerName}_Historical_Values.json', 'r+') as f:
        storedValues = json.load(f)

    
    stochK = indicators["stochK"]
    stochD = indicators["stochD"]
    singal_line = indicators["signal_line"]
    macd = indicators['MACD']
    supertrend = indicators['supertrend']
    eightSMA = indicators['SMA']


    # Start of: Logic gates for determining bullish or bearish sentiment

    # OBV Bullish/Bearish logic gates
    bullishOBV = storedValues[-1]['OnBalanceVolume'] > storedValues[-1]['Smoothing Line']
    bearishOBV = storedValues[-1]['OnBalanceVolume'] < storedValues[-1]['Smoothing Line']

    # macd Bullish/Bearish logic gates
    bullishmacd = macd['close'].iloc[-1] > singal_line['close'].iloc[-1] + 0.25
    bearishmacd = macd['close'].iloc[-1] < singal_line['close'].iloc[-1] - .05


    # Stochastic Bullish/Bearish logic gates
    bullishStochastic = stochK.iloc[-1] > 60 and stochK.iloc[-1] > (stochD.iloc[-1] + 1.5)
    bearishStochastic = (stochK.iloc[-1] < 60 and stochD.iloc[-1] > (stochK.iloc[-1] + 1.5)) or stochK.iloc[-1] < 40

    # Aggregated Oscillator Bullish/Bearish logic gates
    bullishOscillators = bullishOBV and bullishStochastic and bullishmacd
    bearishOscillators = bearishOBV and bearishStochastic and bearishmacd

    # SuperTrend Bullish/Bearish logic gates
    bullishSuperTrend = supertrend.iloc[-1]["SUPERTd_10_2.0"] == 1 and (supertrend.iloc[-2]["SUPERTd_10_2.0"] == -1 or supertrend.iloc[-3]["SUPERTd_10_2.0"] == -1)
    bearishSuperTrend = supertrend.iloc[-1]["SUPERTd_10_2.0"] == -1 and (supertrend.iloc[-2]["SUPERTd_10_2.0"] == 1 or supertrend.iloc[-3]["SUPERTd_10_2.0"] == 1)

    # Volume-Oscillator-weighted SuperTrend buy and sell signals
    VOSTbuySignal = (bullishSuperTrend and bullishOscillators and storedValues[-1]['close'] > eightSMA.iloc[-1])
    VOSTsellSignal = (bearishSuperTrend and bearishOscillators and storedValues[-1]['close']  < eightSMA.iloc[-1])


    # Determine if currently in a "De-Risk Zone"
    deRisk = (not VOSTsellSignal) and ((stochK.iloc[-1] < 55) or (storedValues[-1]['close'] < eightSMA.iloc[-1]))

    # End of: Logic gates for determining bullish or bearish sentiment


    if VOSTbuySignal and not deRisk:

        market_order_data = MarketOrderRequest(
            symbol=f'{tickerName}',
            qty=1000,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )

        # Market order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        ) 
        print(f'{datetime.date()}\nVOST Buy Signal: Buying {tickerName}')
        sys.stdout.flush()


    if VOSTsellSignal:
        try:
            if(trading_client.get_open_position(f'{tickerName}')):
                market_order_data = MarketOrderRequest(
                    symbol=f'{tickerName}',
                    qty=1000,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )

                # Market order
                market_order = trading_client.submit_order(
                    order_data=market_order_data
                )
            
        except:
            pass


        # Market order
        market_order = trading_client.submit_order(
            order_data=market_order_data
        ) 
        print(f'{datetime.date()}\nVOST Sell Signal: Selling {tickerName}')
        sys.stdout.flush()


    if deRisk:
        try:
            if(trading_client.get_open_position(f'{tickerName}')):
                market_order_data = MarketOrderRequest(
                    symbol="f'{tickerName}'",
                    qty=1000,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )

                # Market order
                market_order = trading_client.submit_order(
                    order_data=market_order_data
                )
                
                print(f'{datetime.date()}\nDe-Risking {tickerName}')
                sys.stdout.flush()
        except:
            pass
        if not(deRisk) and not(VOSTbuySignal) and not(VOSTsellSignal):
            print(f'No action taken on {tickerName}. Current Time: {datetime.datetime.now()}')