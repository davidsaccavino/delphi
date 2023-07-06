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
with open(cwd + '/json/QQQ_Historical_Values.json', 'r+') as f:
    storedDataframe = pd.DataFrame(json.load(f))



# Calculate Moving Average Convergence Divergence
def getMACD():

    # Calculate fast and slow exponential moving averages (EMAs)
    fast_ema = storedDataframe[["close"]].ewm(span=12, adjust=False).mean(numeric_only=True)
    slow_ema = storedDataframe[["close"]].ewm(span=26, adjust=False).mean(numeric_only=True)
    macd = fast_ema - slow_ema


    # Caclulate the signal line and MACD spread
    signal_line = macd.ewm(span=9, adjust=False).mean()


    return macd, signal_line


def getStochastic():

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


    return round(stochK, 2), round(stochD, 2)




def getSuperTrend():
    supertrend = ta.supertrend(high = storedDataframe['high'], low = storedDataframe['low'], close = storedDataframe['close'], length = 10, multiplier = 2, offset = -9)
    return supertrend.iloc[:-10, :]




def get8BarSMA():
    sma = storedDataframe['close'].rolling(window=8).mean(numeric_only=True).dropna()

    return sma

