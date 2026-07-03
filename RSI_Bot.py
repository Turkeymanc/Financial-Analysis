import nest_asyncio
# This patches Python's core asyncio behavior to allow running inside Spyder
nest_asyncio.apply()
from pandas_ta import rsi

import pandas as pd
from datetime import datetime
import numpy as np
import asyncio

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
    symbol_or_symbols="AMD",
    timeframe=TimeFrame.Day,
    start=datetime(2026, 6, 10, 15),
    end=datetime(2026, 6, 25, 15)
)

# Get account information
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

bars=[]
has_position = False
async def on_new_bar(bar):
    global bars
    global has_position
    bars.append(bar)
    if len(bars) <15:
        print("Not enough data for RSI Calculation")
    else:
        df=Util.to_dataframe(bars)
        rsi_value=rsi(df.tail(15).close, length=14).iloc[-1]
        print(f"RSI:{rsi_value}")
        if rsi_value <30 and not has_position:
            print("BUY BTC")
            has_position=True
            trading_client.submit_order(
                MarketOrderRequest(
                    symbol="AMD",
                    qty=0.1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.GTC
                )
            )
        elif rsi_value < 70 and has_position:
            print("SELL BTC")
            has_position = False

            trading_client.submit_order(
                MarketOrderRequest(
                    symbol="AMD",
                    qty=0.1,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC
                )
            )
async def main():
    # Subscribe to 1-minute bars for AMD
    stock_data_stream.subscribe_bars(on_new_bar, "AMD")

    print("Waiting for live market data...")
    await stock_data_stream.run()

if __name__ == "__main__":
    asyncio.run(main())