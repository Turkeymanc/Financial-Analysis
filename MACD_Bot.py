import nest_asyncio
nest_asyncio.apply()
from pandas_ta import macd

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

# Configured explicitly with your secret key and the free IEX data feed
stock_data_stream = StockDataStream(
    'PKY3U5DGLHBFMNQUNIAHDFUKMT',
    '4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas',
    feed=DataFeed.IEX
)

trading_stream = TradingStream(
    'PKY3U5DGLHBFMNQUNIAHDFUKMT',
    '4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas',
    paper=True
)

# Alpaca Paper Trading
trading_client = TradingClient(
    'PKY3U5DGLHBFMNQUNIAHDFUKMT',
    '4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas',
    paper=True
)

stock_historical_data_client = StockHistoricalDataClient(
    'PKY3U5DGLHBFMNQUNIAHDFUKMT',
    '4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas'
)

stock_bars_request = StockBarsRequest(
    symbol_or_symbols="TSLA",
    timeframe=TimeFrame.Day,
    start=datetime(2026, 6, 10, 15),
    end=datetime(2026, 6, 25, 15)
)

account = trading_client.get_account()

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

'''
market_order_request = MarketOrderRequest(
    symbol="TSLA",
    qty=1,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC
)

order_data = trading_client.submit_order(
    order_data=market_order_request
)

limit_order_request = LimitOrderRequest(
    symbol="NVDA",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC,
    limit_price=200.00
)

limit_order = trading_client.submit_order(
    order_data=limit_order_request
)

stop_order_request = StopOrderRequest(
    symbol="NVDA",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC,
    stop_price=320
)

stop_order = trading_client.submit_order(
    order_data=stop_order_request
)
'''

async def handle_order_update(update):
    print(f"Order update: {update.order.id}")
    print(f"Filled QTY: {update.qty}")
    print(f"Filled Price: {update.price}")
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

'''
async def main():
    stock_data_stream.subscribe_quotes(handle_quotes, 'SPCX')
    stock_data_stream.subscribe_trades(handle_trades, 'SPCX')
    stock_data_stream.subscribe_bars(handle_bars, 'AMD')
    # The SDK manages its own connection loop internally
    await stock_data_stream.run()


if __name__ == "__main__":
    asyncio.run(main())
'''

#
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

initial_test_bars = [
    SimpleNamespace(
        open=b.open,
        high=b.high,
        low=b.low,
        close=b.close,
        volume=b.volume
    )
    for b in tsla_bars
]

bars = []

has_position = False

async def on_new_bar(bar):
    global bars
    global has_position
    bars.append(bar)
    if len(bars) < 35:
        print(f"Not enough data for macd Calculation: {len(bars)}/35")
    else:
        df = Util.to_dataframe(bars)
        macd_did = macd(df['close'], fast=12, slow=26, signal=9)        
        print(f"macd:\n{macd_did.tail(1)}")
        
        df['MACD_Histogram'] = macd_did['MACDh_12_26_9']
        
        if df['MACD_Histogram'].iloc[-1] > 0 and not has_position:
            print("BUY TSLA")
            has_position = True
            trading_client.submit_order(
                order_data=MarketOrderRequest(
                    symbol="TSLA",
                    qty=100,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            )
        elif df['MACD_Histogram'].iloc[-1] < 0 and has_position:
            print("SELL TSLA")
            has_position = False

            trading_client.submit_order(
                order_data=MarketOrderRequest(
                    symbol="TSLA",
                    qty=100,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            )

async def main():
    print("Pre-loading historical test bars...")
    bars.extend(initial_test_bars)

    stock_data_stream.subscribe_bars(on_new_bar, "TSLA")

    print("Waiting for live market data...")
    await stock_data_stream.run()

if __name__ == "__main__":
    asyncio.run(main())
