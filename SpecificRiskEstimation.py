# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 11:24:15 2018

@author: Han
"""
import pandas as pd
import os
import numpy as np

def SpecificRisk(df,factorret,time,stock,window,indcode = '2012',method = 'EWMA',halfday=60):
    if type(df) == str:
        df = pd.read_csv(df,parse_dates=[str(time)])
        del df['Unnamed: 0']
    elif type(df)  == pd.DataFrame:
        df[str(time)] = pd.to_datetime(df[str(time)])
    if type(factorret) == str:
        factorret = pd.read_csv(factorret,parse_dates=[str(time)])
        del factorret['Unnamed: 0']
    elif type(factorret)  == pd.DataFrame:
        factorret[str(time)] = pd.to_datetime(factorret[str(time)])        
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
    df = pd.merge(df,industry,on=[str(stock)])
    factorlist = list(factorret.columns)
    try:
        factorlist.remove(str(time))
        factorlist.remove('const')
        factorlist.remove('num')
    except:
        pass
    data = pd.merge(df,factorret,on=[str(time)])
    templist = [data[i+'_x']*data[i+'_y'] for i in factorlist]
    data['fitted'] = np.sum(templist,axis=0)
    data['fitted'] = data['fitted'] + data['const']
    retdatapath = os.path.join(os.path.abspath('.'),'InPutData','monthly_return_2005-2017')
    retdata = pd.DataFrame()
    for i in os.listdir(retdatapath):
        temp = os.path.join(retdatapath,i,'TRD_Mnth.csv')
        temp = pd.read_csv(temp,parse_dates = ['Trdmnt'])
        retdata = pd.concat([retdata,temp],axis=0)
    retdata = retdata[retdata['Markettype']!= 2]
    retdata = retdata[retdata['Markettype']!= 8]
    retdata = retdata[['Stkcd','Trdmnt','Mretnd']]
    retdata.columns = [str(stock),str(time),'Mretnd']
    retdata = retdata.drop_duplicates(['Stkcd','Trddt'])
    data = pd.merge(data,retdata,on=[str(time),str(stock)])
    data['residual'] = data['Mretnd'] - data['fitted']
    data = data[[str(stock),str(time),'residual']]
    def weightcreate(x,num):
        weight = (0.5)**(x)
        weightlist = [(weight**(num-i))**2 for i in range(num)]
        return weightlist
    ewmaweight = weightcreate(1/halfday,window)
    def SpecificVarCal(df,window,method):
        df = df.sort_values(str(time))
        if method == 'EWMA':
            df['SpecificVar'] = df['residual'].rolling(window).apply(lambda x : np.var(x*ewmaweight))
        else:
            df['SpecificVar'] = df['residual'].rolling(window).var()
        del df[str(stock)]
        return df
    data = data.groupby(str(stock)).apply(SpecificVarCal,window,method).reset_index()
    data = data.dropna()
    del data['level_1']
    data = data[[str(stock),str(time),'SpecificVar']]
    return(data)

if __name__ == '__main__' :
    df = os.path.join(os.path.abspath('.'),'Data','Factor_Preprocessing.csv')
    factorret = os.path.join(os.path.abspath('.'),'Data','Factor_Return_Regression.csv')
    test = SpecificRisk(df,factorret,'Trddt','Stkcd',12).dropna()
    test.to_csv(os.path.join(os.path.abspath('.'),'Data','SpecificRisk.csv'))
    
    