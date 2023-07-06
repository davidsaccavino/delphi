#!/usr/bin/env python3
import os, sys, schedule, time, subprocess

cwd = os.path.dirname(__file__)

def job(t):
    print("Parsing Data")
    sys.stdout.flush()
    subprocess.run(["python3", cwd + "/jsonTamer.py"])
    time.sleep(30)
    subprocess.run(["python3", cwd + "/broker.py"])
    return

schedule.every().day.at("09:45").do(job,'It is 09:45')
print("Sheduler initialized")
sys.stdout.flush()

while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute

