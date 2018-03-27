# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 16:13:38 2018

@author: Han
"""
import pandas as pd
import os

"""因子ewma方差计算"""
def FactorCovariance(df,time,window,*factorlist,method='EWMA',halfday=60):
    if type(df) == str:
        df = pd.read_csv(df,parse_dates=[str(time)])
        del df['Unnamed: 0']
    elif type(df)  == pd.DataFrame:
        df[str(time)] = pd.to_datetime(df[str(time)])
    df = df.sort_values(str(time))
    df = df.set_index(str(time))
    del df['num'],df['const']
    if len(factorlist) != 0:
        df = df[factorlist]
    if method == 'EWMA':
        def weightcreate(x,num):
            weight = (0.5)**(x)
            weightlist = [(weight**(num-i))**2 for i in range(num)]
            return weightlist
        ewmaweight = weightcreate(1/halfday,window)
        def multi(df):
            return df.mul(ewmaweight,axis=0)
        result = pd.DataFrame()
        for i in range(len(df)-window+1):
            temp = df.iloc[i:(i+window),:]
            temp = multi(temp)
            date = temp.index[-1]
            tempcov = temp.cov()
            tempcov['Trddt'] = date
            result = pd.concat([result,tempcov])
    else:
        result = df.rolling(window).cov().dropna()
        result = result.reset_index()
    return result

if __name__ == '__main__' :
    df = os.path.join(os.path.abspath('.'),'Data','Factor_Return_Regression.csv')
    test = FactorCovariance(df,'Trddt',12)
    #,['beta', 'BP', 'earningsfactor', 'leveragefactor', 'RSTR','Non-Linear Size', 'residualvolatilityfactor', 'Size']
    test.to_csv(os.path.join(os.path.abspath('.'),'Data','Factor_Return_Covariance.csv'))