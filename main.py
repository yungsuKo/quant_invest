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

### 보유한 코인량 조회
def get_balance_coin(ticker):
    return upbit.get_balance(ticker)

### 평균 매수가 조회
def get_buy_avg(ticker):
    return upbit.get_avg_buy_price(ticker)

### 주문 정보 조회
def get_order_info(ticker):
    try:
        orders = upbit.get_order(ticker)
        if "error" in orders[0]:
            return None
        return orders[-1]  # 마지막 주문건에 대한 정보 리턴
    except Exception as e:
        print(e)
        return None

# info는 원하는 symbol 을 입력하거나, 주문의 uuid 를 입력
print(get_order_info(coin))