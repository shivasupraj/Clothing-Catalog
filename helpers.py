import requests
import re

def checkUrl(url):
    try:
        request = requests.get(url)
        return request.status_code == 200
    except Exception:
        return False

def checkPrice(price):
    try:
        float(price)
        return True
    except ValueError:
        return False


