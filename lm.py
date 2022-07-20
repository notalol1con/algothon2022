from sklearn import linear_model
import numpy as np
import pandas as pd

nInst = 0
nt = 0

# Commission rate
commRate = 0.0025 # was 0.0050

# Dollar position limit (maximum absolute dollar value of any individual stock position)
dlrPosLimit = 10000

timeOut=600
numStocks = 100

pricesFile="./prc500.txt"
prcAll = df=pd.read_csv(pricesFile, sep='\s+', header=None, index_col=None)

def recalculateModel(prcHist, stockName):
    global numStocks
    backtrackDays = 30
    leaderDays = 15
    X = [[] for i in range(backtrackDays)]
    X_pred = [[] for i in range(5)]
    curStock = prcHist[stockName][-30:]
    for i in range(numStocks):
        if i == stockName:
            continue
        bestAr = None
        bestCorr = None
        shift = None
        for j in range(5,leaderDays):
            curComp = prcHist[i].shift(j)[-30:]
            curCorr = curStock.corr(curComp)
            if abs(curCorr) > abs(bestCorr):
                bestCorr = curCorr
                bestAr = curComp
                shift = j
        if bestCorr != None and abs(bestCorr) > 0.9:
            for k in range(backtrackDays):
                X[k].append(bestAr[k])
            for k in range(5):
                X_pred[k].append(curComp[-shift+k])
    model = linear_model.LinearRegression().fit(X,curStock)
    y_pred = linear_model.LinearRegression().predict(X_pred)
    return y_pred
