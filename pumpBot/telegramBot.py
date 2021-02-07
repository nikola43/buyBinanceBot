# A simple script to print some messages.
import os
import sys
import time

from telethon import TelegramClient, events, utils

def get_coin_name(text):
    substring = "$"
    coin = ""

    try:
        i = text.index(substring)
        coin = text[i:]
        coin = coin.split(" ")[0]
        print(coin)
        print(i)
    except ValueError:
        print("Not found!")
    else:
        print("Found!")
    return coin

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


session = "test"
api_id = 2156362
api_hash = "0d96604bf1fa9092de979309d1606466"
proxy = None  # https://github.com/Anorov/PySocks

# Create and start the client so we can make requests (we don't here)
client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()


# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".
@client.on(events.NewMessage())#pattern=r'(?i).*\b(hello|hi)\b'))
async def handler(event):
    sender = await event.get_sender()
    #client.get_input_entity(PeerChannel(fwd.from_id))
    #channel = await event.get_channel()

    #group = event.group()
    #group = event.get_group()
    #print(group)
    #print(utils.get_peer_id(sender))
    #print(utils.get_input_location(sender))
    #print(utils.get_input_dialog(sender))
    #print(utils.get_inner_text(sender))

    #print(utils.get_extension(sender))
    #print(utils.get_attributes(sender))
    #print(utils.get_input_user(sender))

    name = utils.get_display_name(sender)
    print('said', event.text)
    coin = get_coin_name(event.txt)

    if len(coin) > 0:
        print("buy")


    #print(utils.get_input_entity(PeerChannel(sender)))
    #print(utils.get_input_channel(get_input_peer(channel)))

    

try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()

# Note: We used try/finally to show it can be done this way, but using:
#
#   with client:
#       client.run_until_disconnected()
#
# is almost always a better idea.