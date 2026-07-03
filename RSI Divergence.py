import nest_asyncio
nest_asyncio.apply()
from pandas_ta import rsi

import pandas as pd
from datetime import datetime, timedelta, timezone
import numpy as np
import asyncio
from types import SimpleNamespace
import math  


from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest
)

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.stream import TradingStream
from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed
stock_data_stream=StockDataStream("PKY3U5DGLHBFMNQUNIAHDFUKMT", 
                                  "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas", 
                                  feed=DataFeed.IEX)

trading_stream=TradingStream("PKY3U5DGLHBFMNQUNIAHDFUKMT", 
                             "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas",
                             paper=True)
trading_client=TradingClient("PKY3U5DGLHBFMNQUNIAHDFUKMT",
                             "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas",
                             paper=True
                             )
stock_historical_data_client = StockHistoricalDataClient(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT",
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas"
)
account=trading_client.get_account()

print("Account Number:", account.account_number)
print("Buying Power:", account.buying_power)
print("Currency:", account.currency)

class Util:
    @staticmethod
    def to_dataframe(data):
        data_list = data if isinstance(data, list) else [data]

        try:
            return pd.DataFrame([item.model_dump() for item in data_list])
        except AttributeError:
            try:
                return pd.DataFrame([item.dict() for item in data_list])
            except AttributeError:
                return pd.DataFrame([vars(item) for item in data_list])

async def handle_order_update(update):
    print(f"Order update: {update.order.id}")
    print(f"Filled QTY: {update.qty}")
    print(f"Filled PriceL {update.price}")
    print(f"Status:{update.order.status}")
async def handle_quotes(quote):
    print("New Quote")
    print(quote)
async def handle_trades(trade):
    print("New Trade")
    print(trade)
async def handle_bars(bar):
    print("New Bar")
    print(bar)

print("Fetching real historical bars to prime MACD...")
historical_request = StockBarsRequest(
    symbol_or_symbols="TSLA",
    timeframe=TimeFrame.Minute,
    start=datetime.now(timezone.utc) - timedelta(minutes=60),
    end=datetime.now(timezone.utc),
    feed=DataFeed.IEX
)

historical_data = stock_historical_data_client.get_stock_bars(historical_request)
tsla_bars = historical_data.data.get("TSLA", [])
initial_test_bars = []
for bar in tsla_bars:
    initial_test_bars.append({
        "open": bar.open,
        "high": bar.high,
        "close": bar.close,
        "volume": bar.volume
    })
    
print(historical_data)
print("SCRIPT STARTED")
bars = []
has_position=False


 

async def on_new_bars(bar):
    global bars
    global has_position
    if len(bars)<60:
        print("67")
    else:
        bars.append(bar)
        df = Util.to_dataframe(bars)
        rsi_value=rsi(df.tail(15).close, length=14).iloc[-1]
        print(f"rsi:\n{rsi_value.tail(1)}")

    

async def main():
    print("Pre-loading historical test bars...")
    bars.extend(initial_test_bars)

    stock_data_stream.subscribe_bars(on_new_bars, "TSLA")

    print("Waiting for live market data...")
    await stock_data_stream.run()

if __name__ == "__main__":
    asyncio.run(main())

    