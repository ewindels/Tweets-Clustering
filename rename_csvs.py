import pandas as pd
import os

for data_file in os.listdir('data/')[1:]: #beware, [1:] is mac offset
    a = pd.read_csv('data/' + data_file)
    a.columns = ['date' if ch == 'data' else ch for ch in list(a.columns)]
    a.to_csv('data/' + data_file)
    