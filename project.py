import pandas as pd
from constants import *
import argparse
import numpy as np
import csv 

def calc_dan_model(hf,pos,week):
	ranks = hf[hf['Pos'] == pos][hf['Week'] < week]['Avg Rank']
	scores = hf[hf['Pos'] == pos][hf['Week'] < week]['DK points']
	print pos, week
	if pos in PROJECTION_TYPE[FP_QB] or pos in PROJECTION_TYPE[FP_DST]:
		linear_fit = np.poly1d(np.polyfit(ranks,scores,1))
		quadratic_fit = np.poly1d(np.polyfit(ranks,scores,2))
		ret_func = lambda x: np.mean([linear_fit(x),quadratic_fit(x)])
		print "r2 score is %f" % (r_squared(scores,map(ret_func,ranks)))
		return ret_func
	elif pos in PROJECTION_TYPE[FP_FLEX]:
		linear_fit = np.poly1d(np.polyfit(ranks,scores,1))
		quadratic_fit = np.poly1d(np.polyfit(ranks,scores,2))
		log_fit = np.poly1d(np.polyfit(np.log(ranks),scores,1))
		ret_func = lambda x: np.mean([linear_fit(x),quadratic_fit(x),log_fit(np.log(x))])
		print "r2 score is %f" % (r_squared(scores,map(ret_func,ranks)))
		return ret_func

def r_squared(real_scores, predicted_scores):
    real_mean = np.sum(real_scores)/len(real_scores)
    ssreg = np.sum((predicted_scores-real_mean)**2)
    sstot = np.sum((real_scores - real_mean)**2)
    return ssreg / sstot


def write_week(players,regressions,week):
	with open('data/week%s.csv' % week, 'wb') as csvfile:
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
	cur_week = max(hist_frame['Week']) + 1
	for week in range(2,cur_week):
		reg_funcs = {pos:calc_dan_model(hist_frame,pos,week) for pos in ALL_POS}
		players = hist_frame[hist_frame['Week']==week]
		write_week(players,reg_funcs,week)
	reg_funcs = {pos:calc_dan_model(hist_frame,pos,cur_week) for pos in ALL_POS}
	write_week(cur_frame,reg_funcs,0)
	print "Generated projections for weeks 2-%s" % cur_week
	