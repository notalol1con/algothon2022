from fileinput import close
import pandas as pd
import numpy as np

nInst=100
currentPos = np.zeros(nInst)

def positionGradient(prcSoFar):
    global currentPos
    
    for i in range(len(prcSoFar)):
        close_prc = prcSoFar[i][-1]

        # days looking back for moving avg
        span = 15
        span_ceiling = 30
        span_floor = 10
        grad = 0
        
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

        # setting boundaries for trade criteria
        avg_prc = sum(prcSoFar[i]) / len(prcSoFar[i])
        std_multiple = np.std(prcSoFar[i])
        shift = avg_prc*std_multiple

        
        # Calculate gradient for the period
        if (5 < len(prcSoFar[0])):
            grad = (close_prc - prcSoFar[i][-(5+1)]) / 5.0

        # setting trade criteria
        if (prc_series["EWMA"].iloc[-1] + shift  <= close_prc) and grad < 0:
            currentPos[i] -= round(8500 / close_prc)
        elif (prc_series["EWMA"].iloc[-1] - shift  >= close_prc) and grad > 0:
            currentPos[i] += round(8500 / close_prc)
        

    return currentPos