import schedule 
import time 
import requests

TIMES_TO_BACKUP = [
    "00:00", "06:00", "12:00", "18:00"
]
TIME_TO_RESET = "18:00"


def daily_reset():
    response = requests.get(f"https://justhink.net/daily-reset/DAILY_RESET")

    print(f"Daily reset has been done succesfully: {response} - {response.status_code}")

def daily_backup():
    response = requests.get(f"https://justhink.net/daily-reset/DAILY_BACKUP")

    print(f"Daily backup has been done succesfully: {response} - {response.status_code}")

for _time in TIMES_TO_BACKUP:
    schedule.every().day.at(_time).do(daily_backup)

schedule.every().day.at(TIME_TO_RESET).do(daily_reset)


print(f"Daily reset program has been started. It will reset at {TIME_TO_RESET}. (To terminate, press Ctrl + C)")

while 1:
    schedule.run_pending()
    time.sleep(1)