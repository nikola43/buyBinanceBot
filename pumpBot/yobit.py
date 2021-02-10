import os
from telethon import TelegramClient, events
import colored
from colored import stylize

def get_coin_name(text):
    try:
        return str(text[text.index(" "):].split(" ")[4].replace("*", ""))
    except ValueError:
        return None

session = "test"
api_id = 2156362
api_hash = "0d96604bf1fa9092de979309d1606466"
proxy = None  # https://github.com/Anorov/PySocks
telegram = TelegramClient(session, api_id, api_hash, proxy=None).start()

# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".
@telegram.on(events.NewMessage())  # pattern=r'(?i).*\b(hello|hi)\b'))
async def handler(event):
    coin = get_coin_name(event.text)
    # sender = await event.get_sender()
    print(stylize("said", colored.fg("red")))
    print(stylize(event.text, colored.fg("red")))
    print(stylize("coin: " + coin, colored.fg("red")))

    if coin is not None:
        f = open("asset.txt", "w")
        f.write(coin)
        f.close()

if __name__ == "__main__":
    try:
        os.remove("asset.txt")
    except:
        print("")

    telegram.run_until_disconnected()
    telegram.disconnect()
