import requests
import os
from urllib.request import urlopen, Request
from telethon import TelegramClient, events
import hmac, hashlib, json
from urllib.parse import urlencode
from price_parser import Price
import time
import colored
from colored import stylize
from decimal import *
import sys
import math


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


def get_coin_name(text):
    try:
        return text[text.index("$"):].split(" ")[0][1:]
    except ValueError:
        return None


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


def calculate_percent(value, percent):
    return (value * percent) / 100


def calculate_max_buy_quantity(price, balance, lot_size):
    precision = 2
    if lot_size == '1.00000000':
        precision = 0
    return round(balance / price, precision)


def calculate_calculate_percent_price(price, percent):
    return round(price - calculate_percent(price, percent), 8)


def get_symbol_name(symbol_name):
    return symbol_name.replace("BTC", "")


def get_symbol_minimum_quantity(symbol_info):
    selected_symbol_filters = symbol_info['filters']
    for symbolFilter in selected_symbol_filters:
        if symbolFilter['filterType'] == 'LOT_SIZE':
            return symbolFilter['minQty']


def get_symbol_minimum_notional(symbol_info):
    selected_symbol_filters = symbol_info['filters']
    for symbolFilter in selected_symbol_filters:
        if symbolFilter['filterType'] == 'MIN_NOTIONAL':
            return symbolFilter['minNotional']


def get_btc_balance(client):
    return round(Price.fromstring(client.get_asset_balance(asset='BTC')["free"]).amount, 8)


def get_symbol_balance(client, symbol_name, base_asset_precision):
    return round(Price.fromstring(client.get_asset_balance(asset=get_symbol_name(symbol_name))["free"]).amount,
                 base_asset_precision)


def get_symbol_ask_bid_price(tickers, symbol_name, base_asset_precision):
    for item in tickers:
        if item['symbol'] == symbol_name:
            ask_bid_price = {
                "bid_price": round(Price.fromstring(item['bidPrice']).amount, base_asset_precision),
                "ask_price": round(Price.fromstring(item['askPrice']).amount, base_asset_precision)
            }
            return ask_bid_price


def print_take_profit_result(quantity, buy_price, sell_price):
    cost = float(quantity) * float(buy_price)
    ben = float(quantity) * float(sell_price)
    print(cost)
    print(ben)
    profit = ben - cost
    print(stylize("Take Profit Sell ", colored.fg("green")))
    print(stylize("Quantity: " + str(quantity), colored.fg("green")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("green")))
    print(stylize(
        "Profit: " + str(profit) + " BTC",
        colored.fg("green")))
    print("")


def print_stop_loss_result(quantity, buy_price, sell_price):
    print(stylize("Stop Loss Sell ", colored.fg("red")))
    print(stylize("Quantity: " + str(quantity), colored.fg("red")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("red")))
    print(stylize(
        "Loss: " + str((float(quantity) * float(sell_price)) -
                       (float(quantity) * float(buy_price))) + " BTC",
        colored.fg("red")))
    print("")


def print_current_status(price, high_price, stop_loss_price, initial_buy_price, take_profit_price):
    print(stylize("Current Price: " + str(price), colored.fg("green")))
    print(stylize("High Price: " + str(high_price), colored.fg("green")))
    print(stylize("Stop Loss Price: " + str(stop_loss_price), colored.fg("yellow")))
    print(stylize("Selected Symbol Initial Buy Price: " +
                  str(initial_buy_price), colored.fg("green")))
    print(stylize("selectedSymbolSellPrice: " +
                  str(take_profit_price), colored.fg("blue")))
    print("")


def calculate_quantity(symbol_balance, lot_size):
    if lot_size == 1:
        return round(symbol_balance - (symbol_balance * Decimal(0.1) / 100), 0)
    else:
        return round(symbol_balance - (symbol_balance * Decimal(0.1) / 100), 8)


def floatPrecision(f, n):
    n = int(math.log10(1 / float(n)))
    f = math.floor(float(f) * 10 ** n) / 10 ** n
    f = "{:0.0{}f}".format(float(f), n)
    return str(int(f)) if int(n) == 0 else f


useTelegram = False

selectedSymbolLastPrice = 0.0
selectedSymbolBidPrice = 0.0
selectedSymbolAskPrice = 0.0
selectedSymbolSellPrice = 0.0
selectedSymbolMinLotSize = 0.0
selectedSymbolMinNotional = 0.0
selectedSymbolStopLossPrice = 0.0
selectedSymbolInitialBuyPrice = 0.0
btcBalance = 0.0
selectedSymbolBalance = 0.0
stopLossPercent = 1  # 3%
takeProfitPercent = 1  # 1%
baseAssetPrecision = 0.0
order = None
buy = False
tick_size = None
symbol_info = None
step_size = None

session = "test"
api_id = 2156362
api_hash = "0d96604bf1fa9092de979309d1606466"
proxy = None  # https://github.com/Anorov/PySocks
telegram = TelegramClient(session, api_id, api_hash, proxy=proxy).start()

apikey = 'B705C63E6968CFB12B9FD8A5787E7990'
secret = '814e83158e6affdd76db67f8f3f81f8e'


# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".
@telegram.on(events.NewMessage())  # pattern=r'(?i).*\b(hello|hi)\b'))
async def handler(event):
    sender = await event.get_sender()

    print('said', event.text)
    coin = get_coin_name(event.txt)

    if len(coin) > 0:
        selectedSymbol = coin.upper() + "BTC"


# selectedSymbolName = sys.argv[1]
selectedSymbolName = "dash"
selectedSymbol = selectedSymbolName.lower() + "_btc"

if __name__ == "__main__":
    a = yobit(api_key=apikey, secret=secret)
    # x = requests.get("https://yobit.net/api/3/trades/ltc_btc?limit=1")

    # get btc baslance
    r = a.execute_query("getInfo", {})
    btcBalance = float(r["return"]["funds"]["btc"])
    selectedSymbolBalance = float(r["return"]["funds"][selectedSymbolName])

    print("btcBalance")
    print(btcBalance)

    print("selectedSymbolBalance")
    print(selectedSymbolBalance)
    print("")

    # GET PRICE
    symbol_info = json.loads(requests.get("https://yobit.net/api/3/ticker/" + selectedSymbol).text)
    initialPrice = float(round(float(symbol_info[selectedSymbol]["last"]), 8))
    selectedSymbolStopLossPrice = round(Decimal(initialPrice) - Decimal(initialPrice) * stopLossPercent / 100, 8)
    selectedSymbolSellPrice = initialPrice
    buyprice = float(round(float(initialPrice) + (float(initialPrice) * 0.2), 8))

    buy_quantity = float(round(float(r["return"]["funds"]["btc"]) / buyprice, 8))
    buy_quantity_with_fee = float(round(buy_quantity - (buy_quantity * 5) / 100, 8))

    selectedSymbolInitialBuyPrice = buyprice
    selectedSymbolLastPrice = buyprice

    print("buy_quantity")
    print(buy_quantity)
    print("")

    print("buy_quantity_with_fee")
    print(buy_quantity_with_fee)
    print("")

    print("selectedSymbolBalance")
    print(selectedSymbolBalance)
    print("")

    print("initialPrice")
    print(initialPrice)
    print("")

    print("buyprice")
    print(buyprice)
    print("")

    print("selectedSymbolStopLossPrice")
    print(selectedSymbolStopLossPrice)
    print("")

    print("selectedSymbolSellPrice")
    print(selectedSymbolSellPrice)
    print("")

    # INITIAL BUY
    params = {
        "pair": selectedSymbol,
        "type": "buy",
        "rate": str(initialPrice),
        "amount": str(buy_quantity_with_fee),
    }
    print(params)
    r = a.execute_query("Trade", params)
    print(r)
    # SET INITIAL BUY PRICE
    buy = True


    if buy == True:


        print("selectedSymbolBalance")
        print(selectedSymbolBalance)
        print("")
        print()
        while True:
            r = a.execute_query("getInfo", {})
            if "return" in r:
                selectedSymbolBalance = float(r["return"]["funds"][selectedSymbolName])
            # get symbol info
            # GET PRICE
            symbol_info = json.loads(requests.get("https://yobit.net/api/3/ticker/" + selectedSymbol).text)
            current_price = round(float(symbol_info[selectedSymbol]["last"]), 8)

            # NEW TARGET
            if current_price > selectedSymbolInitialBuyPrice and current_price > selectedSymbolLastPrice:
                print(stylize("New price target: " + str(selectedSymbolSellPrice), colored.fg("yellow")))
                selectedSymbolLastPrice = current_price
                selectedSymbolSellPrice = float(round(float(current_price) - (float(current_price) * 0.2), 8))
                print("price " + str(selectedSymbolSellPrice))

            # STOP LOSS SELL
            if current_price > selectedSymbolInitialBuyPrice and  current_price < selectedSymbolSellPrice:
                params = {
                    "pair": selectedSymbol,
                    "type": "sell",
                    "rate": str(float(round(float(selectedSymbolSellPrice) - (float(selectedSymbolSellPrice) * 0.2), 8))),
                    "amount": str(selectedSymbolBalance)
                }
                r = a.execute_query("Trade", params)
                print("SELL")
                exit(0)

            print_current_status(current_price, selectedSymbolLastPrice, selectedSymbolStopLossPrice,
                                 selectedSymbolInitialBuyPrice, selectedSymbolSellPrice)

            time.sleep(0.5)
    telegram.disconnect()
