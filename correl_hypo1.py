from optimize import *
import numpy as np
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt


y1 = df[df['Year']==2011]

playerpoints = pd.DataFrame(y1.groupby(['PID'])['Points'].sum())
playerpoints['PID'] = playerpoints.index

teampoints = y1.groupby(['Team'])['Points'].sum()

rrank = {}
for pid, data in playerpoints.iterrows():
	team = y1[y1['PID']==pid].iloc[0]['Team']
	rrank[pid] = data['Points'] / teampoints[team]

rrank = pd.DataFrame(rrank.items())
rrank.columns = ['PID', 'RRank']


variances = y1.groupby(['PID'])['Points'].var()
variances = pd.DataFrame(variances)
variances['PID'] = variances.index
variances.columns = ['Variance', 'PID']

merged = variances.merge(rrank, on='PID')
merged = merged[merged['Variance'].notnull()]

#remove shit
merged = merged[merged['RRank'] > 0.2]


quadratic_fit = np.poly1d(np.polyfit(merged['RRank'],merged['Variance'],2))

correl = r2_score(merged['Variance'], map(quadratic_fit,merged['RRank']))

plt.scatter(merged['RRank'], merged['Variance'])
plt.show()