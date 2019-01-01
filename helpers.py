import requests
import re

def check_url(url):
    try:
        request = requests.get(url)
        return request.status_code == 200
    except Exception:
        return False

def check_price(price):
    try:
        float(price)
        return True
    except ValueError:
        return False
