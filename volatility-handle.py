"""
Concept:
- When bearish market:
    + Cancel all orders
    + Sell all free assets remaining; dont care borrowed

- When bullish market:
    + Cancel all orders
    + Calculate which assets borrowed
        + If free >= borrow -> repay
        + If free < borrow; buy market, amount = borrow - free; -> repay
"""
