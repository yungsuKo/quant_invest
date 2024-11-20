import os
import pyupbit
import requests

### 거래할 코인 symbol
coin = "KRW-DOGE" 

with open("key.txt") as f:
    access_key, secret_key = [line.strip() for line in f.readlines()]
with open("slack.txt") as f:
    slack_key = f.readline()


### 업비트 연동
upbit = pyupbit.Upbit(access_key, secret_key)


def get_balance_cash():
    return upbit.get_balance("KRW")

### ticker의 현재가 조회
def get_cur_price(ticker):
    return pyupbit.get_current_price(ticker)

### 존재하는 ticker 명 전체 조회
# url = "https://api.upbit.com/v1/market/all"
# res = requests.get(url).json()

# ticker_list = {}

# for i in res:
#     name = i['korean_name']
#     ticker = i['market']

#     if ticker.startswith("KRW"):
#         ticker_list[name] = ticker

# print(ticker_list)

def get_balance_coin(ticker):
    return upbit.get_balance(ticker)

print(get_balance_coin(coin))