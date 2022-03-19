from cProfile import label
from turtle import color
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyparsing import alphas
import yfinance as yf

#datos=pd.read_csv('BTC-USD.csv')
datos=yf.download('BTC-USD','2016-1-1','2021-12-31')


#USO DE LA MEDIA MOVIL SIMPLE PARA 30 Y 100 MUESTRAS

#print(datos.head())
#print(type(datos))

"""
plt.figure(figsize=(10,5))
plt.plot(datos['Close'],label="BTC-USD")
plt.title('BTC-USD 2016 - 2022')
plt.xlabel('Días [1 Ene 2016 - 8 feb 2022]')
plt.ylabel('Precio cierre en USD')

"""

MVS30=pd.DataFrame()
MVS30['Close']=datos['Close'].rolling(window=30).mean()

MVS100=pd.DataFrame()
MVS100['Close']=datos['Close'].rolling(window=100).mean()

#print(MVS30[0:30])  #MVS30[MVS30.index==30]
#print(MVS100[0:100])  #MVS30[MVS30.index==100]

"""
plt.plot(MVS30["Close"],label="MSV 30")
plt.plot(MVS100["Close"],label="MSV 100")

plt.legend(loc="upper left")
plt.show()
"""

data=pd.DataFrame()
data["BTC-USD"]=datos['Close']
data["MVS30"]=MVS30['Close']
data["MVS100"]=MVS100['Close']

#print(data)

def signal(data):
    compra=[]
    venta=[]
    condicion=0

    for dia in range(len(data)):
        
        if data["MVS30"][dia]>data["MVS100"][dia]:
            if condicion!=1:
                compra.append(data['BTC-USD'][dia])
                venta.append(np.nan)
                condicion=1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        elif data["MVS30"][dia]<data["MVS100"][dia]:
            if condicion!=-1:
                venta.append(data['BTC-USD'][dia])
                compra.append(np.nan)
                condicion=-1
            else:
                compra.append(np.nan)
                venta.append(np.nan)
        else:
             compra.append(np.nan)
             venta.append(np.nan)

    return (compra,venta)



Sen=signal(data)


data["Compra"]=Sen[0]
data["Venta"]=Sen[1]

#print(data)

plt.style.use('bmh')

plt.figure(figsize=(10,5))
plt.scatter(data.index,data['Compra'],label="Precio de compra",marker='^',color='green')
plt.scatter(data.index,data['Venta'],label="Precio de venta",marker='^',color='red')
plt.legend(loc="upper left")
plt.show()
