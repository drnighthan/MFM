# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 15:47:40 2018

@author: Hanbrendan
"""
import pandas as pd
from sklearn import preprocessing
import scipy
import os 
"""因子的预处理，这里主要是对因子的标准化
    其中df为输入的csv路径或者DataFrame
    time为时间列在df中的名字
    stock为股票代码列在df中的名字
"""
def processing(df,time,stock,factorlist,winsor=False,madwin=True):
    if type(df)  == pd.DataFrame:
        df[str(time)] = pd.to_datetime(df[str(time)])
    elif type(df) == str:
        df = pd.read_csv(df,parse_dates=[str(time)])
        del df['Unnamed: 0']
    def mad(df2,n):
        xm = df2.median(axis=0)
        Dmad = (abs(df2 - xm)).median(axis=0)
        upper = xm + n*Dmad
        lower = xm - n*Dmad
        df3 = pd.DataFrame()
        for i in list(df2.columns):
            temp = df2[[i]]
            temp = temp.where(temp<=upper[i],upper[i])
            temp = temp.where(temp>=lower[i],lower[i])
            df3 = pd.concat([df3,temp],axis=1)
        return df3
    def stand(df2,factorlist):
        stocklist = list(df2[str(stock)])
        res = df2[factorlist]
        if winsor:
            res = pd.DataFrame(scipy.stats.mstats.winsorize(res,axis=1))
        if madwin:
            res = pd.DataFrame(mad(res,6))
        res = pd.DataFrame(preprocessing.scale(res))
        res.columns = factorlist
        res['Stkcd'] = stocklist
        return res 
    factor_process = df.groupby([str(time)]).apply(stand,factorlist).reset_index()
    try:
        del factor_process['level_1']
    except:
        pass
    return factor_process


if __name__ == '__main__' :
    test = processing('C:/Users/Han/Downloads/R code NCFR/BarraStep/datasample/barrafactor.csv','Trddt','Stkcd'
               ,['beta', 'BP', 'earningsfactor','leveragefactor', 'RSTR', 'Non-Linear Size', 'residualvolatilityfactor','Size'])
    test.to_csv(os.path.join(os.path.abspath('.'),'Data','Factor_Preprocessing.csv'))
#    test = processing('C:/Users/Han/Downloads/GitHub/MFM/Data/ValueFactor.csv','Trddt','Stkcd'
#               ,['Netcashflow', 'Operatingcashflow', 'EP','EPcut', 'Sales', 'FCF', 'NetAsset','EV2ToEBITDA'])
#    test.to_csv(os.path.join(os.path.abspath('.'),'Data','Value_Factor_Preprocessing.csv'))

    
    
    