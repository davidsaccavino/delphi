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


# Fetch historical data from local json file
storedDataframe = pd.DataFrame()
with open('./json/QQQ_Historical_Values.json', 'r+') as f:
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




# Calculate On-Balance-Volume
def getOBV():

    i = 0
    obv = []

    for i in range(len(storedDataframe['close'])):

        if i == 0:
            value = storedDataframe['OnBalanceVolume'][i]
            obv.append(value)


        elif storedDataframe['close'][i] > storedDataframe['close'][i - 1] :
            value = obv[-1] + storedDataframe['Volume'][i]
            obv.append(value)


        elif storedDataframe['close'][i] < storedDataframe['close'][i - 1]:
            value = obv[-1] - storedDataframe['Volume'][i]
            obv.append(value)


        elif storedDataframe['close'][i] == storedDataframe['close'][i - 1]:
            value = obv[-1]
            obv.append(value)

    return obv




# Calculate Smoothed Moving Average of OBV
def getOBVSMMA():

    obv_len = 8

    # 600678000 is the initial value of the OBV as it is the first value in the json file
    initial_ma = 600678000
    initial_smma = (initial_ma * (obv_len - 1) + storedDataframe['OnBalanceVolume'][obv_len]) / obv_len
    smma = [initial_smma]


    for i in range(1, len(storedDataframe['OnBalanceVolume'])):
        smma.append((smma[i - 1] * (obv_len - 1) + storedDataframe['OnBalanceVolume'][i]) / obv_len)


    return smma




def getStochastic():

    # Calculate the highest high and lowest low over the past 14 days
    highest_high = storedDataframe['high'].rolling(window=14).max()
    lowest_low = storedDataframe['low'].rolling(window=14).min()


    # Calculate %K, unsmoothed
    stochK = (storedDataframe['close'] - lowest_low) / (highest_high - lowest_low) * 100
    # Smooth %K
    stochK = stochK.rolling(window=3).mean()


    # Calculate %D
    stochD = stochK.rolling(window=3).mean()


    return round(stochK, 2), round(stochD, 2)




def getSuperTrend():
    supertrend = ta.supertrend(high = storedDataframe['high'], low = storedDataframe['low'], close = storedDataframe['close'], length = 11, multiplier = 3, offset = -10)
    return supertrend.iloc[:-11, :]




def get8BarSMA():
    sma = storedDataframe['close'].rolling(window=8).mean(numeric_only=True).dropna()

    return sma

