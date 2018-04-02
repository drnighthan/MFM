# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 14:29:56 2018

@author: Hanbrendan
"""
import pandas as pd
import statsmodels.api as sm 
import os
import numpy as np
import scipy
"""因子有效性检验"""
def Factorrettest(factordataset,stock,time,factor,retname,indcode = '2012'):
    if type(factordataset) == str:
        df = pd.read_csv(factordataset,parse_dates=[str(time)])
        del df['Unnamed: 0']
    elif type(factordataset)  == pd.DataFrame:
        df = factordataset
        df[str(time)] = pd.to_datetime(df[str(time)])
    df = df[[str(stock),str(time),str(factor)]]
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
#    retdatapath = os.path.join(os.path.abspath('.'),'InPutData','monthly_return_2005-2017')
#    retdata = pd.DataFrame()
#    for i in os.listdir(retdatapath):
#        temp = os.path.join(retdatapath,i,'TRD_Mnth.csv')
#        temp = pd.read_csv(temp,parse_dates = ['Trdmnt'])
#        retdata = pd.concat([retdata,temp],axis=0)
    retdatapath = os.path.join(os.path.abspath('.'),'InPutData','monthly_return_2005-2018')
    retdata = pd.DataFrame()
    temp = os.path.join(retdatapath,'TRD_Mnth.txt')
    retdata = pd.read_table(temp,parse_dates = ['Trdmnt'])
    retdata = retdata[retdata['Markettype']!= 2]
    retdata = retdata[retdata['Markettype']!= 8]
    retdata = retdata[['Stkcd','Trdmnt','Mretnd']]
    retdata.columns = [str(stock),str(time),'Mretnd']
    data = pd.merge(df,retdata,on=[str(stock),str(time)])
    data = pd.merge(data,industry,on=[str(stock)])
    ylist = ['Mretnd']
    lastindcode = list(data.columns)[-1]
    xlist = [i for i in list(data.columns) if i not in [lastindcode,str(stock),str(time),'Mretnd']]
    data = data.dropna()
    def Ols(df):
        temp = sm.regression.linear_model.OLS(df[ylist],df[xlist]).fit()
        res = pd.DataFrame(temp.params).T
        res = res[[str(factor)]]
        tval = pd.DataFrame(temp.tvalues).T
        tval = res[[str(factor)]]
        tval.columns = [str(factor)+'_t']
        res = pd.concat([res,tval],axis=1)
        res['num'] = len(df)
        return res
    regresult =data.groupby([str(time)]).apply(Ols).reset_index()
    del regresult['level_1']
    regresult['abs'+str(factor)+'_t'] = np.abs(regresult[str(factor)+'_t'])
    temp = scipy.stats.ttest_1samp(regresult['abs'+str(factor)+'_t'], 0)
    vaildresult = pd.DataFrame(np.array(temp)).T
    vaildresult.columns = ['Abs_t_statistic','Abs_t_pvalue']
    vaildresult['Factorname'] = str(factor)
    vaildresult['t>2_percet'] = len(regresult[(regresult['abs'+str(factor)+'_t']>2) == True])/len(regresult)
    vaildresult[str(factor)+'_ret_pvalue'] = (scipy.stats.ttest_1samp(regresult[str(factor)],0).pvalue)
    if np.array((vaildresult['Abs_t_pvalue']<0.01)&(vaildresult['t>2_percet']<0.1)&(vaildresult[str(factor)+'_ret_pvalue']<0.01)):
        vaildresult['type'] = 'Return'
    elif np.array((vaildresult['Abs_t_pvalue']<0.01)&(vaildresult['t>2_percet']<0.1)&(vaildresult[str(factor)+'_ret_pvalue']>=0.01)):
        vaildresult['type'] = 'Risk'
    else:
        vaildresult['type'] = 'NotVaild'
    resultdict = dict()
    resultdict['factor_return'] = regresult
    resultdict['vaild_test'] = vaildresult
    return resultdict

if __name__ == '__main__' :
    factordataset = os.path.join(os.path.abspath('.'),'Data','Factor_preprocessing.csv')
    resultall = dict()
    factorlist = ['beta', 'BP', 'earningsfactor', 'leveragefactor','RSTR', 'Non-Linear Size', 'residualvolatilityfactor', 'Size']
    for i in factorlist:
        resultall[i] = Factorrettest(factordataset,'Stkcd','Trddt',i,'Mretnd',indcode = '2012')
#    factordataset = os.path.join(os.path.abspath('.'),'Data','Value_Factor_Preprocessing.csv')
#    resultall = dict()
#    factorlist = ['Netcashflow', 'Operatingcashflow', 'EP','EPcut', 'Sales', 'FCF', 'NetAsset','EV2ToEBITDA']
#    for i in factorlist:
#        resultall[i] = Factorrettest(factordataset,'Stkcd','Trddt',i,'Mretnd',indcode = '2012')
