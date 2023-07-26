import jsonTamer, delphi, broker

class Ticker:

    def __init__(self, name):
        self.name = name

    def scrapeStockData(self):
        jsonTamer.jsonTamer(self.name)

    def calculateIndicators(self):
        indicators = delphi.delphi(self.name)

        broker.broker(self.name, indicators)


        