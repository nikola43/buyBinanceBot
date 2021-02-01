from binance.client import Client
from price_parser import Price
import time
import colored
from colored import stylize
from decimal import *

apikey = 'z8oJ86HRXRKHppUeLZMOY8564f3gnNueSrmOL1455SXtkTmyHwusLc1XCjjGBKZt'
secret = 'UZggnxZ7moBpHw74iGK9SkXHlnci6RAsajO7x1wptsGvgr2qs5lRNu6y5WvJZvDJ'

client = Client(apikey, secret)

selectedSymbol = "FLM" + "BTC"
selectedSymbolLastPrice = 0
selectedSymbolBidPrice = 0
selectedSymbolAskPrice = 0
selectedSymbolSellPrice = 0
selectedSymbolMinLotSize = 0
selectedSymbolMinNotional = 0
selectedSymbolStopLossPrice = 0
selectedSymbolInitialBuyPrice = 0
btcBalance = 0
selectedSymbolBalance = 0
stopLossPercent = 5
takeProfitPercent = 1


def calculate_percent(value, percent):
    return (value * percent) / 100


def calculate_max_buy_quantity(price, balance):
    return balance / price


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
    return Price.fromstring(client.get_asset_balance(asset='BTC')["free"]).amount


def get_symbol_balance(client, symbol_name):
    return Price.fromstring(client.get_asset_balance(asset=get_symbol_name(symbol_name))["free"]).amount


def get_symbol_ask_bid_price(tickers, symbol_name):
    for item in tickers:
        symbol = item['symbol']
        if symbol == symbol_name:
            ask_bid_price = {
                "bid_price": round(Price.fromstring(item['bidPrice']).amount, 8),
                "ask_price": round(Price.fromstring(item['askPrice']).amount, 8)
            }
            return ask_bid_price


def print_take_profit_result(quantity, sell_price):
    print(stylize("Take Profit Sell ", colored.fg("green")))
    print(stylize("Quantity: " + str(quantity), colored.fg("green")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("green")))
    print(stylize(
        "Profit: " + str(quantity * sell_price) + " BTC",
        colored.fg("green")))
    print("")


def print_stop_loss_result(quantity, sell_price):
    print(stylize("Stop Loss Sell ", colored.fg("red")))
    print(stylize("Quantity: " + str(quantity), colored.fg("red")))
    print(stylize("Sell Price: " + str(sell_price), colored.fg("red")))
    print(stylize(
        "Loss:" + str(quantity * sell_price) + " BTC",
        colored.fg("red")))
    print("")


def print_current_status(bid_price, ask_price, sell_price, stop_loss_price, initial_buy_price):
    print(stylize("Buy Price: " + str(bid_price), colored.fg("green")))
    print(stylize("Sell Price: " + str(ask_price), colored.fg("red")))
    print(stylize("Stop Loss Price: " + str(stop_loss_price), colored.fg("yellow")))
    print(stylize("Selected Symbol Initial Buy Price: " + str(initial_buy_price), colored.fg("green")))
    print(stylize("selectedSymbolSellPrice: " + str(sell_price), colored.fg("blue")))
    print("")


def calculate_quantity(symbol_balance, lot_size):
    if lot_size == 1:
        return round(symbol_balance - (symbol_balance * Decimal(0.1) / 100), 0)
    else:
        return round(symbol_balance - (symbol_balance * Decimal(0.1) / 100), 8)


if __name__ == "__main__":
    # get symbol info
    symbol_info = client.get_symbol_info(selectedSymbol)

    # get initial price
    tickers = client.get_orderbook_tickers()
    selectedSymbolPrices = get_symbol_ask_bid_price(tickers, selectedSymbol)
    selectedSymbolBidPrice = selectedSymbolPrices["bid_price"]
    selectedSymbolAskPrice = selectedSymbolPrices["ask_price"]

    # get symbol minimum lot size and minimum notional
    selectedSymbolMinLotSize = get_symbol_minimum_quantity(symbol_info)
    selectedSymbolMinNotional = get_symbol_minimum_notional(symbol_info)

    # print(selectedSymbolMinLotSize)
    # print(selectedSymbolMinNotional)
    # print(tickers)

    # GET BTC AND SELECTED SYMBOL BALANCE
    btcBalance = get_btc_balance(client)
    selectedSymbolBalance = get_symbol_balance(client, selectedSymbol)
    btcBalance = btcBalance / 20  # 2% usable

    print(stylize("BTC BALANCE: " + str(btcBalance), colored.fg("blue")))
    print(stylize(get_symbol_name(selectedSymbol) + " BALANCE: " + str(selectedSymbolBalance), colored.fg("blue")))
    print("")

    q = round(calculate_max_buy_quantity(selectedSymbolBidPrice, btcBalance) - (
            calculate_max_buy_quantity(selectedSymbolBidPrice, btcBalance) * Decimal(0.1)) / 100, 0)
    order = client.order_market_buy(symbol=selectedSymbol, quantity=q)
    selectedSymbolInitialBuyPrice = round(Price.fromstring(order["fills"][0]["price"]).amount, 8)

    btcBalance = get_btc_balance(client)
    selectedSymbolBalance = get_symbol_balance(client, selectedSymbol)
    print(stylize("BTC BALANCE: " + str(btcBalance), colored.fg("blue")))
    print(stylize(get_symbol_name(selectedSymbol) + " BALANCE: " + str(selectedSymbolBalance), colored.fg("blue")))
    print("")

    print(stylize("Selected Symbol Initial Buy Price: " + str(selectedSymbolInitialBuyPrice), colored.fg("green")))

    while (True):
        tickers = client.get_orderbook_tickers()
        selectedSymbolPrices = get_symbol_ask_bid_price(tickers, selectedSymbol)
        selectedSymbolBidPrice = selectedSymbolPrices["bid_price"]
        selectedSymbolAskPrice = selectedSymbolPrices["ask_price"]

        # SET STOP LOSS
        if selectedSymbolLastPrice == 0:
            selectedSymbolLastPrice = round(selectedSymbolBidPrice, 8)
            selectedSymbolStopLossPrice = calculate_calculate_percent_price(selectedSymbolLastPrice, stopLossPercent)
            selectedSymbolSellPrice = calculate_calculate_percent_price(selectedSymbolLastPrice, takeProfitPercent)

        # TAKE PROFIT UPDATE
        if selectedSymbolBidPrice > selectedSymbolLastPrice and selectedSymbolBidPrice > selectedSymbolInitialBuyPrice:
            selectedSymbolLastPrice = round(selectedSymbolBidPrice, 8)
            selectedSymbolSellPrice = calculate_calculate_percent_price(selectedSymbolBidPrice, takeProfitPercent)
            print(stylize("New price target: " + str(selectedSymbolBidPrice), colored.fg("yellow")))

        print_current_status(selectedSymbolBidPrice, selectedSymbolAskPrice, selectedSymbolSellPrice,
                             selectedSymbolStopLossPrice, selectedSymbolInitialBuyPrice)

        # STOP LOSS SELL
        if selectedSymbolBidPrice <= selectedSymbolStopLossPrice:
            quantity = calculate_quantity(selectedSymbolBalance, selectedSymbolMinLotSize)
            # order = client.order_market_sell(symbol=selectedSymbol, quantity=quantity)
            print_stop_loss_result(quantity, selectedSymbolStopLossPrice)
            break

        # TAKE PROFIT SELL
        if selectedSymbolBidPrice <= selectedSymbolSellPrice:
            if selectedSymbolBidPrice > selectedSymbolInitialBuyPrice:
                quantity = calculate_quantity(selectedSymbolBalance, selectedSymbolMinLotSize)
                # order = client.order_limit_sell(symbol=selectedSymbol, quantity=quantity,price=str(selectedSymbolSellPrice))
                print_take_profit_result(quantity, selectedSymbolSellPrice)
                break

        selectedSymbolLastPrice = round(selectedSymbolBidPrice, 8)
        time.sleep(0.5)
