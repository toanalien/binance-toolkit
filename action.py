#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pprint
import time
from datetime import datetime, timedelta
from functools import reduce
from operator import itemgetter
import sys
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
)

api_key = os.environ.get("apiKey")
secret_key = os.environ.get("secretKey")

if not (api_key and secret_key):
    logging.error("api_key or secret_key is empty")
    exit(1)

exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret_key,
    "enableRateLimit": True
})

symbol = sys.argv[1].upper()
side = sys.argv[2].upper()
quantity = float(sys.argv[3])
arr_price = sys.argv[4:]

print(sys.argv[4:])

side_effect_type = None

if side == 'BUY':
    side_effect_type = 'MARGIN_BUY'
else:
    side_effect_type = 'NO_SIDE_EFFECT'

exchange.sapi_post_margin_loan({
    'asset': symbol.replace('USDT', ''),
    'amount': quantity
})

for price in arr_price:
    price = float(price)
    print(">> {} at {}".format(side, price))
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