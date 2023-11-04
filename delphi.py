import os, json, pandas as pd, pandas_ta as ta
from dotenv import load_dotenv


# Prevent usage of exponential notation
pd.options.display.float_format = '{:,.4f}'.format

# Load environment variables
load_dotenv()

cwd = os.path.dirname(__file__)

# Fetch historical data from local json file
storedDataframe = pd.DataFrame()
def delphi(tickerName, timeframes):

    signals = {}

    for i in range(len(timeframes)):
        with open(f'{cwd}/json/{tickerName}_{timeframes[i]}_Historical_Values.json', 'r+') as f:
            storedDataframe = pd.DataFrame(json.load(f))
            

            # Calculate fast and slow exponential moving averages (EMAs)
            fast_ema = storedDataframe[["close"]].ewm(span=12, adjust=False).mean(numeric_only=True)
            slow_ema = storedDataframe[["close"]].ewm(span=26, adjust=False).mean(numeric_only=True)
            # Calculate Moving Average Convergence Divergence
            macd = fast_ema - slow_ema


            # Calculate the MACD signal
            signal_line = macd.ewm(span=9, adjust=False).mean()


            # Calculate the highest high and lowest low over the past 14 days
            highest_high = storedDataframe['high'].rolling(window=14).max()
            lowest_low = storedDataframe['low'].rolling(window=14).min()


            # Calculate %K, unsmoothed
            stochK = (storedDataframe['close'].iloc[-1] - lowest_low) / (highest_high - lowest_low)
            stochK = stochK * 100
            # Smooth %K
            stochK = stochK.rolling(window=3).mean()


            # Calculate %D
            stochD = stochK.rolling(window=3).mean()
            

            #Calculate Supertrend
            supertrend = ta.supertrend(high = storedDataframe['high'], low = storedDataframe['low'], close = storedDataframe['close'], length = 10, multiplier = 2, offset = -9)
            supertrend = supertrend.iloc[:-10, :]


            # Calculate 8-bar SMA
            sma = storedDataframe['close'].rolling(window=8).mean(numeric_only=True).dropna()


            # Start of: Logic gates for determining bullish or bearish sentiment


            # OBV Bullish/Bearish logic gates
            bullishOBV = storedValues[-1]['OnBalanceVolume'] > storedValues[-1]['Smoothing Line']
            bearishOBV = storedValues[-1]['OnBalanceVolume'] < storedValues[-1]['Smoothing Line']

            # macd Bullish/Bearish logic gates
            bullishMACD = macd['close'].iloc[-1] > singal_line['close'].iloc[-1] + 0.25
            bearishMACD = macd['close'].iloc[-1] < singal_line['close'].iloc[-1] - .05


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
            VOSTbuySignal = bullishSuperTrend and bullishOscillators and storedValues[-1]['close'] > eightSMA.iloc[-1]
            VOSTsellSignal = bearishSuperTrend and bearishOscillators and storedValues[-1]['close']  < eightSMA.iloc[-1]


            # Determine if currently in a "De-Risk Zone"
            deRisk = not VOSTsellSignal and (stochK.iloc[-1] < 55) or (storedValues[-1]['close'] < eightSMA.iloc[-1])


            # End of: Logic gates for determining bullish or bearish sentiment
            


            signals[timeframes[i]] = [VOSTbuySignal, VOSTsellSignal, deRisk]

    return signals

