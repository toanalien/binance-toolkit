#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import pprint
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

if sys.argv[1].upper() == 'ALL':
    margin_openorders = exchange.sapi_get_margin_openorders()
    for order in margin_openorders:
        order = exchange.sapi_delete_margin_order({
            'symbol': order['symbol'],
            'orderId': order['orderId']
        })
        pp.pprint(order)
else:
    symbol = sys.argv[1].upper()
    order_id = sys.argv[2]

    order = exchange.sapi_delete_margin_order({
        'symbol': symbol,
        'orderId': order_id
    })

    pp.pprint(order)