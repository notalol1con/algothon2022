
from fileinput import close
import pandas as pd
import numpy as np

nInst=100
currentPos = np.zeros(nInst)
MACD = pd.DataFrame()

def getMyPosition (prcSoFar):
    global currentPos
    
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

        EMA_12 = prc_series['Close'].ewm(span=12).mean()
        EMA_26 = prc_series['Close'].ewm(span=26).mean()
        MACD[i].append(EMA_12.iloc[-1] - EMA_26.iloc[-1])
        EMA_MACD = MACD[i].ewm(span=9).mean()
        prevMACD, todayMACD = MACD[i].iloc[-2], MACD[i].iloc[-1]
        prevEMA, todayEMA = EMA_MACD.iloc[-2], EMA_MACD.iloc[-2]

        if prevEMA > prevMACD

        # setting boundaries for trade criteria
        avg_prc = sum(prcSoFar[i]) / len(prcSoFar[i])
        std_multiple = np.std(prcSoFar[i])
        shift = avg_prc*std_multiple

        # setting trade criteria
        if prc_series["EWMA"].iloc[-1] + shift  <= close_prc:
            currentPos[i] -= round(8500 / close_prc)
        elif prc_series["EWMA"].iloc[-1] - shift  >= close_prc:
            currentPos[i] += round(8500 / close_prc)


    return currentPos
