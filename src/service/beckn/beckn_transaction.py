import requests
from dotenv import load_dotenv
import os

load_dotenv()

BECKN_BASE_URL = os.getenv("BECKN_BASE_URL")    


def beckn_search(data):
    response = requests.post(f"{BECKN_BASE_URL}/search", json=data)
    return data

def beckn_select(data):
    response = requests.post(f"{BECKN_BASE_URL}/select", json=data)
    return data

def beckn_init(data):
    response = requests.post(f"{BECKN_BASE_URL}/init", json=data)
    return data

def beckn_confirm(data):
    response = requests.post(f"{BECKN_BASE_URL}/confirm", json=data)
    return data