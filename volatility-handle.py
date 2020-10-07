"""

Concept:
- When bearish market:
    + Cancel all orders
    + Sell all free assets remaining; don't care borrowed

- When bullish market:
    + Cancel all orders
    + Calculate which assets borrowed
        + If free >= borrow -> repay
        + If free < borrow; buy market, amount = borrow - free; -> repay

When Bull or Bear

Idea 1:
- Calculate Polynomial Regression (PR), if Total Balance (TB) crossing down -> BEAR; Vice versa

Idea 2:
- In Grid Trading (5 orders per side), if 3 sell orders filled; -> BEAR; Vice versa

"""
