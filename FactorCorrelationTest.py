# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 13:36:31 2018

@author: Han
"""
import pandas as pd
import numpy as np
import os
'''return model'''
def CorrelationTest(factordataset,factorlist,stock,time,M):
    if type(factordataset) == str:
        df = pd.read_csv(factordataset,parse_dates=[str(time)])
        del df['Unnamed: 0']
    elif type(factordataset)  == pd.DataFrame:
        df = factordataset
        df[str(time)] = pd.to_datetime(df[str(time)])
    del df[str(stock)]
    def corrcoef(df,factorlist):
        temp = df[factorlist]
        temp = pd.DataFrame(np.corrcoef(temp.T))
        temp.columns = factorlist
        temp.index = factorlist
        return(temp)
    temp = df.groupby(str(time)).apply(lambda x :corrcoef(x,factorlist))
    abstemp = abs(temp)
    abstemp = abstemp.reset_index()
    datelist = list(abstemp[str(time)].drop_duplicates().sort_values())
    corrall = dict()
    for i in range(0,(len(datelist)-M)):
        temp = abstemp[(abstemp[str(time)]>datelist[i])&(abstemp[str(time)]<=datelist[i+M])]
        del temp[str(time)]
        temp3 = temp.groupby('level_1').median()
        namelist = list(temp3.columns)
        temp3.columns = [i + '_median' for i in temp3.columns]
        temp2 = temp.groupby('level_1').mean()
        temp2 = temp2[namelist]
        temp2.columns = [i + '_mean' for i in temp2.columns]
        temp = pd.merge(temp2,temp3,right_index=True,left_index=True)
        temp = temp.loc[namelist].reset_index()
        corrall[datelist[i+M]] = temp
    return corrall

if __name__ == '__main__' :
    factordataset = os.path.join(os.path.abspath('.'),'Data','Factor_preprocessing.csv')
    test = CorrelationTest(factordataset,['beta', 'BP', 'earningsfactor', 'leveragefactor', 'RSTR','Non-Linear Size', 'residualvolatilityfactor', 'Size'],'Stkcd','Trddt',12)
