#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ccxt
import pprint
import logging
from dotenv import load_dotenv

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()


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

# margin isolated account
margin_iso = exchange.sapi_get_margin_isolated_account()
iso_symbol_has_asset = list(
    filter(
        lambda x: x["baseAsset"]["totalAsset"] != "0"
        or x["quoteAsset"]["totalAsset"] != "0",
        margin_iso["assets"],
    )
)
print("Margin Isolated Account\n")
list(
    map(
        lambda x: print("{:>20}: {:>10}".format(x, margin_iso[x])),
        ["totalAssetOfBtc", "totalLiabilityOfBtc", "totalNetAssetOfBtc"],
    )
)
print(
    "{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
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
list(
    map(
        lambda x: (
            print(
                "{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
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
                "{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
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
print("=" * 7)
# margin cross account
margin_cro = exchange.sapi_get_margin_account()
cro_symbol_has_asset = list(
    filter(
        lambda x: x["netAsset"] != "0",
        margin_cro["userAssets"],
    )
)
print("Margin Cross Account\n")

list(
    map(
        lambda x: print("{:>20}: {:>10}".format(x, margin_cro[x])),
        ["marginLevel", "totalAssetOfBtc", "totalLiabilityOfBtc", "totalNetAssetOfBtc"],
    )
)
print(
    "{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
        "asset",
        "borrowed",
        "free",
        "interest",
        "locked",
        "netAsset",
    )
)
list(
    map(
        lambda x: print(
            "{:>15}{:>15}{:>15}{:>15}{:>15}{:>15}".format(
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
