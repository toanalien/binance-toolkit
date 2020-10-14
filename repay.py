#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pprint
import sys
import time
from datetime import datetime, timedelta
from functools import reduce
from operator import itemgetter
import ccxt
import requests
from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()

local_tz = os.environ.get("local_tz", "UTC")
os.environ["TZ"] = local_tz
time.tzset()

# logging.basicConfig(level=logging.DEBUG)

api_key = os.environ.get("apiKey")
secret_key = os.environ.get("secretKey")
bot_token = os.environ.get("bot_token")
bot_chatID = os.environ.get("bot_chatID")

if not (api_key and secret_key):
    logging.error("api_key or secret_key is empty")
    exit(1)

exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret_key,
    "enableRateLimit": True,
    "market": "margin",
})

# load ticker price

dict_ticker_price = exchange.fetchTickers()
dict_ticker_price = {
    k.replace("/", ""): v
    for k, v in dict_ticker_price.items()
}

# symbol = sys.argv[1].upper()

margin_cro = exchange.sapi_get_margin_account()

cro_symbol_has_asset = list(
    filter(
        lambda x: x["borrowed"] != "0" and x["free"] != "0",
        margin_cro["userAssets"],
    ))
print("\nMargin Cross Account\n")

margin_cro["totalNetAssetOfUSDT"] = float(
    margin_cro["totalNetAssetOfBtc"]) * float(
        dict_ticker_price["BTCUSDT"]["bid"])

list(
    map(
        lambda x: print("{:>20}: {:>10}".format(x, margin_cro[x])),
        [
            "marginLevel",
            "totalAssetOfBtc",
            "totalLiabilityOfBtc",
            "totalNetAssetOfBtc",
            "totalNetAssetOfUSDT",
        ],
    ))
print("\n{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
    "asset",
    "borrowed",
    "free",
    "interest",
    "locked",
    "netAsset",
))
print("-" * 90)
list(
    map(
        lambda x: print("{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
            x["asset"],
            x["borrowed"],
            x["free"],
            x["interest"],
            x["locked"],
            x["netAsset"],
        )),
        cro_symbol_has_asset,
    ))


def telegram_bot_sendtext(bot_message, parse_mode='Markdown'):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=' + parse_mode + '&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def repay(asset):
    amount = asset['borrowed'] if float(asset['borrowed']) < float(
        asset['free']) else asset['free']
    trans = exchange.sapi_post_margin_repay({
        'asset': asset['asset'],
        'amount': amount
    })

    telegram_bot_sendtext("{}\n{}".format(
        datetime.now().strftime('%Y-%m-%d %H:%M'), trans),
                          parse_mode='HTML')
    return trans


print(list(map(repay, cro_symbol_has_asset)))