# binance-toolkit

## Setup Environment

- Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Fill user data

```bash
cat .env
apiKey=<REPLACE>
secretKey=<REPLACE>
local_tz=<REPLACE>
SAMPLE_SPREADSHEET_ID=<REPLACE>
bot_token=<REPLACE>
bot_chatID=<REPLACE>
```

## Run

```bash
python main.py
```

### Auto repay

```
# crontab -e
*/5 * * * * source /home/toanalien/binance-toolkit/venv/bin/activate; python /home/toanalien/binance-toolkit/repay.py >> /home/toanalien/repay.log 2>&1
0 * * * * source /home/toanalien/binance-toolkit/venv/bin/activate; python /home/toanalien/binance-toolkit/report.py >> /home/toanalien/report.log 2>&1
*/5 * * * * source /home/centos/binance-toolkit/venv/bin/activate; python /home/centos/binance-toolkit/judge.py STOPLOSS_BALANCE TAKEPROFIT_BALANCE >> /home/centos/log/judge.log 2>&1
```

### Report feature

```
- Create Google spreadsheet file, copy file ID
- Open file
  + Add header: Timestamp	In BTC	In USDT	To Date	Change (from cell A1->E1)
  + Choose Tools -> Script editor, and code

function FROM_UNIX_EPOCH(epoch_in_secs) {
    return new Date(epoch_in_secs * 1000).toLocaleString('vi-VN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: false
    }); // Convert to milliseconds
}

```
