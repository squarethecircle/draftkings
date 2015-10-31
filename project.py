import pandas as pd
from constants import *
import argparse
import numpy as np
import csv
from sklearn import neighbors
from sklearn.metrics import r2_score


def calc_dan_model(hf,pos):
    ranks = hf[hf['Pos'] == pos]['Avg Rank']
    scores = hf[hf['Pos'] == pos]['Points']
    if pos in PROJECTION_TYPE[FP_QB] or pos in PROJECTION_TYPE[FP_DST]:
        linear_fit = np.poly1d(np.polyfit(ranks,scores,1))
        quadratic_fit = np.poly1d(np.polyfit(ranks,scores,2))
        ret_func = lambda x: np.mean([linear_fit(x),quadratic_fit(x)])
        print "r2 score is %f" % (r2_score(scores,map(ret_func,ranks)))
        return ret_func
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        linear_fit = np.poly1d(np.polyfit(ranks,scores,1))
        quadratic_fit = np.poly1d(np.polyfit(ranks,scores,2))
        log_fit = np.poly1d(np.polyfit(np.log(ranks),scores,1))
        ret_func = lambda x: np.mean([linear_fit(x),quadratic_fit(x),log_fit(np.log(x))])
        print "r2 score is %f" % (r2_score(scores,map(ret_func,ranks)))
        return ret_func


def calc_new_model(hf,pos):
    ranks = hf[hf['Points']>0][hf['Pos'] == pos]['Avg Rank']
    scores = hf[hf['Points']>0][hf['Pos'] == pos]['Points']
    if pos in PROJECTION_TYPE[FP_QB] or pos in PROJECTION_TYPE[FP_DST]:
        crazy_fit = np.poly1d(np.polyfit(ranks,scores,5))
        print "r2 score is %f" % (r2_score(scores,map(crazy_fit,ranks)))
        return crazy_fit
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        crazy_fit = np.poly1d(np.polyfit(ranks,scores,5))
        print "r2 score is %f" % (r2_score(scores,map(crazy_fit,ranks)))
        return crazy_fit


def calc_knn_model(hf,pos):
    ranks = hf[hf['Pos'] == pos]['Avg Rank']
    scores = hf[hf['Pos'] == pos]['Points']
    print pos, week
    knn = neighbors.KNeighborsRegressor(10)
    ret_func = lambda x: knn.fit(np.reshape(ranks,(len(ranks),1)),scores).predict(x)[0]
    print "r2 score is %f" % (r2_score(scores,map(ret_func,ranks)))
    return ret_func




def write_week(players,regressions,year,week):
    with open('data/%s-Week%s.csv' % (year,week), 'wb') as csvfile:
            projwriter = csv.writer(csvfile, delimiter=',')
            projwriter.writerow(['playername','points'])
            for i,player in players.iterrows():
                player_projected = regressions[player['Pos']](player['Avg Rank'])
                projwriter.writerow([player['PID'], player_projected])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    hist_frame = pd.read_pickle('data/histdata')
    cur_frame = pd.read_pickle('data/curprojs')
    for year in range(2011, CUR_YEAR+1):
        max_week = max(hist_frame[hist_frame['Year'] == year]['Week'])
        for week in range(1, max_week+1):
            if week == 1 and year == 2011:
                continue
            print year, week
            i_frame = hist_frame[np.logical_or(hist_frame['Year'] < year,np.logical_and(hist_frame['Year'] == year,hist_frame['Week'] < week))]
            reg_funcs = {pos: calc_new_model(i_frame, pos) for pos in ALL_POS}
            write_week(hist_frame[hist_frame['Year'] == year][hist_frame['Week'] == week], reg_funcs, year, week)

    print "Generated all projections"
    
