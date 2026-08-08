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

liquid_mid_caps = [
    "RDDT",    # ATI Inc. (Materials/Aerospace Metals)
    "TSLA",   # Allegro MicroSystems (Semiconductors)
    "SOFI",   # Exelixis Inc. (Biotechnology)
    "PLTR",   # Chart Industries (Industrial Equipment)
]

all_ug = pd.DataFrame()

for stonk in liquid_mid_caps:
    underlying_request = StockBarsRequest(
        symbol_or_symbols=stonk,
        timeframe=TimeFrame.Day,
        start=datetime(2025, 9, 1),
        end=datetime(2025, 9, 30)
    )

    ug = stock_historical_data_client.get_stock_bars(underlying_request).df.reset_index()
    ug["ticker"] = stonk
    ug["previous"] = ug["close"].shift(1)

    epstein = []

    def history(high, low, close, previous):
        daily_variance = 0.5 * (math.log(high / low) ** 2) - (2 * math.log(2) - 1) * (math.log(close / previous) ** 2)
        return daily_variance

    for index, row in ug.iterrows():
        result = history(row["high"], row["low"], row["close"], row["previous"])
        epstein.append(result)

    epstein.pop(0)
    historic = sum(epstein) / len(epstein)
    annual = (historic ** 0.5) * 15.8745
    all_ug = pd.concat([all_ug, ug], ignore_index=True)
    print(stonk ,annual)
ticker = 0
jake = [] 

for index, row in all_ug.iterrows():
    price = row["close"]
    stock_symbol = row["ticker"]
    
    tim = chain(
        underlying_symbols=stock_symbol,  
        expiration_date_gte="2026-09-01",
        expiration_date_lte="2026-09-30",
        strike_price_gte=price * 0.99,
        strike_price_lte=price * 1.01,
        contract_type=ContractType.CALL,
    )
    if not tim.empty:
        for contract in tim["symbol"].tolist():
            jake.append((stock_symbol, contract))

umy = []
dmy=[]
for stock_symbol, target_symbol in jake:
    snapshot_config = OptionSnapshotRequest(symbol_or_symbols=target_symbol)
    all_snapshots = option_data_client.get_option_snapshot(snapshot_config)
    single_snapshot = all_snapshots[target_symbol]

    if single_snapshot.implied_volatility is not None:
        marvin = single_snapshot.implied_volatility
        '''
        print(target_symbol, marvin)
        '''
        umy.append(stock_symbol)
        dmy.append(marvin)
    else:
        '''
        print(target_symbol, "Implied Volatility: N/A")
        '''
umy = pd.DataFrame(umy, columns=["symbol"])
umy["volatility"] = dmy

for category, group in umy.groupby("symbol"):
    cool=(category + " - " + str(group["volatility"].mean()))
    print(category + " - " + str(group["volatility"].mean()))

