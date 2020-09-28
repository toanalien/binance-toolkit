#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

entry_price = float(sys.argv[1])
percent = float(sys.argv[2])

print(
    "entry: {}\n{:.5f}\t{:.5f}".format(
        entry_price,
        entry_price * (100 - percent) / 100,
        entry_price * (100 + percent) / 100,
    )
)
