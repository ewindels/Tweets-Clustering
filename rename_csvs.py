import pandas as pd
import os

for data_file in os.listdir('data/')[1:]: #beware, [1:] is mac offset for DS_store
    a = pd.read_csv('data/' + data_file)
    a.columns = ['date' if ch == 'data' else ch for ch in list(a.columns)]
    a.drop('Unnamed: 0', axis=1, inplace=True)
    a.to_csv('data/' + data_file, index=False)
    