import os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd
import numpy as np

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

pd.options.display.float_format = '{:,.4f}'.format



   


storedValues = {}
storedDataframe = pd.DataFrame()
with open('./json/QQQ_Historical_Values.json', 'r+') as f:
    storedValues = json.load(f)
    storedDataframe = pd.DataFrame(storedValues)


    data_client = StockHistoricalDataClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))
    startDate = storedValues[-1]['time']
    startDate = startDate[:10]

    startDate = datetime.strptime(startDate, '%Y-%M-%d') + timedelta(weeks=4, days=4)

    request_params = StockBarsRequest(
                            symbol_or_symbols=["QQQ"],
                            timeframe=TimeFrame.Day,
                            start=startDate,
                    )
    bars = data_client.get_stock_bars(request_params)

    bars_df = bars.df
    bars_df.rename(index={1: 'time'}, columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'Volume'}, inplace=True)
    bars_df.index.names = ['symbol', 'time']


 
    bars_df['time'] = (bars_df.index).get_level_values(1).astype(str)
    storedDataframe = storedDataframe.append(bars_df, ignore_index=True)

    
    
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



  
    obv = getOBV()

    def getOBVSMMA():
        obv_len = 8
        initialSMMA =  storedValues[-1]['Smoothing Line']
        
        smma = [initialSMMA]

        length = len(storedDataframe) - len(storedValues)

        for i in range(0, length):
            smma.append(round((smma[i] * (obv_len - 1) + obv[len(storedValues) + i]) / obv_len))

        return smma[1:]



        

    smma = getOBVSMMA()

    jsonChunk = []
    for i in range(len(storedDataframe['close'])):
        
        #format time to match json
        time = storedDataframe['time'].iloc[i]
        time = time[:10]
        if(i < len(storedValues)):
            currentSMMA = storedValues[i]['Smoothing Line']
        else:
            currentSMMA = smma[i - len(storedValues)]

        jsonChunk.append({
        'time' : time,
        'open' : storedDataframe['open'].iloc[i],
        'high' : storedDataframe['high'].iloc[i],
        'low' : storedDataframe['low'].iloc[i],
        'close' : storedDataframe['close'].iloc[i],
        'Volume' : storedDataframe['Volume'].iloc[i],
        'Smoothing Line' : currentSMMA,
        'OnBalanceVolume' : obv[i]
        })
        
    


    json.dump(jsonChunk, open('./json/QQQ_Historical_Values.json', 'w+'), indent=4)