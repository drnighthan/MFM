# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 14:29:56 2018

@author: Hanbrendan
"""
import pandas as pd
import statsmodels.api as sm 
import os 
import numpy as np
"""因子收益率计算"""
def FactorReturnEstimation(df,time,stock,factorlist,method='WLS',indcode = '2012'):
    if type(df) == str:
        df = pd.read_csv(df,parse_dates=[str(time)])
        del df['Unnamed: 0']
    elif type(df)  == pd.DataFrame:
        df[str(time)] = pd.to_datetime(df[str(time)])
    industrypath = os.path.join(os.path.abspath('.'),'InPutData','company_info_1990_2017','TRD_Co.csv')
    industry = pd.read_csv(industrypath,encoding = 'gbk')
    if indcode == '2001':
        industryname = 'Nindcd'
    elif indcode == '2012':
        industryname = 'Nnindcd'
    elif indcode == 'LargeIndustry':
        industryname = 'Indcd'
    temp = pd.get_dummies(industry[industryname])
    industry = pd.concat([industry[['Stkcd']],temp],axis=1)
    industry = industry.rename({'Stkcd':str(stock)})
    retdatapath = os.path.join(os.path.abspath('.'),'InPutData','monthly_return_2005-2017')
    retdata = pd.DataFrame()
    for i in os.listdir(retdatapath):
        temp = os.path.join(retdatapath,i,'TRD_Mnth.csv')
        temp = pd.read_csv(temp,parse_dates = ['Trdmnt'])
        retdata = pd.concat([retdata,temp],axis=0)
    retdata = retdata[retdata['Markettype']!= 2]
    retdata = retdata[retdata['Markettype']!= 8]
    '''选择了总市值作为权重'''
    if method == 'WLS':
        retdata = retdata[['Stkcd','Trdmnt','Mretnd','Msmvttl']]
        sumvalue = retdata.groupby('Trdmnt').apply(lambda x : np.sum(x['Msmvttl'])).reset_index()
        retdata = pd.merge(retdata,sumvalue,on=['Trdmnt'])
        retdata['ValueWeight'] = retdata['Msmvttl']/retdata[0]
        retdata = retdata[['Stkcd','Trdmnt','Mretnd','ValueWeight']]
        retdata.columns = [str(stock),str(time),'Mretnd','ValueWeight']
    else:
        retdata = retdata[['Stkcd','Trdmnt','Mretnd']]
        retdata.columns = [str(stock),str(time),'Mretnd']
    data = pd.merge(df,retdata,on=[str(stock),str(time)])
    data = pd.merge(data,industry,on=[str(stock)])
    ylist = ['Mretnd']
    lastindcode = []
    if method == 'WLS':
        xlist = [i for i in list(data.columns) if i not in [lastindcode,str(stock),str(time),'Mretnd','ValueWeight']]
    else:
        xlist = [i for i in list(data.columns) if i not in [lastindcode,str(stock),str(time),'Mretnd']]
    data = data.dropna()
    def Ols(df):
        temp = sm.regression.linear_model.OLS(df[ylist],sm.add_constant(df[xlist])).fit()
        res = pd.DataFrame(temp.params).T
        res['num'] = len(df)
        return res       
    def Wls(df):
        temp = sm.regression.linear_model.WLS(df[ylist],sm.add_constant(df[xlist]),weights=df['ValueWeight']).fit()
        res = pd.DataFrame(temp.params).T
        res['num'] = len(df)
        return res
    if method == 'WLS':
        regresult =data.groupby([str(time)]).apply(Wls).reset_index()
    else:
        regresult =data.groupby([str(time)]).apply(Ols).reset_index()
    del regresult['level_1']
    return regresult

if __name__ == '__main__' :
    df = os.path.join(os.path.abspath('.'),'Data','Factor_Preprocessing.csv')
    test = FactorReturnEstimation(df,'Trddt','Stkcd',['beta', 'BP', 'earningsfactor', 'leveragefactor', 'RSTR','Non-Linear Size', 'residualvolatilityfactor', 'Size'])
    test.to_csv(os.path.join(os.path.abspath('.'),'Data','Factor_Return_Regression.csv'))