import sys, os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pandas as pd
import numpy as np

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

pd.options.display.float_format = '{:,.4f}'.format

cwd = os.path.dirname(__file__)


def jsonTamer(tickerName, timeframes):
    storedValues = {}
    storedDataframe = pd.DataFrame()
    for i in range(len(timeframes)):


        print(f'Parsing {tickerName} {timeframes[i]} data.')
        with open(f'{cwd}/json/{tickerName}_{timeframes[i]}_Historical_Values.json', 'r+') as f:
            storedValues = json.load(f)
            storedDataframe = pd.DataFrame(storedValues)

            startDate = storedValues[-1]['time']
            if timeframes[i] == "Hour":
                request_timeframe = TimeFrame.Hour
                startDate = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)
            elif timeframes[i] == "Day":
                request_timeframe = TimeFrame.Day
                startDate = datetime.strptime(startDate, '%Y-%m-%d') + timedelta(days=1)
                startDate = startDate.replace(hour=0, minute=0, second=0)
            elif timeframes[i] == "Week":
                request_timeframe = TimeFrame.Week
                startDate = datetime.strptime(startDate, '%Y-%m-%d') + timedelta(weeks=1)
                startDate = startDate.replace(hour=0, minute=0, second=0)

            data_client = StockHistoricalDataClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))





            request_params = StockBarsRequest(
                                    symbol_or_symbols=[tickerName],
                                    timeframe=request_timeframe,
                                    start=startDate,
                            )


            bars = data_client.get_stock_bars(request_params)
            print(bars)
            try:
                bars_df = bars.df
            except:
                print(f'No bars were found to add to the {tickerName}-{timeframes[i]} dataframe.')
                sys.stdout.flush()
                exit(1)

            bars_df.rename(index={1: 'time'}, columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'Volume'}, inplace=True)
            bars_df.index.names = ['symbol', 'time']


        
            bars_df['time'] = (bars_df.index).get_level_values(1).astype(str)
            storedDataframe = storedDataframe.append(bars_df, ignore_index=True)

            
            
            def getOBV():
                obv = []
                for obvIterator in range(len(storedDataframe['close'])):
                    if obvIterator == 0:
                        value = storedDataframe['OnBalanceVolume'][obvIterator]
                        obv.append(value)
                    elif storedDataframe['close'][obvIterator] > storedDataframe['close'][obvIterator - 1] :
                        value = obv[-1] + storedDataframe['Volume'][obvIterator]
                        obv.append(value)
                    elif storedDataframe['close'][obvIterator] < storedDataframe['close'][obvIterator - 1]:
                        value = obv[-1] - storedDataframe['Volume'][obvIterator]
                        obv.append(value)
                    elif storedDataframe['close'][obvIterator] == storedDataframe['close'][obvIterator - 1]:
                        value = obv[-1]
                        obv.append(value)


                return obv



        
            obv = getOBV()

            def getOBVSMMA():
                obv_len = 8
                initialSMMA =  storedValues[-1]['Smoothing Line']
                
                smma = [initialSMMA]

                length = len(storedDataframe) - len(storedValues)

                for obvIterator in range(0, length):
                    smma.append(round((smma[obvIterator] * (obv_len - 1) + obv[len(storedValues) + obvIterator]) / obv_len))

                return smma[1:]



                

            smma = getOBVSMMA()

            jsonChunk = []
            for jsonChuckIterator in range(len(storedDataframe['close'])):
                
                #format time to match json
                time = storedDataframe['time'].iloc[jsonChuckIterator]
                time = time[:10]
                if(i < len(storedValues)):
                    currentSMMA = storedValues[jsonChuckIterator]['Smoothing Line']
                else:
                    currentSMMA = smma[i - len(storedValues)]
                
                HeikinAshiClose = (storedDataframe['open'].iloc[jsonChuckIterator] + storedDataframe['high'].iloc[jsonChuckIterator] + storedDataframe['low'].iloc[jsonChuckIterator] + storedDataframe['close'].iloc[jsonChuckIterator]) / 4
                HeikinAshiOpen = (storedDataframe['open'].iloc[jsonChuckIterator - 1] + storedDataframe['close'].iloc[jsonChuckIterator - 1]) / 2
                HeikinAshiHigh = max(storedDataframe['high'].iloc[jsonChuckIterator], HeikinAshiOpen, HeikinAshiClose)
                HeikinAshiLow = min(storedDataframe['low'].iloc[jsonChuckIterator], HeikinAshiOpen, HeikinAshiClose)

                jsonChunk.append({
                'time' : time,
                'open' : HeikinAshiOpen.iloc[jsonChuckIterator],
                'high' : HeikinAshiHigh.iloc[jsonChuckIterator],
                'low' : HeikinAshiLow.iloc[jsonChuckIterator],
                'close' : HeikinAshiClose.iloc[jsonChuckIterator],
                'Volume' : storedDataframe['Volume'].iloc[jsonChuckIterator],
                'Smoothing Line' : currentSMMA,
                'OnBalanceVolume' : obv[jsonChuckIterator]
                })

            print(jsonChunk)
                
            


            json.dump(jsonChunk, open(f'{cwd}/json/{tickerName}_{timeframes[i]}_Historical_Values.json', 'w+'), indent=4)


jsonTamer("QQQ", ["Hour"])