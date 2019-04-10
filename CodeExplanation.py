# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g8750jeFAl9DjOC6vKk_dsyFo0nJkElf

## 1. Generate effective frontier combinations by Monte Carlo simulation
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd 
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

##import data
#data2=pd.read_csv('/content/drive/My Drive/Colab Notebooks/SharePrices.csv',encoding='gbk',index_col='Date')
data2=pd.read_csv('/content/drive/My Drive/Colab Notebooks/SharesPrices3.csv',encoding='gbk',index_col='Date')
#data2=pd.read_csv('/content/drive/My Drive/Colab Notebooks/SharePrice1.csv',encoding='gbk',index_col='Date')
data2

"""*Calculate the expected return rate and volatility of the stock portfolio under different weights, and use it to map the income fluctuations of the stock portfolio under different weights.*"""

log_returns=np.log(data2.pct_change()+1)
number = 10000 
stock_num=len(log_returns.columns)#Number of shares
weights=np.random.rand(number, stock_num)
weights/=np.sum(weights, axis = 1).reshape(number,1) 
pret=np.dot(weights, log_returns.mean()*250)#Expected annualized return on stock portfolio
pvol=np.diag(np.sqrt(np.dot(weights,np.dot(log_returns.cov()*250,weights.T))))#Expected annualized volatility of stock portfolios

plt.figure(figsize=(10,6))
plt.scatter(pvol,pret,c=pret/pvol,marker='o')
plt.xlabel('expected vol')
plt.ylabel('expected return')
plt.grid(True)
plt.colorbar(label='sharp ratio')

"""## 2.Identify the most optimal portfolio in these combinations"""

import scipy.optimize as sco

"""*Write the optimized constraints, the convention of the minimum function is expressed as follows*"""

cons=({'type':'eq','fun': lambda x: np.sum(x)-1})#The constraint is that the sum of all parameters (weights) is 1.
bnd=tuple((0,1) for i in range(stock_num))##We also limit the parameter value (weight) between 0 and 1. These values are supplied to the minimized function in a tuple of multiple tuples.

"""*Write the calculation function of the target variable (3) The target combination for solving the Sharpe maximization, risk minimization, and maximization of profit*"""

def statistics(weights):
    weights=np.array(weights)
    pret=np.dot(weights, log_returns.mean()*252)#Expected annualized return on stock portfolio
    pvol=np.sqrt(np.dot(weights.T,np.dot(log_returns.cov()*252,weights)))#Expected annualized volatility of stock portfolios
    return np.array([pret, pvol, pret/pvol])

###Solving the combined weight of the maximum expected return
def min_neg_pret(weights):
    return  -1*statistics(weights)[0] 
opts_maxReturn=sco.minimize(min_neg_pret, stock_num*[1/stock_num], method='SLSQP', bounds=bnd, constraints=cons)
print(opts_maxReturn['x'].round(3))
print(statistics(opts_maxReturn['x']))

 ###Solving combination weights with minimized volatility
def min_vol(weights):
    return statistics(weights)[1] 
opts_minVolatility = sco.minimize(min_vol, stock_num*[1/stock_num], method='SLSQP',bounds=bnd, constraints=cons)
print(opts_minVolatility['x'].round(3))
print(statistics(opts_minVolatility['x']))

###Solve the largest combination weight of the Sharpe rate
def min_neg_sharp(weights):
    return -1*statistics(weights)[2]
opts_maxSharpRatio = sco.minimize(min_neg_sharp, stock_num*[1/stock_num], method='SLSQP', bounds=bnd, constraints=cons)
print(opts_maxSharpRatio['x'].round(3))
print(statistics(opts_maxSharpRatio['x'])) #Expected rate of return, expected volatility, and SharpRatio

"""*Calculate the Markowitz Efficient Frontier*"""

trets=np.linspace(0.12,0.21,50)
tvols=[]
 
for trets_i in trets:
    cons1=({'type':'eq','fun': lambda x: np.sum(x)-1},{'type':'eq','fun': lambda y: statistics(y)[0]-trets_i})#Constraint is the sum of all parameters (weights) is 1, and the expected return is equal to the target return
    res=sco.minimize(min_vol,stock_num*[1/stock_num], method='SLSQP', bounds=bnd, constraints=cons1)
    tvols.append(res['fun'])
tvols=np.array(tvols)

##plot
plt.figure(figsize=(10,6))
plt.scatter(tvols, trets,marker='x',c=trets/tvols, label='Efficient Frontier')
plt.scatter(pvol, pret, marker='o', c=pret/pvol)
plt.colorbar(label='SharpRatio')

plt.plot(statistics(opts_maxSharpRatio['x'])[1],statistics(opts_maxSharpRatio['x'])[0],marker='*',markersize=15,label='MaxSharpRatio Portfolio')
plt.plot(statistics(opts_minVolatility['x'])[1],statistics(opts_minVolatility['x'])[0],marker='*',markersize=15,label='MinVolatility Portfolio')
plt.plot(statistics(opts_maxReturn['x'])[1],statistics(opts_maxReturn['x'])[0],marker='*',markersize=15,label='MaxReturn Portfolio')
plt.grid(True)

plt.xlabel('Expected Vol')
plt.ylabel('Expected Return')
plt.legend()

