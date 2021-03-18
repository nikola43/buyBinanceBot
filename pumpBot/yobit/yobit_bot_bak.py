import requests
import os
from urllib.request import urlopen, Request
import hmac, hashlib, json
from urllib.parse import urlencode
import time
import colored
from colored import stylize


class yobit(object):
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def execute_query(self, method, params=None):
        if params is None:
            params = {}
        params['method'] = method
        params['nonce'] = str(int(time.time()))
        post_data = urlencode(params).encode()
        signature = hmac.new(
            self.secret.encode(),
            post_data,
            hashlib.sha512).hexdigest()
        headers = {
            'Sign': signature,
            'Key': self.api_key,
            'User-Agent': "Mozilla/5.0"
        }
        request = Request("https://yobit.net/tapi", post_data, headers=headers)
        response = urlopen(request)
        return json.loads(response.read())


def check_coin():
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                return f.read()
            except:
                # whatever reader errors you care about
                print("errr")
                return None
        # handle error
    else:
        print("Coin not selected")
        return None


def print_current_status(price, last_price, high_price, stop_loss_price, initial_buy_price, take_profit_price):
    current_price_color = "gray"
    if price > last_price:
        current_price_color = "green"
    elif price < last_price:
        current_price_color = "red"
    else:
        current_price_color = "dark_orange_3a"

    print(stylize("Current Price: " + str(price), colored.fg(current_price_color)))
    print(stylize("High Price: " + str(high_price), colored.fg("green")))
    print(stylize("Stop Loss Price: " + str(stop_loss_price), colored.fg("red")))
    print(stylize("Selected Symbol Initial Buy Price: " +
                  str(initial_buy_price), colored.fg("blue")))
    print(stylize("selectedSymbolSellPrice: " +
                  str(take_profit_price), colored.fg("green")))
    print("")


# VARIABLES
stop_loss_percent = 0.2
take_profit_percent = 2.0
initial_price = 0.0
stop_loss_price = 0.0
target_sell_price = 0.0
btc_balance = 0.0
selected_symbol_balance = 0.0
buy_price = 0.0
last_price = 0.0
initial_buy_price = 0.0
high_price = 0.0
buy_quantity = 0.0
buy_quantity_with_fee = 0.0
symbol_info = {}
# selectedSymbolName = sys.argv[1]
selected_symbol_name = "eth"
selected_symbol = selected_symbol_name.lower() + "_btc"

apikey = 'B705C63E6968CFB12B9FD8A5787E7990'
secret = '814e83158e6affdd76db67f8f3f81f8e'
yobitApi = yobit(api_key=apikey, secret=secret)
buy = False
symbol_name = "eth"
symbol = symbol_name.lower() + "_btc"

if __name__ == "__main__":
    filename = "asset.txt"
    while True:
        coin = check_coin()
        if coin is not None:
            print(coin)
            break

    print("sd")
    # x = requests.get("https://yobit.net/api/3/trades/ltc_btc?limit=1")
    # get btc baslance
    r = yobitApi.execute_query("getInfo", {})
    btc_balance = float(r["return"]["funds"]["btc"])
    # selected_symbol_balance = float(r["return"]["funds"][selected_symbol_name])

    print("btcBalance")
    print(btc_balance)
    print("")
    print("selectedSymbolBalance")
    print(selected_symbol_balance)
    print("")

    # GET PRICE
    symbol_info = json.loads(requests.get("https://yobit.net/api/3/ticker/" + selected_symbol).text)
    initial_price = float(round(float(symbol_info[selected_symbol]["last"]), 8))
    stop_loss_price = float(round(float(initial_price) - (float(initial_price) * stop_loss_percent), 8))

    target_sell_price = initial_price
    buy_price = round(initial_price + (initial_price * take_profit_percent) / 100, 8)

    buy_quantity = float(round(float(r["return"]["funds"]["btc"]) / buy_price, 8))
    buy_quantity_with_fee = float(round(buy_quantity - (buy_quantity * 5) / 100, 8))

    initial_buy_price = buy_price
    high_price = buy_price

    print("buy_quantity")
    print(buy_quantity)
    print("")

    print("buy_quantity_with_fee")
    print(buy_quantity_with_fee)
    print("")

    print("selectedSymbolBalance")
    print(selected_symbol_balance)
    print("")

    print("initialPrice")
    print(initial_price)
    print("")

    print("buyprice")
    print(buy_price)
    print("")

    print("selectedSymbolStopLossPrice")
    print(stop_loss_price)
    print("")

    print("selectedSymbolSellPrice")
    print(target_sell_price)
    print("")

    # # INITIAL BUY
    # params = {
    #     "pair": selected_symbol,
    #     "type": "buy",
    #     "rate": str(high_price),
    #     "amount": str(buy_quantity_with_fee),
    # }
    # print(params)
    # r = yobitApi.execute_query("Trade", params)
    # print(r)
    while True:
        r = yobitApi.execute_query("getInfo", {})
        if "return" in r and symbol in r["return"]["funds"]:
            selectedSymbolBalance = float(r["return"]["funds"][symbol])
        # get symbol info
        # GET PRICE
        symbol_info = json.loads(requests.get("https://yobit.net/api/3/ticker/" + symbol).text)
        current_price = round(float(symbol_info[symbol]["last"]), 8)

        # NEW TARGET
        if current_price > buy_price and current_price > high_price:
            print(stylize("New price target: " + str(current_price), colored.fg("yellow")))
            target_sell_price = float(
                round(float(current_price) - (float(current_price) * 0.2), 8))
            print("price " + str(target_sell_price))

        # TAKE PROFIT
        if current_price <= target_sell_price and current_price > buy_price:
            take_profit_price = float(round(float(target_sell_price) - (float(target_sell_price) * 0.2), 8))
            print("take_profit_price")
            print(take_profit_price)
            if take_profit_price > buy_price:
                params = {
                    "pair": symbol,
                    "type": "sell",
                    "rate": str(take_profit_price),
                    "amount": str(selected_symbol_balance)
                }
                r = yobitApi.execute_query("Trade", params)
                print("TAKE PROFIT")
                exit(0)

        # STOP LOSS 6%
        if current_price <= stop_loss_price:
            stop_loss_sell_price = float(round(float(stop_loss_price) - (float(stop_loss_price) * stop_loss_percent), 8))
            print("stop_loss_sell_price")
            print(stop_loss_sell_price)
            params = {
                "pair": symbol,
                "type": "sell",
                "rate": str(stop_loss_sell_price),
                "amount": str(selected_symbol_balance)
            }
            r = yobitApi.execute_query("Trade", params)
            print("STOP LOSS")
            exit(0)

        print_current_status(current_price, last_price, high_price, stop_loss_price,
                             initial_buy_price, target_sell_price)
        last_price = current_price

        time.sleep(0.5)
