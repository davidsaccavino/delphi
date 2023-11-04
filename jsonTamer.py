import sys, os, json, pandas as pd
import datetime
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

dt = datetime.datetime
timedelta = datetime.timedelta

load_dotenv()

pd.options.display.float_format = '{:,.4f}'.format

cwd = os.path.dirname(__file__)




def jsonTamer(tickerName, timeframes):
    storedValues = {}
    storedDataframe = pd.DataFrame()


    for i in range(len(timeframes)):


        print(f'Parsing {tickerName} {timeframes[i]} data.')
        with open(f'{cwd}/json/{tickerName}_{timeframes[i]}_Historical_Values.json', 'r+') as f:
            #Populate storedDataframe with the json data in a dataframe format
            storedValues = json.load(f)
            storedDataframe = pd.DataFrame(storedValues)


            # Set the startDate to the last date in the storedDataframe
            startDate = storedValues[-1]['time']
            


            # Determine the timeframe for the current request
            if timeframes[i] == "Hour":
                request_timeframe = TimeFrame.Hour
                startDate = dt.strptime(startDate, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)
                startDate = startDate.astimezone(datetime.timezone.utc)


            elif timeframes[i] == "Day":
                request_timeframe = TimeFrame.Day
                startDate = dt.strptime(startDate, '%Y-%m-%d') + timedelta(days=1)
                startDate = startDate.replace(hour=0, minute=0, second=0)

            elif timeframes[i] == "Week":
                request_timeframe = TimeFrame.Week
                startDate = dt.strptime(startDate, '%Y-%m-%d') + timedelta(weeks=1)
                startDate = startDate.replace(hour=0, minute=0, second=0)


            # Initialize the data client with the API keys
            data_client = StockHistoricalDataClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))

            request_params = StockBarsRequest(
                                    symbol_or_symbols=[tickerName],
                                    timeframe=request_timeframe,
                                    start=startDate)
            
            # Request the bars from the Alpaca API
            bars = data_client.get_stock_bars(request_params)
            

            # Confirm that bars were found and try to convert to a dataframe for easier manipulation
            try:
                bars_df = bars.df
                
                print(f'Finished parsing {tickerName}-{timeframes[i]} data.')

            except:
                print(f'No bars were found to add to the {tickerName}-{timeframes[i]} dataframe.')
                exit(1)

            # Log the stdout to the systemctl journal for debugging purposes
            sys.stdout.flush()

            # Rename columns to match the storedDataframe
            bars_df.rename(index={1: 'time'}, columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'Volume'}, inplace=True)

            # Set the index to match the storedDataframe
            bars_df.index.names = ['symbol', 'time']


            # Replace the bars_df time index with the storedDataframe time index
            bars_df['time'] = (bars_df.index).get_level_values(1).astype(str)

            # Append newly gathered data to storedDataframe
            storedDataframe = storedDataframe.append(bars_df, ignore_index=True)

            
            # Calculate OBV
            def getOBV():
                obv = []
                for obvIterator in range(len(storedDataframe['close'])):
                    if obvIterator == 0:
                        value = storedDataframe['OnBalanceVolume'][obvIterator]

                    elif storedDataframe['close'][obvIterator] > storedDataframe['close'][obvIterator - 1]:
                        value = obv[-1] + storedDataframe['Volume'][obvIterator]
                        
                    elif storedDataframe['close'][obvIterator] < storedDataframe['close'][obvIterator - 1]:
                        value = obv[-1] - storedDataframe['Volume'][obvIterator]
                        
                    elif storedDataframe['close'][obvIterator] == storedDataframe['close'][obvIterator - 1]:
                        value = obv[-1]
                    
                    obv.append(value)
                    
                return obv
            obv = getOBV()


            # Calculate Smoothed Moving Average of OBV
            def getOBVSMMA():
                smma_len = 8

                smma = [storedValues[-1]['Smoothing Line']]

                length = len(storedDataframe) - len(storedValues)

                for smmaIterator in range(0, length):
                    smma.append(round((smma[smmaIterator] * (smma_len - 1) + obv[len(storedValues) + smmaIterator]) / smma_len))

                return smma[1:]
            smma = getOBVSMMA()



            # Generate jsonChunk to append to json file
            jsonChunk = []
            for jsonChunkIterator in range(len(storedDataframe['close'])):                

                
                    
                # Get SMMA values in the proper order to append to jsonChunk
                if(jsonChunkIterator < len(storedValues)):
                    try:
                        currentSMMA = storedValues[jsonChunkIterator]['Smoothing Line']
                    except:
                        print(currentSMMA, jsonChunkIterator, storedValues[-1])
                        exit(1)
                else:
                    currentSMMA = smma[jsonChunkIterator - len(storedValues)]
                
                
                # Calculate Heikin Ashi Close, Open, High, Low values
                # HeikinAshiClose = (storedDataframe['open'].iloc[jsonChunkIterator] + storedDataframe['high'].iloc[jsonChunkIterator] + storedDataframe['low'].iloc[jsonChunkIterator] + storedDataframe['close'].iloc[jsonChunkIterator]) / 4
                # HeikinAshiOpen = (storedDataframe['open'].iloc[jsonChunkIterator - 1] + storedDataframe['close'].iloc[jsonChunkIterator - 1]) / 2
                # HeikinAshiHigh = max(storedDataframe['high'].iloc[jsonChunkIterator], HeikinAshiOpen, HeikinAshiClose)
                # HeikinAshiLow = min(storedDataframe['low'].iloc[jsonChunkIterator], HeikinAshiOpen, HeikinAshiClose)
                

                # format time to match json
                time = storedDataframe['time'].iloc[jsonChunkIterator]
                if(timeframes[i] == "Hour"):
                    time = time[:19]
                    time = dt.strptime(time, '%Y-%m-%d %H:%M:%S')
                    # fix timezone
                    if(jsonChunkIterator != 0):
                        time = time - timedelta(hours=5)
                    time = time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time = time[:10]

                # Sequentially append values to jsonChunk to be dumped to json file
                jsonChunk.append({
                'time' : time,
                'open' : storedDataframe['open'].iloc[jsonChunkIterator],
                'high' : storedDataframe['high'].iloc[jsonChunkIterator],
                'low' : storedDataframe['low'].iloc[jsonChunkIterator],
                'close' : storedDataframe['close'].iloc[jsonChunkIterator],
                'Volume' : storedDataframe['Volume'].iloc[jsonChunkIterator],
                'Smoothing Line' : currentSMMA,
                'OnBalanceVolume' : obv[jsonChunkIterator]
                })  

            # Dump jsonChunk to json file
            json.dump(jsonChunk, open(f'{cwd}/json/{tickerName}_{timeframes[i]}_Historical_Values.json', 'w+'), indent=4)
            