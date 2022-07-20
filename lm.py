from fileinput import close
import pandas as pd
import numpy as np

nInst=100
currentPos = np.zeros(nInst)
EWMAs = []

def getMyPosition (prcSoFar):
    global currentPos, EWMAs
    curEWMA = []
    prcPct = pd.DataFrame()
    
    for i in range(len(prcSoFar)):
        close_prc = prcSoFar[i][-1]

        # days looking back for moving avg
        span = 15
        span_ceiling = 30
        span_floor = 10
        
        # changing span depending on volatility
        if len(prcSoFar[0]) > 31:

            todayVola = np.std(prcSoFar[i][-31:-2])
            yesterdayVola = np.std(prcSoFar[i][-30:])

            normVola = (todayVola - yesterdayVola) / todayVola
            span = round(span * (1 + normVola))

            if span > span_ceiling:
                span = span_ceiling
            elif span < span_floor:
                span = span_floor


        # calculate moving avg
        prc_series = pd.DataFrame(prcSoFar[i], columns=['Close'])
        prc_series['EWMA'] = prc_series['Close'].ewm(span=span).mean()
        prcPct[i] = prc_series['Close']

        # setting boundaries for trade criteria
        avg_prc = sum(prcSoFar[i]) / len(prcSoFar[i])
        std_multiple = np.std(prcSoFar[i])
        shift = avg_prc*std_multiple

        curEWMA.append((prc_series["EWMA"].iloc[-1],shift))
    
    EWMAs.append(curEWMA)

    # setting trade criteria
    for i in range(len(prcSoFar)):
        close_prc = prcSoFar[i][-1]
        avg_change = prcPct[i].pct_change().mean()
        std_change = np.std(prcPct[i].pct_change())
        curEWMA, curShift = EWMAs[-1][i]
        changedPos = 0

        

        if curEWMA + curShift  <= close_prc:
            currentPos[i] -= round(8500 / close_prc)
            changedPos = -round(8500 / close_prc)
        elif curEWMA - curShift  >= close_prc:
            currentPos[i] += round(8500 / close_prc)
            changedPos = round(8500 / close_prc)
        else:
            continue
        
        if len(prcSoFar[0]) <= 31:
            continue
        curStockPos, weightedPct = 0, 0
        currentTotal, changes = giveCorrelatedChanges(prcPct, i)
        
        if len(changes) == 0:
            continue
        for change in changes:
            curCorr, leadShift, curStock = change
            # curEWMA, curShift = EWMAs[-leadShift][curStock]
            pctChange = (prcSoFar[curStock][-leadShift] - prcSoFar[curStock][-leadShift-1])/prcSoFar[curStock][-leadShift-1]
            weightedPct += curCorr/currentTotal * pctChange
            # if curEWMA + curShift  <= prcSoFar[curStock][-leadShift]:
            #     curStockPos -= round(8500 / close_prc * curCorr/currentTotal)
            # elif curEWMA - curShift  >= prcSoFar[curStock][-leadShift]:
            #     curStockPos += round(8500 / close_prc * curCorr/currentTotal)
            print(weightedPct)
        if abs(weightedPct) < 0.2:
            print(changedPos)
            currentPos[i] -= changedPos
            changedPos = abs(weightedPct)/(abs(avg_change) + std_change) * changedPos
            currentPos[i] += changedPos
        # currentPos[i] += curStockPos

    return currentPos


def giveCorrelatedChanges(prcPct, stockName):
    numStocks = 100
    backtrackDays = 30
    leaderDays = 9
    currentTotal = 0
    curStock = prcPct[stockName]
    curStock = curStock.iloc[-backtrackDays:]
    changes = []
    for i in range(numStocks):
        if i == stockName:
            # changes.append((1,1, i))
            # currentTotal += 1
            continue
        bestCorr = 0
        shift = None
        for j in range(3,leaderDays,3):
            curComp = prcPct[i].shift(j).iloc[-backtrackDays:]
            curCorr = curStock.corr(curComp)
            if abs(curCorr) > abs(bestCorr):
                bestCorr = curCorr 
                shift = j
        if abs(bestCorr) > 0.9:
            currentTotal += abs(bestCorr)
            changes.append((bestCorr, shift, i))
    return currentTotal, changes