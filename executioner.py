#!/usr/bin/env python3
import os, sys, schedule, time, tickerClass

aapl = tickerClass.ticker("AAPL")
msft = tickerClass.ticker("MSFT")
tsla = tickerClass.ticker("TSLA")
goog = tickerClass.ticker("GOOG")
qqq = tickerClass.ticker("QQQ")

def runDataScraper():
    aapl.scrapeStockData()
    msft.scrapeStockData()
    tsla.scrapeStockData()
    goog.scrapeStockData()
    qqq.scrapeStockData()
    return

def runIndicators():
    aapl.calculateIndicators()
    msft.calculateIndicators()
    tsla.calculateIndicators()
    goog.calculateIndicators()
    qqq.calculateIndicators()
    return

cwd = os.path.dirname(__file__)

def job(t):
    print("Parsing Data")
    sys.stdout.flush()
    runDataScraper()
    time.sleep(90)
    runIndicators()
    return

schedule.every().day.at("09:45").do(job,'It is 09:45')
print("Sheduler initialized")
sys.stdout.flush()

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute

