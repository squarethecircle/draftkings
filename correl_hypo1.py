import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import pdb
from optimize import *
from constants import *

# if cross team == True then it's cross whole team otherwise just cross team + position
def r2_sq(data, p, cross_team=True):
	playerpoints = pd.DataFrame(data[data['Pos']==p].groupby(['PID'])['Points'].sum())
	playerpoints['PID'] = playerpoints.index

	teampoints = data.groupby(['Team'])['Points'].sum() if cross_team else data.groupby(['Team', 'Pos'])['Points'].sum()
	rrank = {}
	for pid, points in playerpoints.iterrows():
	    team = data[data['PID'] == pid].iloc[0]['Team']
	    pos = data[data['PID'] == pid].iloc[0]['Pos']
	    rrank[pid] = points['Points'] / teampoints[team] if cross_team else points['Points'] / teampoints[team][pos]

	rrank = pd.DataFrame(rrank.items())
	rrank.columns = ['PID', 'RRank']

	variances = data.groupby(['PID'])['Points'].var() 
	variances /= data.groupby(['PID'])['Points'].mean() ** 2

	variances = pd.DataFrame(variances)
	variances['PID'] = variances.index
	variances.columns = ['Variance', 'PID']

	merged = variances.merge(rrank, on='PID')
	merged = merged[merged['Variance'].notnull()]

	# remove shit
	merged = merged[merged['RRank'] > 0.2][merged['RRank'] < 1]

	quadratic_fit = np.poly1d(np.polyfit(merged['RRank'], merged['Variance'], 2))

	correl = r2_score(merged['Variance'], map(quadratic_fit, merged['RRank']))

	return correl, merged

print 'Cross Team Correlation'
for p in ALL_POS:
	if p == 'DST':
		continue
	d = df[df['Year'] == 2011]
	correl, merged = r2_sq(d, p)
	plt.scatter(merged['RRank'], merged['Variance'])
	plt.show()
	print p + ' = ' + str(correl)

print 'Cross Team-Pos Correlation'
for p in ALL_POS:
	if p == 'DST':
		continue
	d = df[df['Year'] == 2011]
	correl, merged = r2_sq(d, p, cross_team=False)
	plt.scatter(merged['RRank'], merged['Variance'])
	plt.show()
	print p + ' = ' + str(correl)
