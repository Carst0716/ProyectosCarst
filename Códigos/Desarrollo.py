import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm

#FASE 1: Obtención de los Datos

Activo="COP=X"
FechaIni="2019-01-01"
FechaFin="2022-02-27"

Data=yf.download(Activo,FechaIni,FechaFin)

#FASE 2: Refinación de los datos

print(Data.head())
print(Data.info())
print(Data.describe())

print(Data[Data.duplicated(keep='first')])

"""
corr = Data.set_index('Open').corr()
sm.graphics.plot_corr(corr, xnames=list(corr.columns))
plt.show()
"""