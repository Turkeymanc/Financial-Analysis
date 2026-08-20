import nest_asyncio
nest_asyncio.apply()
from pandas_ta import rsi
import sys
import time
import pandas as pd
from datetime import datetime, timedelta, timezone
import numpy as np
import asyncio
from types import SimpleNamespace
import math  
import yfinance as yf
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, ContractType, PositionIntent
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest
)
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest, 
    OptionSnapshotRequest, 
    OptionBarsRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.stream import TradingStream
from alpaca.data.live import StockDataStream
from alpaca.data.enums import DataFeed

option_data_client = OptionHistoricalDataClient(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT", 
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas" 
)

stock_data_stream = StockDataStream(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT", 
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas", 
    feed=DataFeed.IEX
)

trading_stream = TradingStream(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT", 
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas",
    paper=True
)

trading_client = TradingClient(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT",
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas",
    paper=True
)

stock_historical_data_client = StockHistoricalDataClient(
    "PKY3U5DGLHBFMNQUNIAHDFUKMT", 
    "4ZGE4pAXWXxNPAiGTd5wCq2vnL7Nfesa7C4ytYQwvWas"
)

account = trading_client.get_account()
portfolio = float(account.portfolio_value)
dave = account.buying_power


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
    global has_position
    print(f"Order update: {update.order.id}")
    print(f"Filled QTY: {update.qty}")
    print(f"Filled Price: {update.price}")
    print(f"Status:{update.order.status}")
    if update.order.status == 'filled' and update.order.side == OrderSide.SELL:
        has_position = False
        print("--- Position successfully closed via take profit limit! ---")

async def handle_quotes(quote):
    print("New Quote")
    print(quote)
async def handle_trades(trade):
    print("New Trade")
    print(trade)
async def handle_bars(bar):
    print("New Bar")
    print(bar)
    

def chain(underlying_symbols, expiration_date_gte=None, expiration_date_lte=None, strike_price_gte=None, strike_price_lte=None, contract_type=None):
    option_contracts = []
    params = GetOptionContractsRequest(
        underlying_symbols=[underlying_symbols], 
        expiration_date_gte=expiration_date_gte,
        expiration_date_lte=expiration_date_lte,
        strike_price_gte=str(strike_price_gte) if strike_price_gte else None,
        strike_price_lte=str(strike_price_lte) if strike_price_lte else None,
        type=contract_type,
        limit=10000
    )
    options = trading_client.get_option_contracts(params) 
    option_contracts.extend(options.option_contracts)
    
    while options.next_page_token:
        params.page_token = options.next_page_token
        options = trading_client.get_option_contracts(params) 
        option_contracts.extend(options.option_contracts)
        
        
        
    return Util.to_dataframe(option_contracts)
liquid_mid_caps = ["FTNT"]

all_ug = pd.DataFrame()
for stonk in liquid_mid_caps:
    underlying_request = StockBarsRequest(
        symbol_or_symbols=stonk,
        timeframe=TimeFrame.Day,
        start=datetime(2026, 8, 10),
        end=datetime(2026, 8, 17)
    )

    ug = stock_historical_data_client.get_stock_bars(underlying_request).df.reset_index()
    ug["ticker"] = stonk
    all_ug = pd.concat([all_ug, ug], ignore_index=True)


jake=[]
snake=[]
dake=[]
imp=[]
for index, row in all_ug.iterrows():
    price = row["close"]
    stock_symbol = row["ticker"]
    tim = chain(
        underlying_symbols=stock_symbol,  
        expiration_date_gte="2026-09-11",
        expiration_date_lte="2026-09-11",
        strike_price_gte=price * 0.95,
        strike_price_lte=price * 1.05,
        contract_type=ContractType.CALL,
    )
    jake.append(tim.close_price)
    dake.append(tim.strike_price)
    snake.append(tim.expiration_date)
    imp.append(tim.symbol)
ag = pd.DataFrame({
    "price": pd.concat(jake),
    "strike": pd.concat(dake),
    "expiration": pd.concat(snake),
    "symbol": pd.concat(imp)
})

ag = ag.drop_duplicates("symbol").sort_values("strike")



fake=[]
take=[]
late=[]
simp=[]
for index, row in all_ug.iterrows():
    price = row["close"]
    stock_symbol = row["ticker"]
    tim = chain(
        underlying_symbols=stock_symbol,  
        expiration_date_gte="2026-09-11",
        expiration_date_lte="2026-09-11",
        strike_price_gte=price * 0.95,
        strike_price_lte=price * 1.05,
        contract_type=ContractType.PUT,
    )
    fake.append(tim.close_price)
    take.append(tim.strike_price)
    late.append(tim.expiration_date)
    simp.append(tim.symbol)
    
g = pd.DataFrame({
    "price": pd.concat(fake),
    "strike": pd.concat(take),
    "expiration": pd.concat(late),
    "symbol": pd.concat(simp)
})
g = g.drop_duplicates("symbol").sort_values("strike")


rubix=[]
for target_symbol in g["symbol"]:
    snapshot_config = OptionSnapshotRequest(symbol_or_symbols=target_symbol)
    all_snapshots = option_data_client.get_option_snapshot(snapshot_config)
    single_snapshot = all_snapshots[target_symbol]
    if single_snapshot.implied_volatility is not None:
        option_ask = single_snapshot.latest_quote.ask_price
        rubix.append(option_ask)
g["ask"] = rubix


ubix=[]
for target_symbol in ag["symbol"]:
    snapshot_config = OptionSnapshotRequest(symbol_or_symbols=target_symbol)
    all_snapshots = option_data_client.get_option_snapshot(snapshot_config)
    single_snapshot = all_snapshots[target_symbol]
    if single_snapshot.implied_volatility is not None:
        option_bid = single_snapshot.latest_quote.bid_price
        ubix.append(option_bid)
ag["bid"] = ubix

ticker = yf.Ticker("FTNT")
current_price = ticker.fast_info["last_price"]
print(current_price)


ag["ask"]=rubix
conversion=[]
for index, row in ag.iterrows():
   ender=current_price+row["ask"]-row["bid"]
   david=float(row["strike"])*math.exp(-0.037*(22/365))-ender
   conversion.append(david)
print(conversion)


