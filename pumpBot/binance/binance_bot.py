import requests
import os
from urllib.request import urlopen, Request
import hmac, hashlib, json
from urllib.parse import urlencode
import time
import colored
from colored import stylize
from binance.client import Client
import math
import webbrowser
from decimal import *

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


def floatPrecision(f, n):
    n = int(math.log10(1 / float(n)))
    f = math.floor(float(f) * 10 ** n) / 10 ** n
    f = "{:0.0{}f}".format(float(f), n)
    return str(int(f)) if int(n) == 0 else f


def cancel_order(order):
    try:
        if (order != None):
            order_info = client.get_order(
                symbol=selected_symbol, orderId=order["orderId"])
            print("order_info")
            print(order_info)

            cancel_order_result = client.cancel_order(
                symbol=selected_symbol, orderId=order_info["orderId"])
            print("cancel_order_result")
            print(cancel_order_result)
            return True
    except:
        print("Error: Order no existe o ya se ha realizado")
        return False
    return False


# VARIABLES
stop_loss_percent = 0.05
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
selected_symbol = selected_symbol_name.upper() + "BTC"
apikey = 'z8oJ86HRXRKHppUeLZMOY8564f3gnNueSrmOL1455SXtkTmyHwusLc1XCjjGBKZt'
secret = 'UZggnxZ7moBpHw74iGK9SkXHlnci6RAsajO7x1wptsGvgr2qs5lRNu6y5WvJZvDJ'
client = Client(apikey, secret)
buy = False
symbol_name = "eth"
symbol = symbol_name.upper() + "BTC"
max_profit_percent = 50
order = None
pres = 0
if __name__ == "__main__":
    filename = "asset.txt"
    while True:
        coin = check_coin()
        if coin is not None:
            print(coin)
            symbol = coin.upper() + "BTC"
            webbrowser.open("https://www.binance.com/es/trade/" + coin.upper() + "_BTC?layout=pro", new=2)
            break

    btc_balance = float(client.get_asset_balance(asset="BTC")['free'])

    print("btcBalance")
    print(btc_balance)
    print("")
    print("selectedSymbolBalance")
    print(selected_symbol_balance)
    print("")

    # GET PRICE
    symbol_info = client.get_symbol_info(symbol)
    tick_size = float(list(filter(
        lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))[0]['tickSize'])
    step_size = float(list(filter(
        lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))[0]['stepSize'])
    initial_price = float(list(filter(
        lambda x: x['symbol'] == symbol, client.get_all_tickers()))[0]['price'])
    initial_price = float(floatPrecision(initial_price, tick_size))
    stop_loss_price = float(round(float(initial_price) - (float(initial_price) * stop_loss_percent), 8))
    # initial_buy_price = float(round(initial_price + (initial_price * take_profit_percent) / 100, 8))

    pres = len(str(step_size)[2:])
    if pres == 1:
        pres = 0

    buy_quantity = float(btc_balance / initial_price)
    buy_quantity_with_fee = float(round(buy_quantity - (buy_quantity * 10) / 100, pres))
    sell_quantity = float(float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres)))

    print("buy_quantity_with_fee")
    print(buy_quantity_with_fee)
    print("")

    print("sell_quantity")
    print(sell_quantity)
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

    # order = client.order_market_buy(symbol=symbol, quantity=buy_quantity_with_fee)
    # print(order)
    #initial_buy_price = float(floatPrecision(order["fills"][0]["price"], tick_size))
    initial_buy_price = initial_price
    high_price = initial_buy_price
    stop_loss_price = float(round(float(initial_buy_price) - (float(initial_buy_price) * stop_loss_percent), 8))
    sell_quantity = float(float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres)))
    print("sell_quantity")
    print(sell_quantity)
    print("")
    while True:
        # GET PRICE
        symbol_info = client.get_symbol_info(symbol)
        current_price = float(list(filter(
            lambda x: x['symbol'] == symbol, client.get_all_tickers()))[0]['price'])
        stop_loss_price = float(round(float(current_price) - (float(current_price) * stop_loss_percent), 8))
        tick_size = float(list(filter(
            lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))[0]['tickSize'])
        step_size = float(list(filter(
            lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))[0]['stepSize'])
        target_sell_price = current_price

        # TAKE MAX PROFIT
        if current_price > initial_buy_price + ((initial_buy_price * max_profit_percent) / 100):
            cancel_order(order)
            sell_quantity = float(float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres)))
            print("take_profit_price")
            print(sell_quantity)
            order = client.order_market_sell(symbol=symbol, quantity=sell_quantity)
            print("TAKE MAX PROFIT")
            exit(0)

        # STOP LOSS 6%
        if current_price <= stop_loss_price:
            cancel_order(order)
            sell_quantity = float(float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres)))
            print("take_profit_price")
            print(sell_quantity)
            order = client.order_market_sell(symbol=symbol, quantity=sell_quantity)
            print("STOP LOSS")
            exit(0)

        # NEW TARGET
        if current_price > initial_buy_price and current_price > high_price:
            high_price = current_price
            print(stylize("New price target: " + str(current_price), colored.fg("yellow")))
            target_sell_price = float(
                round(float(current_price) - (float(current_price) * 0.2), 8))
            print("price " + str(target_sell_price))

        # TAKE PROFIT
        # if current_price <= target_sell_price and current_price > initial_buy_price:
        if current_price > initial_buy_price and current_price < (high_price - ((high_price * 15) / 100)):
            cancel_order(order)
            sell_quantity = float(float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres)))
            print("take_profit_price")
            print(sell_quantity)
            order = client.order_market_sell(symbol=symbol, quantity=sell_quantity)
            print("TAKE PROFIT")
            exit(0)

        print_current_status(current_price, last_price, high_price, stop_loss_price,
                             initial_buy_price, target_sell_price)
        last_price = current_price

        time.sleep(0.5)
