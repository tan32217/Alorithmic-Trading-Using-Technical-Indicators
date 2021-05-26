import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import copy
import statsmodels.api as sm
import matplotlib.pyplot as plt

def MACD(DF,a,b,c):
    df = DF.copy()
    df["MA_Fast"]=df["Adj Close"].ewm(span=a,min_periods=a).mean()
    df["MA_Slow"]=df["Adj Close"].ewm(span=b,min_periods=b).mean()
    df["MACD"]=df["MA_Fast"]-df["MA_Slow"]
    df["Signal"]=df["MACD"].ewm(span=c,min_periods=c).mean()
    df.dropna(inplace=True)
    return (df["MACD"],df["Signal"])

def OBV(DF):
    df = DF.copy()
    df['daily_ret'] = df['Adj Close'].pct_change()
    df['direction'] = np.where(df['daily_ret']>=0,1,-1)
    df['direction'][0] = 0
    df['vol_adj'] = df['Volume'] * df['direction']
    df['obv'] = df['vol_adj'].cumsum()
    return df['obv']


def ATR(DF,n):
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2

def slope(ser,n):
    slopes = [i*0 for i in range(n-1)]
    for i in range(n,len(ser)+1):
        y = ser[i-n:i]
        x = np.array(range(n))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled,x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


def CAGR(DF):
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR



tickers = ["RELIANCE.NS","ASIANPAINT.NS","TCS.NS","ICICIBANK.NS","EICHERMOT.NS"]


ohlc_intraday = {}           

for i in range(len(tickers)):
    ohlc_intraday[tickers[i]] = yf.download(tickers[i], interval = "5m", start = "2021-03-01", end = "2021-03-20")
    ohlc_intraday[tickers[i]].drop(["Close"],axis = 1, inplace = True)
    ohlc_intraday[tickers[i]].columns = ["Open","High","Low","Adj Close","Volume"]     



ohlcmerged = {}
df = copy.deepcopy(ohlc_intraday)
tickers_signal = {}
tickers_ret = {}
for ticker in tickers:
    print("merging for ",ticker)
    ohlcmerged[ticker] = df[ticker]
    ohlcmerged[ticker]["Date"] = ohlcmerged[ticker].index
    ohlcmerged[ticker]["macd"]= MACD(ohlcmerged[ticker],12,26,9)[0]
    ohlcmerged[ticker]["macd_sig"]= MACD(ohlcmerged[ticker],12,26,9)[1]
    ohlcmerged[ticker]["macd_slope"] = slope(ohlcmerged[ticker]["macd"],5)
    ohlcmerged[ticker]["macd_sig_slope"] = slope(ohlcmerged[ticker]["macd_sig"],5)
    ohlcmerged[ticker]["obv"]= OBV(ohlcmerged[ticker])
    ohlcmerged[ticker]["obv_slope"]= slope(ohlcmerged[ticker]["obv"],5)
    tickers_signal[ticker] = ""
    tickers_ret[ticker] = []
 


for ticker in tickers:
    print("calculating daily returns for ",ticker)
    for i in range(len(ohlc_intraday[ticker])):
        if tickers_signal[ticker] == "":
            tickers_ret[ticker].append(0)
            if i > 0:
                if ohlcmerged[ticker]["obv_slope"][i]>30 and ohlcmerged[ticker]["macd"][i]>ohlcmerged[ticker]["macd_sig"][i] and ohlcmerged[ticker]["macd_slope"][i]>ohlcmerged[ticker]["macd_sig_slope"][i]:
                    tickers_signal[ticker] = "Buy"
                
        
        elif tickers_signal[ticker] == "Buy":
            tickers_ret[ticker].append((ohlcmerged[ticker]["Adj Close"][i]/ohlcmerged[ticker]["Adj Close"][i-1])-1)
            if i > 0:
                if ohlcmerged[ticker]["macd"][i]<ohlcmerged[ticker]["macd_sig"][i] and ohlcmerged[ticker]["macd_slope"][i]<ohlcmerged[ticker]["macd_sig_slope"][i]:
                    tickers_signal[ticker] = ""
                
        
    ohlcmerged[ticker]["ret"] = np.array(tickers_ret[ticker])


strategy_df = pd.DataFrame()
for ticker in tickers:
    strategy_df[ticker] = ohlcmerged[ticker]["ret"]
strategy_df["ret"] = strategy_df.mean(axis=1)
CAGR(strategy_df)
x = (1+strategy_df["ret"]).cumprod().plot()
fig = plt.figure()
ax1 = fig.add_axes()
ax1.plot(x)
ax1.set_xlabel('Date')
ax1.set_ylabel("Returns")


cagr = {}
for ticker in tickers:
    print("calculating KPIs for ",ticker)      
    cagr[ticker] =  CAGR(ohlcmerged[ticker])
KPI_df = pd.DataFrame([cagr],index=["Return"])      
KPI_df.T