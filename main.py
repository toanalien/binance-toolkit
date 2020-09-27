#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
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

exchange = ccxt.binance(
    {"apiKey": api_key, "secret": secret_key, "enableRateLimit": True}
)

# load ticker price

dict_ticker_price = exchange.fetchTickers()
dict_ticker_price = {k.replace("/", ""): v for k, v in dict_ticker_price.items()}

# print(dict_ticker_price['BTCUSDT']['bid'])
intrade_symbol = []

# margin isolated account
margin_iso = exchange.sapi_get_margin_isolated_account()

iso_symbol_has_asset = list(
    filter(
        lambda x: x["baseAsset"]["totalAsset"] != "0"
        or x["quoteAsset"]["totalAsset"] != "0",
        margin_iso["assets"],
    )
)

print("\nMargin Isolated Account\n")
list(
    map(
        lambda x: print("{:>20}: {:>10}".format(x, margin_iso[x])),
        ["totalAssetOfBtc", "totalLiabilityOfBtc", "totalNetAssetOfBtc"],
    )
)


print(
    "\n{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
        "asset",
        "borrowed",
        "free",
        "interest",
        "netAsset",
        "netAssetOfBtc",
        "totalAsset",
        "liquidatePrice",
        "marginLevel",
    )
)

print("-" * 135)
list(
    map(
        lambda x: (
            print(
                "{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
                    x["baseAsset"]["asset"],
                    x["baseAsset"]["borrowed"],
                    x["baseAsset"]["free"],
                    x["baseAsset"]["interest"],
                    x["baseAsset"]["netAsset"],
                    x["baseAsset"]["netAssetOfBtc"],
                    x["baseAsset"]["totalAsset"],
                    x["liquidatePrice"],
                    x["marginLevel"],
                )
            ),
            print(
                "{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
                    x["quoteAsset"]["asset"],
                    x["quoteAsset"]["borrowed"],
                    x["quoteAsset"]["free"],
                    x["quoteAsset"]["interest"],
                    x["quoteAsset"]["netAsset"],
                    x["quoteAsset"]["netAssetOfBtc"],
                    x["quoteAsset"]["totalAsset"],
                )
            ),
        ),
        iso_symbol_has_asset,
    ),
)

# margin cross account
margin_cro = exchange.sapi_get_margin_account()
cro_symbol_has_asset = list(
    filter(
        lambda x: x["netAsset"] != "0",
        margin_cro["userAssets"],
    )
)
print("\nMargin Cross Account\n")

margin_cro["totalNetAssetOfUSDT"] = float(margin_cro["totalNetAssetOfBtc"]) * float(
    dict_ticker_price["BTCUSDT"]["bid"]
)

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
    )
)
print(
    "\n{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
        "asset",
        "borrowed",
        "free",
        "interest",
        "locked",
        "netAsset",
    )
)
print("-" * 90)
list(
    map(
        lambda x: print(
            "{:>10}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
                x["asset"],
                x["borrowed"],
                x["free"],
                x["interest"],
                x["locked"],
                x["netAsset"],
            )
        ),
        cro_symbol_has_asset,
    )
)


margin_openorders = exchange.sapi_get_margin_openorders()

intrade_symbol = (
    intrade_symbol
    + list(map(lambda x: x["symbol"], iso_symbol_has_asset))
    + list(map(lambda x: x["symbol"], margin_openorders))
    + list(
        map(
            lambda x: f"{x['asset']}USDT"
            if not x["asset"].replace("/", "") in ["USDT"]
            else "",
            cro_symbol_has_asset,
        )
    )
)

intrade_symbol.remove("")
intrade_symbol = list(dict.fromkeys(intrade_symbol))


margin_all_orders = []

for symbol in intrade_symbol:
    margin_all_orders += exchange.sapi_get_margin_allorders({"symbol": symbol})
    try:
        margin_all_orders += exchange.sapi_get_margin_allorders(
            {"symbol": symbol, "isIsolated": True}
        )
    except:
        pass


margin_all_closed_orders = list(
    filter(
        lambda x: (float(x["executedQty"]) != 0 or x["status"] == "NEW")
        and float(x["time"]) / 1000.0
        > (datetime.now() - timedelta(hours=48)).timestamp(),
        margin_all_orders,
    )
)

print("\nMargin Orders History")
print("-" * 156)
print(
    "{:>10}{:>15}{:>10}{:>15}{:>10}{:>6}{:>10}{:>15}{:>15}{:>15}{:>23}{:>23}".format(
        "symbol",
        "orderId",
        "origQty",
        "executedQty",
        "price",
        "side",
        "status",
        "sum",
        "stopPrice",
        "currentPrice",
        "time",
        "updateTime",
    )
)

list(
    map(
        lambda x: (
            print(
                "{:>10}{:>15}{:>10}{:>15}{:>10}{:>6}{:>10}{:>15.4f}{:>15}{:>15}{:>23}{:>23}".format(
                    x[1]["symbol"],
                    x[1]["orderId"],
                    x[1]["origQty"],
                    x[1]["executedQty"],
                    x[1]["price"],
                    x[1]["side"],
                    x[1]["status"],
                    float(x[1]["executedQty"]) * float(x[1]["price"])
                    if x[1]["side"] == "FILLED"
                    else float(x[1]["origQty"])
                    * float(dict_ticker_price[x[1]["symbol"]]["last"]),
                    x[1]["stopPrice"],
                    dict_ticker_price[x[1]["symbol"]]["last"],
                    datetime.fromtimestamp(x[1]["time"] / 1000.0).strftime(
                        "%d/%m/%Y, %H:%M:%S%z"
                    ),
                    datetime.fromtimestamp(x[1]["updateTime"] / 1000.0).strftime(
                        "%d/%m/%Y, %H:%M:%S%z"
                    ),
                )
            ),
            print("-" * 10)
            if x[0] != len(margin_all_closed_orders) - 1
            and x[1]["symbol"] != margin_all_closed_orders[x[0] + 1]["symbol"]
            else None,
        ),
        enumerate(margin_all_closed_orders),
    )
)
