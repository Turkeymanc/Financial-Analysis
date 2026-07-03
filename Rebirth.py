
import yfinance as yf
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import requests



"Stock Release"
x=input("Enter the ticker symbol of the stock:")
print(x)
y=input("Is this the correct symbol and is it in all caps? yes or no lowercase:")
while y=="no":
    x=input("Enter the ticker symbol of the stock:")
    print(x)
    y=input("Is this the correct symbol and is it in all caps? yes or no lowercase:")


g=int(input("What do you want the date length to be:"))
date=g

end=dt.datetime.today()
start=dt.datetime.today()-dt.timedelta(date)
stock_choice = yf.download(x, start=start, end=end)
if isinstance(stock_choice.columns, pd.MultiIndex):
    stock_choice.columns = stock_choice.columns.droplevel(1)
a=input("What do you wanna do with the stock? Chose these options and type exactly as shown: MACD, Graph of Lows, Graph of Highs, RSI, Bollinger Bands, Moving Average, and Stock Graph:")

def MACD(df,a=12, b=26, c=9):
    d=df.copy()
    d["ma_fast"]=d["Close"].ewm(span=a, min_periods=a).mean()
    d["ma_slow"]=d["Close"].ewm(span=b, min_periods=b).mean()
    d["macd"]= d["ma_fast"]- d["ma_slow"]
    d["signal"]=d["macd"].ewm(span=c, min_periods=c).mean()
    return d["macd"]
def Signal(df,a=12, b=26, c=9):
    d=df.copy()
    d["ma_fast"]=d["Close"].ewm(span=a, min_periods=a).mean()
    d["ma_slow"]=d["Close"].ewm(span=b, min_periods=b).mean()
    d["macd"]= d["ma_fast"]- d["ma_slow"]
    d["signal"]=d["macd"].ewm(span=c, min_periods=c).mean()
    return d["signal"]
def graphoflows():
    lows=stock_choice["Low"]
    lows.plot(kind="line", title="Low Prices")
    plt.show()
def graphhighs():
    high=stock_choice["High"]
    high.plot(kind="line", title="High Prices")
    plt.show()
def graph():
    regular=stock_choice["Close"]
    regular.plot(kind="line", title=x+"Stock Price")
    plt.show()
    return regular
    
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
    return df[["rsi","Upper Band", "Lower Band"]]
def Boll_Band(DF,n=14):
    df=DF.copy()
    df["MB"]=df["Close"].rolling(n).mean()
    df["UB"]=df["MB"]+2*df["Close"].rolling(n).std(ddof=0)
    df["LB"]=df["MB"]-2*df["Close"].rolling(n).std(ddof=0)
    return df["MB"]
def Boll_Ban(DF,n=14):
    df=DF.copy()
    df["MB"]=df["Close"].rolling(n).mean()
    df["UB"]=df["MB"]+2*df["Close"].rolling(n).std(ddof=0)
    df["LB"]=df["MB"]-2*df["Close"].rolling(n).std(ddof=0)
    return df["UB"]
def Boll_Bd(DF,n=14):
    df=DF.copy()
    df["MB"]=df["Close"].rolling(n).mean()
    df["UB"]=df["MB"]+2*df["Close"].rolling(n).std(ddof=0)
    df["LB"]=df["MB"]-2*df["Close"].rolling(n).std(ddof=0)
    return df["LB"]
def moving_average(DF, n=14):
    df=DF.copy() 
    df["M"]=df["Close"].rolling(n).mean()
    return df["M"]
if (a=="MACD"):
    mad=(MACD(stock_choice,a=12, b=26, c=9))-Signal(stock_choice,a=12, b=26, c=9)
    mad.plot(kind="line", title="MACD Line")
    plt.show()
if (a=="Graph of Lows"): 
    graphoflows()
if (a=="Graph of Highs"):
    graphhighs()
if (a=="RSI"):
    me=RSI(stock_choice, n=14)
    me.plot(title="RSI", color="black", kind="line")
    plt.show()
if (a=="Bollinger Bands"):
    epstein=pd.DataFrame()
    epstein["one"]=Boll_Band(stock_choice,n=14)
    epstein["two"]=Boll_Ban(stock_choice,n=14)
    epstein["three"]=Boll_Bd(stock_choice,n=14)
    epstein.plot(kind="line", title="Bollinger Bands")
    plt.show()
if (a=="Stock Graph"):
    graph()
if (a=="Moving Average"):
    nice=pd.DataFrame()
    graph()
    pe=moving_average(stock_choice,n=14)
    nice["one"]=pe
    nice["two"]=graph()
    nice.plot(title="Moving Average", kind="line")
    plt.show()




