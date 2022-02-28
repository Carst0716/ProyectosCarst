import talib as ta
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np


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


#FASE 3: Análisis de datos y calculo de indicadores

#Media móvil para 30 muestras
Data['SMA 30']=ta.SMA(Data['Close'].values,30)

#Media móvil para 100 muestras
Data['EMA 100']=ta.EMA(Data['Close'].values,100)

#Bandas de bollinger para un periodo de 30 muestras
Data['upper_band'], Data['middle_band'], Data['lower_band']=ta.BBANDS(Data['Close'],timeperiod=20)

#ADX: Average Directional Movement Index
Data['ADX']=ta.ADX(Data['High'],Data['Low'],Data['Close'],timeperiod=14)

#RSI: Relative strength index
Data['RSI']=ta.RSI(Data['Close'],14)

#FASE 4: 