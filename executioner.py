#!/usr/bin/env python3
import sys, schedule, time, subprocess

def job(t):
    print("Parsing Data")
    sys.stdout.flush()
    subprocess.run(["python", "jsonTamer.py"])
    time.sleep(30)
    subprocess.run(["python", "broker.py"])
    return

schedule.every().day.at("09:45").do(job,'It is 09:45')
print("Sheduler initialized")
sys.stdout.flush()

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute

