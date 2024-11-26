import os
import pyupbit
import requests
import time

### 거래할 코인 symbol
coin = "KRW-DOGE" 

with open("key.txt") as f:
    access_key, secret_key = [line.strip() for line in f.readlines()]
with open("slack.txt") as f:
    slack_key = f.readline()

def send(msg):
    try:
        url = slack_key
        header = {'Content-type': 'application/json'}
        icon_emoji = ":slack:"
        username = "coin_bot"
        attachments = [{
            "text": msg
        }]

        data = {"username": username, "attachments": attachments, "icon_emoji": icon_emoji}
        print(data)

        # 메세지 전송
        return requests.post(url, headers=header, json=data)
        
    except Exception as e:
        print("Slack Message 전송에 실패했습니다.")
        print("에러 내용 : " + e)

        exit(0)
        
### fetch 함수를 통해 안정적으로 호출
def fetch_data(fetch_func, max_retries=20, delay=0.5):
    for i in range(max_retries):
        res = fetch_func() # fetch_func() 함수를 호출하여 데이터
        if res is not None: # 가져온 데이터가 None이 아닌 경우 루프를 종료
            return res
        time.sleep(delay) # 데이터를 가져오지 못한 경우 0.5초 동안 대기
    return None

### 업비트 연동
upbit = pyupbit.Upbit(access_key, secret_key)


def get_balance_cash():
    return fetch_data(lambda : upbit.get_balance("KRW"))

### ticker의 현재가 조회
def get_cur_price(ticker):
    return fetch_data(lambda : pyupbit.get_current_price(ticker))

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
    return fetch_data(lambda : upbit.get_balance(ticker))

### 평균 매수가 조회
def get_buy_avg(ticker):
    return fetch_data(lambda : upbit.get_avg_buy_price(ticker))

### 주문 정보 조회
def get_order_info(ticker):
    try:
        orders = fetch_data(lambda : upbit.get_order(ticker))
        if "error" in orders[0]:
            return None
        return orders[-1]  # 마지막 주문건에 대한 정보 리턴
    except Exception as e:
        print(e)
        return None

### 매수 주문하기
def order_buy_market(ticker, buy_amount):  
    """
    : ticker : 코인 이름
    : buy_amount : 매수할 금액
    """
    if buy_amount < 5000:  
        print("amount is better than 5000")
        return 0
    try:
        res = upbit.buy_market_order(ticker,buy_amount)
        if 'error' in res:
            print(res)
            res = 0
            return res
        msg = "매도 성공 \n\n " + res
        send(msg)
        print(res)
    except Exception as e:
        res = 0
        print(e)
    return res

# 시장가 매도
def order_sell_market(ticker, volume):
    """
    : ticker : 코인 이름
    : volume : 매도할 수량
    """
    try:
        res = upbit.sell_market_order(ticker, volume)
        if 'error' in res:
            print(res)
            res = 0
            return res
        msg = "매도 성공 \n\n " + res
        send(msg)
        print(res)
    except Exception as e:
        print(e)
        res = 0 
    return res

# 현재 거래 가능한 보유 코인 수량 조회
# 그 다음 매도 함수 호출


def get_bollinger_bands(prices, window=20, multiplier=2):

    ### 20일 기간 동안 이동 평균선 계산 (Middle Band)
    sma = prices.rolling(window).mean()

    ### 20일 동안의 표준 편차 계산
    rolling_std = prices.rolling(window).std()

    ### 중간 밴드 + (표준편차 * 2)
    upper_band = sma + (rolling_std * multiplier)
    
    ### 중간 밴드 - (표준편차 * 2)
    lower_band = sma - (rolling_std * multiplier)

    return upper_band, lower_band

def trading_signal(prices):
    ### get_bollinger_bands() 함수를 통해 상단/하단 밴드 요청
    upper_band, lower_band = get_bollinger_bands(prices)

    band_high = upper_band.iloc[-1]
    band_low = lower_band.iloc[-1]
    cur_price = get_cur_price(coin)

    ### 상단/하단/현재가 출력
    print(f"HIGH : {band_high} / LOW : {band_low} / PRICE : {cur_price}")

    ### 현재 가격이 상단 밴드보다 큰 경우는 'BUY' 신호를, 
    ### 하단 밴드보다 낮은 경우는 'SELL' 신호를,
    ### 밴드안에 있는 경우는 'HOLD' 신호를 return
    if cur_price > band_high:
        print("Sell signal")
        return 'SELL'
    elif cur_price < band_low:
        print("Buy signal")
        return 'BUY'
    else:
        return 'HOLD'
    
def trading(coin):
    ### pyupbit.get_ohlcv() 함수를 이용해서 업비트 사이트의 20일 데이터 받아오기
    prices_data = pyupbit.get_ohlcv(coin, interval="minute1", count=20)
    print(prices_data)
    prices = prices_data['close']
    
    ### 받아온 가격 데이터의 종가만을 추출하여 trading_signal() 함수에 전달
    signal = trading_signal(prices)
    balance_cash = get_balance_cash()
    balance_coin = get_balance_coin(coin)

    ### signal 이 "BUY" 이고 현재 보유 현금이 10000원 보다 많은 경우 매수 주문
    ### signal 이 "SELL" 이고 현재 보유 코인이 1개 보다 많은 경우 매도 주문
    if signal == 'BUY' and balance_cash > 10000:
        print("BUY Order")
        return order_buy_market(coin, 10000)
    elif signal == 'SELL' and balance_coin > 0:
        print("SELL Order")
        return order_sell_market(coin, balance_coin)
    else:
        print("Hold position.")
    return None

def run():
    ret = trading(coin)
    if ret is not None:
        print(ret)

while True:
    run()
    time.sleep(5)