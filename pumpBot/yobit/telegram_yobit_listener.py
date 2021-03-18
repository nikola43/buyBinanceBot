import os
from telethon import TelegramClient, events
import colored
from colored import stylize
import os
import discord
import logging
import pandas as pd


def get_telegram_coin_name(text):
    print(str(text[text.index(" "):].split(" ")[4].replace("*", "")))
    if "The Coin is" in text:
        try:
            return str(text[text.index(" "):].split(" ")[4].replace("*", ""))
        except ValueError:
            return None
    return None


# Discord
# logging.basicConfig(level=logging.INFO)

# client = discord.Client()
# guild = discord.Guild

session = "test"
api_id = 2156362
api_hash = "0d96604bf1fa9092de979309d1606466"
proxy = None  # https://github.com/Anorov/PySocks
telegram = TelegramClient(session, api_id, api_hash, proxy=None).start()


# @client.event
# async def on_ready():
#     print('We have logged in as {0.user}'.format(client))
#     await client.change_presence(activity=discord.Game('_scan help'))
#
# @client.event
# async def on_message(message):
#     print(message)

# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".
@telegram.on(events.NewMessage())  # pattern=r'(?i).*\b(hello|hi)\b'))
async def handler(event):
    sender = await event.get_sender()
    print("sender.id")
    print(sender.id)


    if str(sender.id) == str("358896373"):
        print("yo")

    if str(sender.id) == str("1463366726"):
        print("yo")

    coin = get_telegram_coin_name(event.text)
    # sender = await event.get_sender()
    print(stylize("said", colored.fg("red")))
    print(stylize(event.text, colored.fg("red")))
    # print(stylize("coin: " + coin, colored.fg("red")))

    if coin is not None:
        try:
            os.remove("asset.txt")
        except:
            print("")
        f = open("asset.txt", "w")
        f.write(coin)
        f.close()
        print("Coin selected " + coin)
        telegram.disconnect()


if __name__ == "__main__":
    try:
        os.remove("asset.txt")
    except:
        print("")

    # client.run("ODA5MTE1MjA3Mjk2ODc2NTQ0.YCQZQg.XYoygp6NRXxAEPlpH09F7jNBQrM")
    print("listening telegram")
    telegram.run_until_disconnected()
    telegram.disconnect()