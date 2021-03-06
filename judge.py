#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Concept:
- When bearish market:
    + Cancel all orders
    + Sell all free assets remaining; don't care borrowed

- When bullish market:
    + Cancel all orders
    + Calculate which assets borrowed
        + If free < borrow; buy market, amount = borrow - free; -> repay

When Bull or Bear

Idea 1:
- Calculate Polynomial Regression (PR), if Total Balance (TB) crossing down -> BEAR; Vice versa

Idea 2:
- In Grid Trading (5 orders per side), if 3 sell orders filled; -> BEAR; Vice versa

"""

import json
import logging
import math
import os
import pprint
import sys
import time
import urllib.parse
from datetime import datetime, timedelta
from functools import reduce
from operator import itemgetter

import ccxt
import requests
from ccxt.base.errors import InvalidOrder

from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()

local_tz = os.environ.get("local_tz", "UTC")
os.environ["TZ"] = local_tz
time.tzset()

# logging.basicConfig(
#     filename="app.log",
#     filemode="a",
#     format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
#     datefmt="%d-%b-%y %H:%M:%S%z",
#     level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
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
    "enableRateLimit": True
})

margin_cro = exchange.sapi_get_margin_account()


def precision_and_scale(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return (magnitude, 0)
    frac_part = abs(x) - int_part
    multiplier = 10**(max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return (magnitude + scale, scale)


dict_ticker_price = exchange.fetchTickers()
dict_ticker_price = {
    k.replace("/", ""): v
    for k, v in dict_ticker_price.items()
}


def telegram_bot_sendtext(bot_message, parse_mode='Markdown'):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=' + parse_mode + '&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


# load ticker price

dict_ticker_price = exchange.fetchTickers()
dict_ticker_price = {
    k.replace("/", ""): v
    for k, v in dict_ticker_price.items()
}

dict_market = {}

markets = exchange.fetchMarkets()

for market in markets:
    dict_market[market['id']] = market

# print(stoploss)


def cancel_all_orders():
    margin_openorders = exchange.sapi_get_margin_openorders()

    # stop all orders
    if len(margin_openorders) > 0:
        telegram_bot_sendtext("{}\nStop *{}* orders".format(
            datetime.now().strftime('%Y-%m-%d %H:%M'), len(margin_openorders)))
        for moo in margin_openorders:
            order = exchange.sapi_delete_margin_order({
                'symbol': moo['symbol'],
                'orderId': moo['orderId']
            })

            telegram_bot_sendtext(
                "{}\nCancel {} *{}* {} {}".format(
                    datetime.now().strftime('%Y-%m-%d %H:%M'),
                    order['orderId'], order['symbol'], order['origQty'],
                    order['price']), )


def sell_all_assets():
    cro_symbol_has_asset = list(
        filter(
            lambda x: x["free"] != "0" and x["asset"] != "USDT",
            margin_cro["userAssets"],
        ))

    for symbol in cro_symbol_has_asset:
        try:
            order = exchange.sapi_post_margin_order({
                'symbol':
                symbol['asset'] + 'USDT',
                'side':
                'SELL',
                'quantity':
                symbol['free'],
                'type':
                'MARKET',
            })
            telegram_bot_sendtext("{}\n{}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M'), order),
                                  parse_mode='HTML')
        except InvalidOrder as e:
            telegram_bot_sendtext("{}\n{}\n{}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                urllib.parse.quote(str(e)), symbol),
                                  parse_mode='HTML')


def repay(asset):
    amount = asset['borrowed'] if float(asset['borrowed']) < float(
        asset['free']) else asset['free']
    trans = exchange.sapi_post_margin_repay({
        'asset': asset['asset'],
        'amount': amount
    })
    return trans


def repay_all_assets():
    cro_symbol_has_asset = list(
        filter(
            lambda x:
            (float(x["free"]) < float(x["borrowed"])) and x["asset"] != "USDT",
            margin_cro["userAssets"],
        ))

    for symbol in cro_symbol_has_asset:
        try:
            _symbol = symbol['asset'] + 'USDT'
            filters = dict_market[_symbol]['info']['filters']
            LOT_SIZE_FILTER = list(
                filter(lambda x: x['filterType'] == 'LOT_SIZE',
                       filters)).pop()

            LOT_SIZE_FILTER_VAL = float(LOT_SIZE_FILTER['minQty'])

            precision = precision_and_scale(float(LOT_SIZE_FILTER_VAL))[-1]

            order = exchange.sapi_post_margin_order({
                'symbol':
                _symbol,
                'side':
                'BUY',
                'quantity':
                round(
                    float(symbol["borrowed"]) - float(symbol["free"]),
                    precision),
                'type':
                'MARKET',
            })

            telegram_bot_sendtext("{}\n{}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M'), order),
                                  parse_mode='HTML')
        except InvalidOrder as e:
            telegram_bot_sendtext("{}\n{}\n{}".format(
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                urllib.parse.quote(str(e)), symbol),
                                  parse_mode='HTML')

    # print(list(map(repay, cro_symbol_has_asset)))


def stoploss_handle():
    cancel_all_orders()
    sell_all_assets()


def takeprofit_handle():
    cancel_all_orders()
    repay_all_assets()


if sys.argv[1] == 'take':
    takeprofit_handle()
elif sys.argv[1] == 'stop':
    stoploss_handle()
else:
    margin_cro = exchange.sapi_get_margin_account()
    margin_cro["totalNetAssetOfUSDT"] = float(
        margin_cro["totalNetAssetOfBtc"]) * float(
            dict_ticker_price["BTCUSDT"]["bid"])
    stoploss = float(sys.argv[1])
    takeprofit = float(sys.argv[2])

    if margin_cro["totalNetAssetOfUSDT"] > takeprofit:
        takeprofit_handle()

    if margin_cro["totalNetAssetOfUSDT"] < stoploss:
        stoploss_handle()
