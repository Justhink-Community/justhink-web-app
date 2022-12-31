import schedule 
import time 
import requests
import os

TIME_TO_RESET = "18:00"


def daily_reset():
    response = requests.get(f"https://justhink.net/daily-reset/DAILY_RESET")
    os.system('cd ..')
    os.system('git add .')
    os.system('git commit -m "Daily Patch - No description"')
    os.system('git push')
    os.system('cd source')
    print(f"Daily reset has been done succesfully: {response} - {response.status_code}")

daily_reset()

schedule.every().day.at(TIME_TO_RESET).do(daily_reset)

print(f"Daily reset program has been started. It will reset at {TIME_TO_RESET}. (To terminate, press Ctrl + C)")

while 1:
    schedule.run_pending()
    time.sleep(1)