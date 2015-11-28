import csv, argparse
import pandas as pd
import numpy as np
from sklearn import neighbors
from sklearn.metrics import r2_score

from constants import *

CHANGE_RANK = {FP_DST: 6, FP_QB: 30, FP_FLEX:40}
POS_DB = {'DST':FP_DST,'QB':FP_QB,'RB':FP_FLEX,'TE':FP_FLEX,'WR':FP_FLEX}

pd.set_option('display.width', 400)

def calc_dan_model(hf, pos):
    if pos in PROJECTION_TYPE[FP_QB]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_QB]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_QB]]['Points']
    if pos in PROJECTION_TYPE[FP_DST]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_DST]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_DST]]['Points']
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_FLEX]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_FLEX]]['Points']
    if pos in PROJECTION_TYPE[FP_QB] or pos in PROJECTION_TYPE[FP_DST]:
        linear_fit = np.poly1d(np.polyfit(ranks, scores, 1))
        quadratic_fit = np.poly1d(np.polyfit(ranks, scores, 2))
        ret_func = lambda x: np.mean([linear_fit(x), quadratic_fit(x)])
        print "r2 score is %f" % (r2_score(scores, map(ret_func, ranks)))
        return ret_func
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        linear_fit = np.poly1d(np.polyfit(ranks, scores, 1))
        quadratic_fit = np.poly1d(np.polyfit(ranks, scores, 2))
        log_fit = np.poly1d(np.polyfit(np.log(ranks), scores, 1))
        ret_func = lambda x: np.mean(
            [linear_fit(x), quadratic_fit(x), log_fit(np.log(x))])
        print "r2 score is %f" % (r2_score(scores, map(ret_func, ranks)))
        return ret_func


def calc_new_model(hf, pos):
    if pos in PROJECTION_TYPE[FP_QB]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_QB]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_QB]]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit
    if pos in PROJECTION_TYPE[FP_DST]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_DST]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_DST]]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                       CHANGE_RANK[FP_FLEX]]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos][hf['Avg Rank'] <
                                                        CHANGE_RANK[FP_FLEX]]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit

def calc_new_2model(hf, pos):
    if pos in PROJECTION_TYPE[FP_QB]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit
    if pos in PROJECTION_TYPE[FP_DST]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit
    elif pos in PROJECTION_TYPE[FP_FLEX]:
        ranks = hf[hf['Points'] > 0][hf['Pos'] == pos]['Avg Rank']
        scores = hf[hf['Points'] > 0][hf['Pos'] == pos]['Points']
        crazy_fit = np.poly1d(np.polyfit(ranks, scores, 5))
        print "r2 score is %f" % (r2_score(scores, map(crazy_fit, ranks)))
        return crazy_fit

def calc_knn_model(hf, pos):
    ranks = hf[hf['Pos'] == pos]['Avg Rank']
    scores = hf[hf['Pos'] == pos]['Points']
    print pos, week
    knn = neighbors.KNeighborsRegressor(10)
    ret_func = lambda x: knn.fit(np.reshape(
        ranks, (len(ranks), 1)), scores).predict(x)[0]
    print "r2 score is %f" % (r2_score(scores, map(ret_func, ranks)))
    return ret_func

WEIGHT = 0.75
def get_adjusted_score(player, regression):
    player_projected = regression(player['Avg Rank'])
    cur_variance = np.sqrt(player['Variance'])
    if player['# Games'] > 1:
        if player['Avg Rank'] > CHANGE_RANK[POS_DB[player['Pos']]]:
            if player_projected > player['D_PPG']:
                return player['D_PPG'] - cur_variance
        return player_projected * WEIGHT + player['D_PPG'] * (1 - WEIGHT) - cur_variance
    else:
        if player['Avg Rank'] > CHANGE_RANK[POS_DB[player['Pos']]]:
            return 0
        else:
            return player_projected - cur_variance

def write_week(players, regressions, year, week):
    with open('data/%s-Week%s.csv' % (year, week), 'wb') as csvfile:
        projwriter = csv.writer(csvfile, delimiter=',')
        projwriter.writerow(['playername', 'points'])
        for i, player in players.iterrows():
            player_projected = get_adjusted_score(player, regressions[player['Pos']])
            projwriter.writerow([player['PID'], player_projected])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    hist_frame = pd.read_pickle('data/histdata')
    
    for year in range(2014,CUR_YEAR + 1):
        max_week = max(hist_frame[hist_frame['Year'] == year]['Week'])
        for week in range(1, max_week + 1):
            if week == 1 and year == 2011:
                continue
            print 'Projecting week %d, year %d' % (week, year)

            players = hist_frame[hist_frame['Year'] == year][hist_frame['Week'] == week]
            previous_weeks = hist_frame[hist_frame['Year'] == year][hist_frame['Week'] < week]

            if len(previous_weeks):
                variance = pd.DataFrame(previous_weeks.groupby('PID')['Points'].var() / 
                    previous_weeks.groupby('PID')['Points'].mean() ** 2)
                variance.insert(0, 'PID', variance.index)
                variance.columns = ['PID', 'Variance']
                players = pd.merge(left=players, right=variance, on='PID')
                players['Variance'].fillna(0, inplace=True)
            else:
                players['Variance'] = 0

            i_frame = hist_frame[np.logical_or(hist_frame['Year'] < year, np.logical_and(
                hist_frame['Year'] == year, hist_frame['Week'] < week))]
            reg_funcs = {pos: calc_new_model(i_frame, pos) for pos in ALL_POS}
            write_week(players, reg_funcs, year, week)
            
    print "Generated all projections"
