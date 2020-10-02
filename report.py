#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ref: https://www.nuomiphp.com/eplan/en/107216.html

from __future__ import print_function

import logging
import os
import os.path
import pickle
import pprint
import sys
import time
from datetime import datetime, timedelta
from functools import reduce
from operator import itemgetter

import ccxt

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

pp = pprint.PrettyPrinter(indent=4)
load_dotenv()

local_tz = os.environ.get("local_tz", "UTC")
os.environ["TZ"] = local_tz
time.tzset()

work_dir = os.path.dirname(os.path.abspath(__file__))
# logging.basicConfig(level=logging.DEBUG)

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

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_SPREADSHEET_ID = os.environ.get('SAMPLE_SPREADSHEET_ID')


def main():
    creds = None
    if os.path.exists(os.path.join(work_dir, 'token.pickle')):
        with open(os.path.join(work_dir, 'token.pickle'), 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                os.path.join(work_dir, 'credentials.json'),
                SCOPES,
                redirect_uri='http://localhost')
            auth_url, _ = flow.authorization_url(prompt='consent')

            print('Please go to this URL: {}'.format(auth_url))
            code = input('Enter the authorization code: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
    with open(os.path.join(work_dir, 'token.pickle'), 'wb') as token:
        pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

    dict_ticker_price = exchange.fetchTickers()
    dict_ticker_price = {
        k.replace("/", ""): v
        for k, v in dict_ticker_price.items()
    }

    margin_cro = exchange.sapi_get_margin_account()

    cro_symbol_has_asset = list(
        filter(
            lambda x: x["free"] != "0" or x["borrowed"] != "0",
            margin_cro["userAssets"],
        ))
    margin_cro["totalNetAssetOfUSDT"] = float(
        margin_cro["totalNetAssetOfBtc"]) * float(
            dict_ticker_price["BTCUSDT"]["bid"])

    values = [
        [
            # Sep 15, 2020, 6:10:59:59 PM
            datetime.now().timestamp(),
            margin_cro["totalNetAssetOfBtc"],
            margin_cro["totalNetAssetOfUSDT"]
        ],
    ]

    body = {'values': values}

    result = service.spreadsheets().values().append(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        body=body,
        valueInputOption='USER_ENTERED',
        range='A1').execute()
    print('{0} cells appended.'.format(result \
                                        .get('updates') \
                                        .get('updatedCells')))


if __name__ == '__main__':
    main()
