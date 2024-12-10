import os
from datetime import datetime
from requests import get
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS  
from dotenv import load_dotenv


load_dotenv()

INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUX_URL = "http://localhost:8086"  

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

write_api = client.write_api(write_options=SYNCHRONOUS)  

URL = 'https://production.api.coindesk.com/v2/tb/price/ticker?assets='

def defaults(args):
    if len(args) == 0:
        raise Exception("Missing argument...")

    final_url = URL + args
    result = get(final_url)
    json_data = result.json()

    individual_symbols = args.split(',')
    results = []

    for s in individual_symbols:
        coin_data = json_data['data'][s]
        results.append({
            "symbol": s,
            "iso": coin_data['iso'],
            "name": coin_data['name'],
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S%z"),
            "current_price": coin_data['ohlc']['c'],
            "open": coin_data['ohlc']['o'],
            "high": coin_data['ohlc']['h'],
            "low": coin_data['ohlc']['l'],
            "close": coin_data['ohlc']['c']
        })

    return results

def send_to_influxdb(data):
    for data_point in data:
        symbol = data_point["symbol"]
        measurement = f"stock-price-{symbol}" 
        point = Point(measurement) \
            .tag("symbol", data_point["symbol"]) \
            .field("current_price", data_point["current_price"]) \
            .field("open", data_point["open"]) \
            .field("high", data_point["high"]) \
            .field("low", data_point["low"]) \
            .field("close", data_point["close"]) \
            .time(datetime.utcnow(), WritePrecision.S)

        write_api.write(bucket=INFLUX_BUCKET, record=point)


def retrieve_real_time_data(stock_symbols):
    while True:
        data = defaults(stock_symbols)
        send_to_influxdb(data)

if __name__ == "__main__":
    stock_symbols = 'BTC,ETH,ETHFI,DOGE,ZETA,BNB,SHIB,SOL,TON,WIF,OKB,PEPE,RUNE,AVA,INJ,SUN' 

    retrieve_real_time_data(stock_symbols)
