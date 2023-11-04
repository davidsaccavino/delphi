import os, sys, schedule, time, tickerClass, datetime as dt

cwd = os.path.dirname(__file__)

timeframesList = ["Hour", "Day"]

FirstSearchofDay = True

# aapl = tickerClass.ticker("AAPL")
# msft = tickerClass.ticker("MSFT")
# tsla = tickerClass.ticker("TSLA")
# goog = tickerClass.ticker("GOOG")
qqq = tickerClass.Ticker("QQQ")


def runDataScraper(timeframes):
    # aapl.scrapeStockData(timeframes)
    # msft.scrapeStockData(timeframes)
    # tsla.scrapeStockData(timeframes)
    # goog.scrapeStockData(timeframes)
    qqq.scrapeStockData(timeframes)
    return


def runIndicators(timeframes):
    # aapl.calculateIndicators(timeframes)
    # msft.calculateIndicators(timeframes)
    # tsla.calculateIndicators(timeframes)
    # goog.calculateIndicators(timeframes)
    qqq.calculateIndicators(timeframes)
    return


def job():
    if FirstSearchofDay:
        runDataScraper(timeframesList)
        time.sleep(30)
        runIndicators(timeframesList)
    
    # If not first search of day, only run the hourly job
    else:
        runDataScraper(timeframesList[0])
        time.sleep(30)
        runIndicators(timeframesList[0])

def secretary():
    dayOfWeekNumber = dt.datetime.today().weekday()
    currentHour = dt.datetime.now().hour

    # Check if it's a weekday if and it's before 4pm
    # if dayOfWeekNumber < 5 and  currentHour < 16:
        # schedule.every().hour.at("30:05").do(job)
    job()
    print("Sheduler initialized")
    sys.stdout.flush()


# schedule.every().day.at("09:20").do(secretary, 'Setting up the routine for the day...')
secretary()


while True:
    schedule.run_pending()
    time.sleep(10) # wait ten seconds

