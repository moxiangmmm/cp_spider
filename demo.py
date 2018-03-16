# coding=utf-8
import requests
import json
from retrying import retry
@retry(stop_max_attempt_number=5)
def hello():
    print(1111)
    try:
        print(sss)
    except Exception as e:
        raise e

def run_hello():
    hello()

def handel_errno():

    print(2222)
    try:
        run_hello()
    except Exception as e:
        print(e)



handel_errno()

