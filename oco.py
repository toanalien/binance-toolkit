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

from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()

local_tz = os.environ.get("local_tz", "UTC")
os.environ["TZ"] = local_tz
time.tzset()

logging.basicConfig(level=logging.DEBUG)

api_key = os.environ.get("apiKey")
secret_key = os.environ.get("secretKey")

if not (api_key and secret_key):
    logging.error("api_key or secret_key is empty")
    exit(1)

symbol = sys.argv[1].upper()
side = sys.argv[2].upper()
entry_price = float(sys.argv[3])
quantity = float(sys.argv[4])
percent_profit_stoploss = float(sys.argv[5])

exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret_key,
    "enableRateLimit": True,
    "market": "margin",
})

print(side)

if side == "BUY":
    side_effect_type = "MARGIN_BUY"
    price = round(entry_price * (100 - percent_profit_stoploss) / 100, 4)
    stopLimitPrice = round(entry_price * (100 + percent_profit_stoploss) / 100,
                           4)
    stopPrice = stopLimitPrice
elif side == "SELL":
    side_effect_type = "NO_SIDE_EFFECT"
    price = round(entry_price * (100 + percent_profit_stoploss) / 100, 2)
    stopLimitPrice = round(entry_price * (100 - percent_profit_stoploss) / 100,
                           2)
    stopPrice = stopLimitPrice
else:
    sys.exit()

order = exchange.sapi_post_margin_order({
    "symbol": symbol,
    "side": side,
    "type": "LIMIT",
    "timeInForce": "GTC",
    "sideEffectType": side_effect_type,
    "quantity": quantity,
    "price": price,
    "isOco": "true",
    "stopLimitPrice": stopLimitPrice,
    "stopPrice": stopPrice,
    "stopLimitTimeInForce": "GTC",
})

print(order)

# python oco.py LINKUSDT SELL 10.6177 1.88 3