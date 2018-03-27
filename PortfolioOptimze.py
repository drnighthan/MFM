# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 17:06:26 2018

@author: Han
"""

import numpy as np
import pandas as pd
from cvxopt import matrix,solvers
import os

def PortfoiloOptimzer(specificriskall,covlist,time,stock,hedge=False,hedgefactor=None,stockfactor=None,factorlist=None,Purefactor=None):
    if type(specificriskall) == str:
        specificriskall = pd.read_csv(specificriskall,parse_dates=[str(time)])
        del specificriskall['Unnamed: 0']
    elif type(specificriskall) == pd.DataFrame:
        specificriskall[str(time)] = pd.to_datetime(specificriskall[str(time)])
    specificdate = list(specificriskall[str(time)].drop_duplicates())
    result = pd.DataFrame()
    for i in specificdate:
        date = i
        specificrisk = specificriskall[specificriskall[str(time)]==date]
        covname = str(date.year)+'-'+str(date.month)+'-1.csv'
        cov = os.path.join(covlist,covname)
        covtemp = pd.read_csv(cov)
        commonstock = list(set(covtemp[str(stock)])&set(specificrisk[str(stock)]))
        commonstock.sort()
        covtemp = covtemp[covtemp[str(stock)].isin(commonstock)]
        covtemp = covtemp.set_index(str(stock))
        specificrisk = specificrisk[specificrisk[str(stock)].isin(commonstock)] 
        commonstock = [str(i) for i in covtemp.index]
        covtemp = covtemp[commonstock]
        specificriskmat = pd.DataFrame(np.diag(specificrisk['SpecificVar']))
        specificriskmat = specificriskmat.set_index(specificrisk[str(stock)])
        specificriskmat.columns = list(specificriskmat.index)
        mat = np.matrix(covtemp) + np.matrix(specificriskmat)
        '''二次项'''
        P = 2*matrix(mat)
        '''一次项'''
        q = matrix(np.zeros(mat.shape[0]))
        '''GX<=h'''
        G = matrix(-1*np.eye(mat.shape[0]))
        h = matrix(np.zeros(mat.shape[0]))
        if not hedge:
            print('Min Var without Hedging')
            sol = solvers.qp(P,q,G,h)
        else:
            if type(hedgefactor) == str:
                hedgefactor = pd.read_csv(hedgefactor,parse_dates=[str(time)])
                del hedgefactor['Unnamed: 0']
            elif type(hedgefactor) == pd.DataFrame:
                hedgefactor[str(time)] = pd.to_datetime(hedgefactor[str(time)])
            if type(stockfactor) == str:
                stockfactor = pd.read_csv(stockfactor,parse_dates=[str(time)])
                del stockfactor['Unnamed: 0']
            elif type(stockfactor) == pd.DataFrame:
                stockfactor[str(time)] = pd.to_datetime(stockfactor[str(time)])
            stockfactortemp = stockfactor[stockfactor[str(time)]==i]
            stockfactortemp = stockfactortemp[stockfactortemp[str(stock)].isin(commonstock)]
            hedgefactortemp = hedgefactor[hedgefactor[str(time)]==i]
            if len(stockfactortemp) == len(hedgefactortemp):
                if not pd.isnull(Purefactor):
                    hedgefactortemp[Purefactor] += 1
                    print('Min Var with Purefactor : %s' %(Purefactor))
                else:
                    print('Min Var with 0 Factor Loading Portfolio')
                hedgefactortemp = hedgefactortemp[factorlist]
                stockfactortemp = stockfactortemp.set_index(str(stock))
                stockfactortemp = stockfactortemp[factorlist]
                if len(stockfactortemp.columns) == len(hedgefactortemp.columns):
                    A = matrix(np.array(stockfactortemp.T))
                    b = matrix(np.array(hedgefactortemp.T))
                    sol = solvers.qp(P,q,G,h,A,b)
                optim_result = pd.DataFrame(np.array(sol['x']))
                optim_result['status'] = sol['status']
                optim_result['Stkcd'] = commonstock
                optim_result['Trddt'] = i
                optim_result = optim_result.rename(columns={0: "optim"})
                result = pd.concat([result,optim_result],axis=0)
                else:
                    print('Factor not common')
            else:
                print('Data empty')
    return(result)
    

if __name__ == '__main__' :
    SpecificRisk = os.path.join(os.path.abspath('.'),'Data','SpecificRisk.csv')
    Covariance = os.path.join(os.path.abspath('.'),'Data','CovarianceEstimation')
    hfactor = os.path.join(os.path.abspath('.'),'Data','sample_hs300.csv')
    sfactor = os.path.join(os.path.abspath('.'),'Data','Factor_Preprocessing.csv')
    flist = ['beta','BP','earningsfactor','leveragefactor','RSTR','residualvolatilityfactor','Size']
    test = PortfoiloOptimzer(SpecificRisk,Covariance,'Trddt','Stkcd',hedge=False,hedgefactor=hfactor,stockfactor=sfactor,factorlist=flist,Purefactor='Size')