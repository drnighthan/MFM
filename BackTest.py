# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 13:19:53 2018

@author: Han
"""
import numpy as np
import pandas as pd
import os

def Backtest(portfolio,time,stock,percentage,lag=1):
    if type(portfolio) == str:
        portfolio = pd.read_csv(portfolio,parse_dates=[str(time)])
        del portfolio['Unnamed: 0']
    elif type(portfolio) == pd.DataFrame:
        portfolio[str(time)] = pd.to_datetime(portfolio[str(time)])
    portfolio[str(time)] = portfolio[str(time)] + pd.DateOffset(months=lag)
    retdatapath = os.path.join(os.path.abspath('.'),'InPutData','monthly_return_2005-2018','TRD_Mnth.txt')
    retdata = pd.read_table(retdatapath,parse_dates = ['Trdmnt'])
    retdata = retdata[retdata['Markettype']!= 2]
    retdata = retdata[retdata['Markettype']!= 8]
    retdata = retdata[['Stkcd','Trdmnt','Mretnd']]
    retdata.columns = [str(stock),str(time),'Mretnd']
    retdata = retdata.dropna()
    data = pd.merge(portfolio,retdata,on=[str(stock),str(time)])
    data['ret+1'] = data[str(percentage)] * data['Mretnd']
    data = data.groupby(str(time)).apply(lambda x : np.sum(x['ret+1']))
    data += 1
    data = data.cumprod()
    return data
    
if __name__ == '__main__' :
    testpath = os.path.join(os.path.abspath('.'),'Data','result.csv')
    test = Backtest(testpath,'Trddt','Stkcd','optim',lag=1)
