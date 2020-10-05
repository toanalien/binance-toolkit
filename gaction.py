#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import math
import os
import pprint
import sys
import time
from datetime import datetime, timedelta
from functools import reduce
from operator import itemgetter

import ccxt

from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()

local_tz = os.environ.get("local_tz", "UTC")
os.environ["TZ"] = local_tz
time.tzset()

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S%z",
    level=logging.DEBUG)

api_key = os.environ.get("apiKey")
secret_key = os.environ.get("secretKey")

if not (api_key and secret_key):
    logging.error("api_key or secret_key is empty")
    exit(1)

# https://stackoverflow.com/a/3019027


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


exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret_key,
    "enableRateLimit": True
})

dict_market = {}

markets = exchange.fetchMarkets()

for market in markets:
    dict_market[market['id']] = market

dict_ticker_price = exchange.fetchTickers()
dict_ticker_price = {
    k.replace("/", ""): v
    for k, v in dict_ticker_price.items()
}

symbol = sys.argv[1].upper()
quantity = float(sys.argv[2])
step = float(sys.argv[3])
max_grid = int(sys.argv[4])
side = None
side_effect_type = None

current_price = dict_ticker_price[symbol]["last"]
filters = dict_market[symbol]['info']['filters']
PRICE_FILTER = list(
    filter(lambda x: x['filterType'] == 'PRICE_FILTER', filters)).pop()

PRICE_FILTER_VAL = float(PRICE_FILTER['minPrice'])

precision = precision_and_scale(float(PRICE_FILTER_VAL))[-1]

for i in range(max_grid * -1, max_grid + 1):
    if i == 0:
        continue
    if i < 0:
        side = "BUY"
        side_effect_type = 'MARGIN_BUY'
    else:
        side = "SELL"
        side_effect_type = 'NO_SIDE_EFFECT'

    price = current_price * (100 + i) / 100

    price = round(price, precision)
    print("{} {} at {}".format(side, quantity, round(price, precision)))

    exchange.sapi_post_margin_loan({
        'asset': symbol.replace('USDT', ''),
        'amount': quantity
    })

    order = exchange.sapi_post_margin_order({
        'symbol': symbol,
        'side': side,
        'quantity': quantity,
        'price': price,
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        "sideEffectType": side_effect_type
    })

    pp.pprint(order)
    time.sleep(3)

# python gaction.py symbol quantity_per_order spread total_orders_per_side
# python gaction.py dashusdt 0.2 1 5 (total 5*2 = 10 orders)