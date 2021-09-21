import requests
from config import *


def SendNotification(message: str):
    #  push notification to applets in IFTTT App, sync with Apple Watch
    data = {
        'WasherWatcher': message
    }
    requests.post(url=IFTTT_url, json=data)


if __name__ == '__main__':
    SendNotification('当前洗衣机忙！')
