import os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd
import numpy as np
pd.options.display.float_format = '{:,.4f}'.format



load_dotenv()


storedValues = {}
storedDataframe = pd.DataFrame()
with open('QQQ_Historical_Values.json', 'r+') as f:
    storedValues = json.load(f)
    storedDataframe = pd.DataFrame(storedValues)







# Calculate Moving Average Convergence Divergence
def getMACD():
    # closing_prices = getClosingPrices()

    # Calculate fast and slow exponential moving averages (EMAs)
    fast_ema = storedDataframe[["close"]].ewm(span=12, adjust=False).mean(numeric_only=True)
    slow_ema = storedDataframe[["close"]].ewm(span=26, adjust=False).mean(numeric_only=True)
    macd = fast_ema - slow_ema

    # Caclulate the signal line and MACD spread
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macdSpread = macd - signal_line


    return macdSpread

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

    initial_ma = 600678000
    initial_smma = (initial_ma * (obv_len - 1) + storedDataframe['OnBalanceVolume'][obv_len]) / obv_len
    smma = [initial_smma]

    for i in range(1, len(storedDataframe['OnBalanceVolume'])):
        smma.append((smma[i - 1] * (obv_len - 1) + storedDataframe['OnBalanceVolume'][i]) / obv_len)

    return smma

