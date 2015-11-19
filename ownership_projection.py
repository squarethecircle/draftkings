import csv
from os import listdir
from os.path import isfile, join

import numpy as np
import matplotlib.pyplot as plt

from optimize import pd, df
from constants import *

### only works for week 10

ALL_POS = ['QB', 'RB', 'WR', 'TE', 'DST', 'FLEX']
path_to_data = 'data/10/'

num_lineups = 0

player_count = {}
files = [ f for f in listdir(path_to_data) if isfile(join(path_to_data,f)) ]
for f in files:
	with open(path_to_data + f, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for row in reader:
			num_lineups += 1
			lineup = row[-1]
			for pos in ALL_POS:
				lineup = lineup.replace(pos, ';')

			for name in lineup.split(';')[1:]:
				clean_name = name.strip()
				if clean_name in player_count:
					player_count[clean_name] += 1
				else:
					player_count[clean_name] = 1

### ownership rates
OR_dict = { p: player_count[p] / float(num_lineups) for p in player_count }

### name translation
name_translation = dict(zip(FANPROS_DST_NAMES.values(), FANPROS_DST_NAMES.keys()))
name_translation['Ted Ginn Jr.'] = 'Ted Ginn'
name_translation['Cecil Shorts III'] = 'Cecil Shorts'
name_translation['Corey Brown'] = 'Philly Brown'

### ppg / salary
p_s_ratio = []

for k,v in OR_dict.items():
	if k in name_translation:
		OR_dict[name_translation[k]] = v
		del OR_dict[k]
		k = name_translation[k]

	r = df[df['Year']==2015][df['Week']==10][df['Name']==k]
	if len(r) == 0:
		del OR_dict[k]
	else:
		prs = r.iloc[0]['D_PPG'] / r.iloc[0]['Salary'] * 100
		if np.isnan(prs):
			del OR_dict[k]
		else:
			p_s_ratio.append((k, prs))

ORs = [p[1] for p in sorted(OR_dict.items(), key=lambda x: x[0])]
PRS = [p[1] for p in sorted(p_s_ratio, key=lambda x: x[0])]



# print PRS
fit = np.poly1d(np.polyfit(PRS, ORs, 1))

plt.plot(PRS, ORs, '.')
plt.plot(PRS, fit(PRS), '-')
plt.show()
