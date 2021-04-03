import os
import time
import colored
from colored import stylize
from binance.client import Client
import math
import webbrowser
import decimal
import sys

def print_current_status(price, last_price, high_price, stop_loss_price, initial_buy_price, take_profit_price):
    current_price_color = "gray"
    if price > last_price:
        current_price_color = "green"
    elif price < last_price:
        current_price_color = "red"
    else:
        current_price_color = "dark_orange_3a"

    print(stylize("Current Price: " + str(price_from_string(price)), colored.fg(current_price_color)))
    print(stylize("High Price: " + str(price_from_string(high_price)), colored.fg("green")))
    print(stylize("Stop Loss Price: " + str(price_from_string(stop_loss_price)), colored.fg("red")))
    print(stylize("Selected Symbol Initial Buy Price: " +
                  str(price_from_string(initial_buy_price)), colored.fg("blue")))
    print(stylize("selectedSymbolSellPrice: " +
                  str(price_from_string(take_profit_price)), colored.fg("green")))
    print("")


def floatPrecision(f, n):
    n = int(math.log10(1 / float(n)))
    f = math.floor(float(f) * 10 ** n) / 10 ** n
    f = "{:0.0{}f}".format(float(f), n)
    return str(int(f)) if int(n) == 0 else f


def cancel_order(orderId):
    try:
        if orderId is not None:
            order_info = client.get_order(
                symbol=symbol, orderId=orderId)
            print("order_info")
            print(order_info)

            cancel_order_result = client.cancel_order(
                symbol=symbol, orderId=order_info["orderId"])
            print("cancel_order_result")
            print(cancel_order_result)
            return True
    except:
        print("Error: Order no existe o ya se ha realizado")
        return False
    return False


def price_from_string(price):
    p = decimal.Decimal(price)
    decimal.getcontext().prec = 8
    decimal.getcontext().create_decimal(p)
    return p


# VARIABLES
stop_loss_percent = 0.01
take_profit_percent = 2.0
initial_price = 0.0
stop_loss_price = 0.0
target_sell_price = 0.0
pair_balance = 0.0
selected_symbol_balance = 0.0
buy_price = 0.0
last_price = 0.0
initial_buy_price = 0.0
high_price = 0.0
buy_quantity = 0.0
buy_quantity_with_fee = 0.0
symbol_info = {}
# selectedSymbolName = sys.argv[1]
apikey = 'z8oJ86HRXRKHppUeLZMOY8564f3gnNueSrmOL1455SXtkTmyHwusLc1XCjjGBKZt'
secret = 'UZggnxZ7moBpHw74iGK9SkXHlnci6RAsajO7x1wptsGvgr2qs5lRNu6y5WvJZvDJ'
client = Client(apikey, secret)
buy = False
symbol_name = sys.argv[1]
pair = "USDT"
symbol = symbol_name.upper() + pair
max_profit_percent = 100

pres = 0
if __name__ == "__main__":

    webbrowser.open("https://www.binance.com/es/trade/" + symbol_name.upper() + "_" + pair + "?layout=pro", new=2)

    pair_balance = price_from_string(client.get_asset_balance(asset=pair)['free'])
    selected_symbol_balance = price_from_string(client.get_asset_balance(asset=symbol_name.upper())['free'])

    print("btcBalance")
    print(pair_balance)
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


    pres = len(str(step_size)[2:])
    if pres == 1:
        pres = 0


    buy_quantity = float(float(pair_balance) / float(initial_price))
    buy_quantity_with_fee = float(round(buy_quantity - (buy_quantity * 10) / 100, pres))
    sell_quantity = float(round(buy_quantity_with_fee - (buy_quantity_with_fee * 10) / 100, pres))

    print("sell_quantity")
    print(sell_quantity)

    order = client.order_market_buy(symbol=symbol, quantity=buy_quantity_with_fee)
    orderId = order["orderId"]
    initial_buy_price = float(floatPrecision(order["fills"][0]["price"], tick_size))
    stop_loss_price = float(round(float(initial_buy_price) - (float(initial_buy_price) * stop_loss_percent), 8))

    print(order)
    high_price = initial_buy_price

    while True:
        # GET PRICE
        symbol_info = client.get_symbol_info(symbol)
        tick_size = float(list(filter(
            lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))[0]['tickSize'])
        step_size = float(list(filter(
            lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))[0]['stepSize'])
        current_price = float(list(filter(
            lambda x: x['symbol'] == symbol, client.get_all_tickers()))[0]['price'])
        current_price = float(floatPrecision(current_price, tick_size))

        target_sell_price = current_price

        # NEW TARGET
        if current_price > initial_buy_price and current_price > high_price:
            high_price = current_price
            print(stylize("New price target: " + str(current_price), colored.fg("yellow")))
            target_sell_price = float(round(float(current_price) - (float(current_price) * 0.003), 8))
            target_sell_stop_price = float(round(float(current_price) - (float(current_price) * 0.006), 8))

            if order is not None:
                print("order[orderId]")
                print(order["orderId"])

            cancel_order(orderId)
            order = client.create_order(symbol=symbol,
                                        side="SELL",
                                        type="STOP_LOSS_LIMIT",
                                        quantity=sell_quantity,
                                        price=floatPrecision(target_sell_stop_price, tick_size),
                                        stopPrice=floatPrecision(target_sell_price, tick_size),
                                        timeInForce="GTC")

            orderId = order["orderId"]
            print("order[orderId]")
            print(order["orderId"])

        # STOP LOSS 5%
        if current_price <= stop_loss_price:
            cancel_order(orderId)
            order = client.order_market_sell(symbol=symbol, quantity=sell_quantity)
            print("STOP LOSS")
            exit(0)

        # TAKE MAX PROFIT
        # if current_price > initial_buy_price + ((initial_buy_price * max_profit_percent) / 100):
        #    cancel_order(orderId)
        #    order = client.order_market_sell(symbol=symbol, quantity=decimal.Decimal(sell_quantity))
        #    print("TAKE MAX PROFIT")
        #    exit(0)

        print_current_status(current_price,
                             last_price,
                             high_price,
                             stop_loss_price,
                             initial_buy_price,
                             target_sell_price)
        last_price = current_price
        time.sleep(0.5)
