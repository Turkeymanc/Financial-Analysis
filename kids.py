import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import time
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
'''
start=dt.datetime.today()-dt.timedelta(10)
end=dt.datetime.today()
ce=yf.download(stocks,start,end)["Close"]
print(ce)
------------------------'''

key_path=r"C:\Users\\Documents\GitHub\StockAnalysis\key.txt"

'''
ts=TimeSeries(key=key_path,output_format='pandas')
dat=ts.get_daily(symbol='USD', outputsize='compact')

'''
'''
------------------------
all_tickers = ["AAPL", "CSCO", "AMZN"]

start = dt.datetime.today() - dt.timedelta(days=30)
end = dt.datetime.today()

# Download close prices
data = yf.download(all_tickers, start, end)["Close"]

print(data)
------------------------
'''
'''
webscrapping
url="https://finance.yahoo.com/quote/AAPL/financials/"
headers={"User-agent":"Chrome/148.0.7778.168"}
page=requests.get(url, headers=headers)
page_content=page.content
soup=BeautifulSoup(page_content,"html.parser")
tabl=soup.find_all("div",{"class":"table yf-yuwun0"})
for t in tabl:
    print(t)
'''

stocks=["AMZN", "FTNT", "AAPL", "CRM"]
start=dt.datetime.today()-dt.timedelta(360)
end=dt.datetime.today()
cl_price=pd.DataFrame()

for ticker in stocks:
    data = yf.download(ticker, start=start, end=end)
    cl_price[ticker] = data["Close"]
'''
def RSI(DF, n=14):
    df = DF.copy()
    
    df["change"] = df["Close"] - df["Close"].shift(1)
    
    df["gain"] = np.where(df["change"] >= 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, -1 * df["change"], 0)
    
    df["avgGain"] = df["gain"].ewm(alpha=1/n, min_periods=n).mean()
    df["avgLoss"] = df["loss"].ewm(alpha=1/n, min_periods=n).mean()
    
    df["rs"] = df["avgGain"] / df["avgLoss"]
    
    df["rsi"] = 100 - (100 / (1 + df["rs"]))
    df["Upper Band"]=70
    df["Lower Band"]=30
    return df["rsi"]
def RI(DF, n=14):
    df = DF.copy()
    
    df["change"] = df["Close"] - df["Close"].shift(1)
    
    df["gain"] = np.where(df["change"] >= 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, -1 * df["change"], 0)
    
    df["avgGain"] = df["gain"].ewm(alpha=1/n, min_periods=n).mean()
    df["avgLoss"] = df["loss"].ewm(alpha=1/n, min_periods=n).mean()
    
    df["rs"] = df["avgGain"] / df["avgLoss"]
    
    df["rsi"] = 100 - (100 / (1 + df["rs"]))
    df["Upper Band"]=70
    df["Lower Band"]=30
    
    return df["Upper Band"]
def RS(DF, n=14):
    df = DF.copy()
    
    df["change"] = df["Close"] - df["Close"].shift(1)
    
    df["gain"] = np.where(df["change"] >= 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, -1 * df["change"], 0)
    
    df["avgGain"] = df["gain"].ewm(alpha=1/n, min_periods=n).mean()
    df["avgLoss"] = df["loss"].ewm(alpha=1/n, min_periods=n).mean()
    
    df["rs"] = df["avgGain"] / df["avgLoss"]
    
    df["rsi"] = 100 - (100 / (1 + df["rs"]))
    df["Upper Band"]=70
    df["Lower Band"]=30
    return df["Lower Band"]

    
Tesla=yf.download("TSLA", start=start, end=end)
hey=pd.DataFrame()
bol=(RSI(Tesla,n=14))
hey["1st"]=bol
hey["2nd"]=(RI(Tesla,n=14))
hey["3rd"]=(RS(Tesla,n=14))
hey.plot(title="tesla Volatility")
plt.show()
print(hey["1st"])
'''

'''
def Boll_Band(DF,n=14):
    df=DF.copy()
    df["MB"]=df["Close"].rolling(n).mean()
    df["UB"]=df["MB"]+2*df["Close"].rolling(n).std(ddof=0)
    df["LB"]=df["MB"]-2*df["Close"].rolling(n).std(ddof=0)
    df["BB_width"]=df["UB"]-df["LB"]
    df["Diddy"]=df["Open"]
    return df[["MB","UB","LB","BB_width","Open"]]

appl=yf.download("FTNT",start=start, end=end )
appl.columns = appl.columns.get_level_values(0)

okay=Boll_Band(appl,n=14)

okay[["MB", "UB", "LB", "Open"]].plot(
    title="AAPL Bollinger Bands"
)
plt.show()
'''
'''
appl=yf.download("AAPL",period="1d", interval="1d" )
    
print(Boll_Band(appl,14))
'''


'''
print(cl_price.describe())
print(cl_price.pct_change())
print(cl_price.head(4).pct_change())
print(cl_price/cl_price.shift(1))
print(cl_price.head(3).shift(1))

'''
'''
daily_return=cl_price.head(12).pct_change()
print(daily_return.mean())
print("----------------------")
print(daily_return.std())
print(daily_return.min())
'''
'''
def MACD(df,a=12, b=26, c=9):
    d=df.copy()
    d["ma_fast"]=d["Close"].ewm(span=a, min_periods=a).mean()
    d["ma_slow"]=d["Close"].ewm(span=b, min_periods=b).mean()
    d["macd"]= d["ma_fast"]- d["ma_slow"]
    d["signal"]=d["macd"].ewm(span=c, min_periods=c).mean()
    return d["macd"]
def KID(df,a=12, b=26, c=9):
    d=df.copy()
    d["ma_fast"]=d["Close"].ewm(span=a, min_periods=a).mean()
    d["ma_slow"]=d["Close"].ewm(span=b, min_periods=b).mean()
    d["macd"]= d["ma_fast"]- d["ma_slow"]
    d["signal"]=d["macd"].ewm(span=c, min_periods=c).mean()
    return d["signal"]

appl = yf.download("GME", start=start, end=end)
macd_line=MACD(df=appl, a=12, b=26, c=9)
mac_line=KID(df=appl, a=12, b=26, c=9)

did=mac_line-macd_line
did.plot(subplots=True,title="bullish/bearish line", grid=True)
print(mac_line)
print(macd_line)
'''
'''
print(daily_return.rolling(window=10).mean()) this gives value over 10 day period
print(daily_return.rolling(window=10).sum())
print(daily_return.rolling(window=10).std())
print(daily_return.rolling(window=10).max())
'''
'''
print(daily_return.rolling(window=10).mean())
'''
'''
cl_price.plot(subplots=True, layout=(2,2),title="Stock Price Evoluition", grid=True)
'''
'''
fig, ax=plt.subplots()
ax.set(title="Mean Daily Return of Stock", xlabel="Stocks", ylabel="Mean Return" )
plt.bar(x=daily_return.columns, height=daily_return.mean(), color=["Red", "Green", "Blue", "Yellow"])
'''

'''
x=int(input("Enter days since today:"))
print((cl_price["AAPL"].iloc[-x])/(cl_price["AAPL"].iloc[-1]))
'''
"""
stock_list = ["FTNT", "AMZN", "TSLA", "AAPL", "MSFT", "NVDA"]
def CAGR(DF):
    df=DF.copy()
    df=df.copy()
    df_return = df["Close"].pct_change()
    cume_return = (1 + df_return).cumprod()
    n=len(df)/252
    CAGR=(cume_return.iloc[-1])**(1/n)-1
    return CAGR
FTNT=yf.download(stock_list,start,end)
heel=(CAGR(FTNT))
sorted_heel = heel.sort_values()
print(sorted_heel)

sorted_heel.plot(kind='bar', x='Category', y='Values', rot=0)

plt.title("Bar Chart via Pandas")
plt.show()
"""
kids=yf.download("FTNT",start,end)
def vol(DF):
    df=DF.copy()
    df["return"]=df["Close"].pct_change()
    volume=df["return"].std()*np.sqrt(252)
    return vol
print(vol(kids))



