import json, datetime

with open('./QQQ_Hour_Historical_Values.json', 'r+') as f:
    storedValues = json.load(f)
    for bar in storedValues:
        currentDateAndHour = datetime.datetime.fromtimestamp(bar['time'])
        bar['time'] = currentDateAndHour.strftime('%Y-%m-%d %H:%M:%S')

    json.dump(storedValues, open('./QQQ_Hour_Historical_Values.json', 'w+'), indent=4)

