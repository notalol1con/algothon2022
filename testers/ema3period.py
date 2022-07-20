from fileinput import close
import pandas as pd
import numpy as np

# days looking back for moving avg
weekSpan = 7
fortnightSpan = 14
monthSpan = 30

nInst=100
currentPos = np.zeros(nInst)

def position3EMA (prcSoFar):
    global currentPos
    
    for i in range(len(prcSoFar)):
        close_prc = prcSoFar[i][-1]

        flag_short = False
        flag_long = False

        # calculate moving avg
        prc_series = pd.DataFrame(prcSoFar[i], columns=['Close'])
        prc_series['ShortEWMA'] = prc_series['Close'].ewm(span=weekSpan).mean()
        prc_series['MidEWMA'] = prc_series['Close'].ewm(span=fortnightSpan).mean()
        prc_series['LongEWMA'] = prc_series['Close'].ewm(span=monthSpan).mean()

        # setting trade criteria
        for j in range(0, len(prc_series)):
            if (prc_series['MidEWMA'][j] < prc_series['LongEWMA'][j]) and (prc_series['ShortEWMA'][j] < prc_series['MidEWMA'][j]) and flag_long == False:
                currentPos[i] -= round(5000 / close_prc)
                flag_short = True
            elif flag_short == True and (prc_series['ShortEWMA'][j] > prc_series['MidEWMA'][j]):
                currentPos[i] += round(5000 / close_prc)
                flag_short = False
            elif (prc_series['MidEWMA'][j] > prc_series['LongEWMA'][j]) and (prc_series['ShortEWMA'][j] > prc_series['MidEWMA'][j]) and flag_long == False:
                currentPos[i] -= round(5000 / close_prc)
                flag_long = True
            elif flag_long == True and (prc_series['ShortEWMA'][j] < prc_series['MidEWMA'][j]):
                currentPos[i] += round(5000 / close_prc)
                flag_long = False

    return currentPos