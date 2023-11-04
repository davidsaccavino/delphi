import jsonTamer, delphi, broker, time


class Ticker:

    def __init__(self, name):
        
        self.name = name


    def scrapeStockData(self, timeframes):

        jsonTamer.jsonTamer(self.name, timeframes)


    def calculateIndicators(self, timeframes):

        signals = delphi.delphi(self.name, timeframes)

        for k, v in signals.items():
            timeframe = k
            VOSTbuySignal = v[0]
            VOSTsellSignal = v[1]
            deRisk = v[2]
            broker.broker(self.name, VOSTbuySignal, VOSTsellSignal, deRisk, timeframe)
            time.sleep(15)


        