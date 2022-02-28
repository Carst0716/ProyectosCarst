import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf

Activo="COP=X"
FechaIni="2019-1-1"
FechaFin="2021-05-03"

aapl=yf.download(Activo,FechaIni,FechaFin)