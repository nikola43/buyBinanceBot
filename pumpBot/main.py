from binance.client import Client
from price_parser import Price
import time
import colored
from colored import stylize
from decimal import *
import sys
import math


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


def print_take_profit_result(quantity, sell_price):
    print(stylize("Take Profit Sell ", colored.fg("green")))
    print(stylize("Quantity: " + str(quantity), colored.fg("green")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("green")))
    print(stylize(
        "Profit: " + str(float(quantity) * float(sell_price)) + " BTC",
        colored.fg("green")))
    print("")


def print_stop_loss_result(quantity, sell_price):
    print(stylize("Stop Loss Sell ", colored.fg("red")))
    print(stylize("Quantity: " + str(quantity), colored.fg("red")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("red")))
    print(stylize(
        "Loss: " + str(float(quantity) * float(sell_price)) + " BTC",
        colored.fg("red")))
    print("")


def print_current_status(price, high_price, stop_loss_price, initial_buy_price, take_profit_price):
    print(stylize("Current Price: " + str(price), colored.fg("green")))
    print(stylize("High Price: " + str(high_price), colored.fg("green")))
    print(stylize("Stop Loss Price: " + str(stop_loss_price), colored.fg("yellow")))
    print(stylize("Selected Symbol Initial Buy Price: " + str(initial_buy_price), colored.fg("green")))
    print(stylize("selectedSymbolSellPrice: " + str(take_profit_price), colored.fg("blue")))
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


apikey = 'z8oJ86HRXRKHppUeLZMOY8564f3gnNueSrmOL1455SXtkTmyHwusLc1XCjjGBKZt'
secret = 'UZggnxZ7moBpHw74iGK9SkXHlnci6RAsajO7x1wptsGvgr2qs5lRNu6y5WvJZvDJ'

client = Client(apikey, secret)
selectedSymbolName = sys.argv[1]
# selectedSymbolName = "lit"
selectedSymbol = selectedSymbolName.upper() + "BTC"
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
takeProfitPercent = 1 # 1%
baseAssetPrecision = 0.0
order = None

if __name__ == "__main__":
    # get symbol info
    symbol_info = client.get_symbol_info(selectedSymbol)
    tick_size = float(list(filter(lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))[0]['tickSize'])
    step_size = float(list(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))[0]['stepSize'])
    price = float(list(filter(lambda x: x['symbol'] == selectedSymbol, client.get_all_tickers()))[0]['price'])
    price = floatPrecision(price, tick_size)
    btc_balance = float(client.get_asset_balance(asset="BTC")['free']) / 10
    quantity = floatPrecision(btc_balance / float(price), step_size)
    selectedSymbolBalance = round(Price.fromstring(client.get_asset_balance(asset=selectedSymbolName)['free']).amount,
                                  8)
    selectedSymbolMinLotSize = get_symbol_minimum_quantity(symbol_info)

    print(stylize("BALANCES", colored.fg("yellow")))
    print(stylize("BTC BALANCE: " + str(btcBalance), colored.fg("blue")))
    print(stylize(get_symbol_name(selectedSymbol) + " BALANCE: " + str(selectedSymbolBalance), colored.fg("blue")))
    print("..")
    print(quantity)
    p = len(str(step_size)[2:])
    print(str(step_size)[2:])
    print(p)
    if p == 1:
        p = 0
    quantity = round(Decimal(quantity) - ((Decimal(quantity) * 5) / 100), p)
    #order = client.order_limit_buy(symbol=selectedSymbol, quantity=quantity, price=price)
    #client.cancel_order(symbol=selectedSymbol, orderId=order["orderId"])

    order = client.order_market_buy(symbol=selectedSymbol, quantity=quantity)
    print(order)

    selectedSymbolInitialBuyPrice = floatPrecision(order["fills"][0]["price"], tick_size)
    # selectedSymbolInitialBuyPrice = floatPrecision(selectedSymbolInitialBuyPrice, tick_size)
    selectedSymbolLastPrice = selectedSymbolInitialBuyPrice

    selectedSymbolStopLossPrice = round(Decimal(selectedSymbolInitialBuyPrice) - (
        round(Price.fromstring(selectedSymbolInitialBuyPrice).amount, 8)) * stopLossPercent / 100, 8)
    selectedSymbolSellPrice = round(Decimal(selectedSymbolInitialBuyPrice) + (
        round(Price.fromstring(selectedSymbolInitialBuyPrice).amount, 8)) * takeProfitPercent / 100, 8)

    selectedSymbolBalance = quantity

    # quantity =
    p = len(str(step_size)[2:])
    print(str(step_size)[2:])
    print(p)
    if p == 1:
        p = 0

    selectedSymbolBalance = round(Decimal(quantity) - ((Decimal(quantity) * 5) / 100), p)
    print(selectedSymbolBalance)
    p = round(Decimal(price) - round(Price.fromstring(price).amount, 8), 8)
    print(p)
    print(stylize("BALANCES", colored.fg("yellow")))
    print(stylize("BTC BALANCE: " + str(btcBalance), colored.fg("blue")))
    print(stylize(get_symbol_name(selectedSymbol) + " BALANCE: " + str(selectedSymbolBalance), colored.fg("blue")))
    print("")

    # q = round(calculate_max_buy_quantity(selectedSymbolBidPrice, btcBalance) - (calculate_max_buy_quantity(selectedSymbolBidPrice, btcBalance) * Decimal(0.1)) / 100, 0)
    # order = client.order_market_buy(symbol=selectedSymbol, quantity=q)
    # selectedSymbolInitialBuyPrice = round(Price.fromstring(order["fills"][0]["price"]).amount, 8)
    #
    # btcBalance = get_btc_balance(client)
    # selectedSymbolBalance = get_symbol_balance(client, selectedSymbol)
    # print(stylize("BTC BALANCE: " + str(btcBalance), colored.fg("blue")))
    # print(stylize(get_symbol_name(selectedSymbol) + " BALANCE: " + str(selectedSymbolBalance), colored.fg("blue")))
    # print("")
    #
    # print(stylize("Selected Symbol Initial Buy Price: " + str(selectedSymbolInitialBuyPrice), colored.fg("green")))
    while True:
        # get symbol info
        # get symbol info
        symbol_info = client.get_symbol_info(selectedSymbol)
        tick_size = float(
            list(filter(lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))[0]['tickSize'])
        step_size = float(list(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))[0]['stepSize'])
        price = float(list(filter(lambda x: x['symbol'] == selectedSymbol, client.get_all_tickers()))[0]['price'])
        price = floatPrecision(price, tick_size)
        btc_balance = float(client.get_asset_balance(asset='BTC')['free']) / 10
        quantity = floatPrecision(btc_balance / float(price), step_size)
        selectedSymbolMinLotSize = get_symbol_minimum_quantity(symbol_info)

        if float(price) > float(selectedSymbolInitialBuyPrice) and float(price) > float(selectedSymbolLastPrice):
            selectedSymbolLastPrice = price
            selectedSymbolSellPrice = round(Decimal(price) + (
                round(Price.fromstring(price).amount, 8)) * takeProfitPercent / 100, 8)
            print(stylize("New price target: " + str(selectedSymbolSellPrice), colored.fg("yellow")))
            p = floatPrecision(str(round(Decimal(price) - (Decimal(price) * Decimal(0.5)) / 100, 8)), tick_size)
            #p = round(float(str(price)) - (float(str(price)) * 1) / 100, 8)
            print("price " + price)
            print("stopPrice " + p)

            print(p)
            
            
            if order != None and order["status"] != "FILLED":
                client.cancel_order(symbol=selectedSymbol, orderId=order["orderId"])
            
            order = client.create_order(symbol=selectedSymbol,side="SELL",type="STOP_LOSS_LIMIT",quantity=selectedSymbolBalance,price=price,stopPrice=p,timeInForce="GTC")

        try:
            o = client.get_order(symbol=selectedSymbol,orderId=order["orderId"])
            print(o)
        except ValueError:
            print("Not found!")
        else:
            print("Found!")
        #print_take_profit_result(selectedSymbolBalance,p)
               
               

                

        print_current_status(price, selectedSymbolLastPrice, selectedSymbolStopLossPrice, selectedSymbolInitialBuyPrice,selectedSymbolSellPrice)
        # STOP LOSS SELL
        if round(Decimal(price), 8) <= selectedSymbolStopLossPrice:
            print(quantity)

        if order != None and order["status"] != "FILLED":
            client.cancel_order(symbol=selectedSymbol, orderId=order["orderId"])

            order = client.order_market_sell(symbol=selectedSymbol, quantity=selectedSymbolBalance)
            print_stop_loss_result(quantity, selectedSymbolStopLossPrice)
            break

        # TAKE PROFIT SELL
        if round(Decimal(price), 8) <= selectedSymbolSellPrice:
            if round(Decimal(price), 8) > round(Price.fromstring(selectedSymbolInitialBuyPrice).amount, 8):
                print(quantity)
                p = round(Price.fromstring(str( round(Decimal(price) + (Decimal(price) * 1) / 100, 8))).amount, 8)
            
                print(round(Decimal(price) + (Decimal(price) * 1) / 100, 8))
                p = floatPrecision(p, tick_size)
                #print(p)

                #order = client.order_market_sell(symbol=selectedSymbol, quantity=selectedSymbolBalance)
                #order = client.order_limit_sell(symbol=selectedSymbol, quantity=selectedSymbolBalance, price=p)
                #print_take_profit_result(selectedSymbolBalance,p)
                #break

        ##selectedSymbolLastPrice = round(selectedSymbolBidPrice, 8)
        time.sleep(0.5)
