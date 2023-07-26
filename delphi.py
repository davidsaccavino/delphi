import os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd
import pandas_ta as ta
import numpy as np

# Prevent usage of exponential notation
pd.options.display.float_format = '{:,.4f}'.format

# Load environment variables
load_dotenv()

cwd = os.path.dirname(__file__)

# Fetch historical data from local json file
storedDataframe = pd.DataFrame()
def delphi(tickerName):
    with open(f'{cwd}/json/{tickerName}_Historical_Values.json', 'r+') as f:
        storedDataframe = pd.DataFrame(json.load(f))

        indicators = {}
        


        # Calculate Moving Average Convergence Divergence

        # Calculate fast and slow exponential moving averages (EMAs)
        fast_ema = storedDataframe[["close"]].ewm(span=12, adjust=False).mean(numeric_only=True)
        slow_ema = storedDataframe[["close"]].ewm(span=26, adjust=False).mean(numeric_only=True)
        macd = fast_ema - slow_ema


        # Caclulate the signal line and MACD spread
        signal_line = macd.ewm(span=9, adjust=False).mean()


        indicators["MACD"] = macd
        indicators["signal_line"] = signal_line



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

        indicators["stochK"] = round(stochK, 2)
        indicators["stockD"] = round(stochD, 2)
        




        #Calculate Supertrend
        supertrend = ta.supertrend(high = storedDataframe['high'], low = storedDataframe['low'], close = storedDataframe['close'], length = 10, multiplier = 2, offset = -9)
        indicators["supertrend"] = supertrend.iloc[:-10, :]




        # Calculate 8-bar SMA
        sma = storedDataframe['close'].rolling(window=8).mean(numeric_only=True).dropna()

        indicators['sma'] = sma

    return indicators

