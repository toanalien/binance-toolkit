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
```

## Run

```bash
python main.py
```

### Auto repay

```
crontab -e
*/5 * * * * source /home/toanalien/binance-toolkit/venv/bin/activate; python /home/toanalien/binance-toolkit/repay.py >> /home/toanalien/repay.log 2>&1
0 * * * * source /home/toanalien/binance-toolkit/venv/bin/activate; python /home/toanalien/binance-toolkit/report.py >> /home/toanalien/report.log 2>&1
```
