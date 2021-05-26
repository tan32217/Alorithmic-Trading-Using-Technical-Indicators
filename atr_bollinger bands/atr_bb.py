import yfinance as yf
import datetime as dt
tan
curr = ["JPYUSD=X","AUDUSD=X","INRUSD=X","EURUSD=X"]
stk = ["MSFT","GOOG","AAPL","FB"]


#ohlcv = yf.download(ticker, period = '1d', interval = '1m')


def ATR(DF,n):
    "function to calculate True Range and Average True Range"
    df = DF.copy()
    df['H-L']=abs(df['High']-df['Low'])
    df['H-PC']=abs(df['High']-df['Adj Close'].shift(1))
    df['L-PC']=abs(df['Low']-df['Adj Close'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1,skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df2 = df.drop(['H-L','H-PC','L-PC'],axis=1)
    return df2




def BollBnd(DF,n):
    "function to calculate Bollinger Band"
    df = DF.copy()
    df["MA"] = df['Adj Close'].rolling(n).mean()
    df["BB_up"] = df["MA"] + 2*df['Adj Close'].rolling(n).std(ddof=0) 
    df["BB_dn"] = df["MA"] - 2*df['Adj Close'].rolling(n).std(ddof=0) 
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df


for ticker in curr:
    ohlcv = yf.download(ticker, period = '1d', interval = '1m')
    BollBnd(ohlcv,20).iloc[-100:,[-4,-3,-2]].plot(title="Bollinger Band"+ "  " + ticker )
    ATR(ohlcv,20).iloc[-100:,[-1]].plot(title="average true range")


for ticker in stk:
    ohlcv = yf.download(ticker, period = '1d', interval = '1m')
    BollBnd(ohlcv,20).iloc[-100:,[-4,-3,-2]].plot(title="Bollinger Band"+ "  " + ticker )
    ATR(ohlcv,20).iloc[-100:,[-1]].plot(title="average true range"+" "+ ticker)