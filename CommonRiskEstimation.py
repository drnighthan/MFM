# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 16:13:38 2018

@author: Han
"""
import pandas as pd
import os 
import numpy as np

"""因子收益率计算"""
def CommonRisk(df,cov,time,stock,method='WLS',indcode = '2012'):
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
    data = pd.merge(df,industry,on=[str(stock)])
    if type(cov) == str:
        cov= pd.read_csv(cov,parse_dates=[str(time)])
        del cov['Unnamed: 0']
    elif type(cov)  == pd.DataFrame:
        cov[str(time)] = pd.to_datetime(cov[str(time)])
    datelist = list(cov[str(time)].drop_duplicates())
    covresultall = dict()
    for i in datelist:
        factortemp = data[data[str(time)]==i]
        del factortemp[str(time)]
        covtemp = cov[cov[str(time)]==i]
        del covtemp[str(time)]
        stocklist = list(factortemp[str(stock)])
        del factortemp[str(stock)]
        factortemp = factortemp[list(covtemp.columns)]
        covresult = pd.DataFrame(np.dot(np.dot(factortemp,covtemp),factortemp.T))
        covresult.columns = stocklist
        covresult[str(stock)] = stocklist
        covresult = covresult.set_index(str(stock))
        covresult.to_csv(os.path.join(os.path.abspath('.'),'Data','CovarianceEstimation',str(i.year)+'-'+str(i.month)+'-1.csv'))
        covresultall[i] = covresult
    return covresultall

if __name__ == '__main__' :
    df = os.path.join(os.path.abspath('.'),'Data','Factor_Preprocessing.csv')
    cov = os.path.join(os.path.abspath('.'),'Data','Factor_Return_Covariance.csv')
    test = CommonRisk(df,cov,'Trddt','Stkcd')
    