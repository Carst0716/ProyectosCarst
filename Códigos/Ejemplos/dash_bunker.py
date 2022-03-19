from tkinter.tix import Select
import pandas as pd
import numpy as np

SelectTen=None

print(len(SelectTen))

if len(SelectTen)==0:
    
    if np.any(SelectTen):
        print("Si")
    else:
        print("No")
else:

    if pd.isnull(SelectTen[0]):
        print("Si")
    else:
        print("No")