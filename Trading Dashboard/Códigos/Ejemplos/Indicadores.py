import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf


plt.style.use('bmh')

aapl=yf.download('COP=X','2019-1-1','2021-05-03')



#Medias moviles

aapl['SMA']=ta.SMA(aapl['Close'].values,21)
aapl['EMA']=ta.EMA(aapl['Close'].values,55)
#Bandas de bollinger

aapl['upper_band'], aapl['middle_band'], aapl['lower_band']=ta.BBANDS(aapl['Close'],timeperiod=20)

aapl[['Close','SMA','EMA','upper_band','middle_band','lower_band']].plot(figsize=(15,15))
plt.show()

#RSI
aapl['RSI']=ta.RSI(aapl.Close,14)
aapl['RSI'].plot(figsize=(15,15))
#plt.show()
