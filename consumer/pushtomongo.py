import os
from datetime import datetime
from requests import get
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['coinstock']  
collection = db['stock_prices']  


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
def send_to_mongodb(data):
    for data_point in data:
  
        collection.insert_one(data_point)
        print(f"Dữ liệu cho {data_point['symbol']} đã được chèn vào MongoDB!")


def retrieve_real_time_data(stock_symbols):
    while True:
        data = defaults(stock_symbols)
        send_to_mongodb(data) 

if __name__ == "__main__":
    stock_symbols = 'BTC' 
    retrieve_real_time_data(stock_symbols)
