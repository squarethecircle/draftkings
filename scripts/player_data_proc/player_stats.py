import sys
sys.path.append('..')
from utils import *
import numpy as np

# Run like
# python player_stats.py C:/Users/YourUser/Dropbox/DFS/data/players

dn = sys.argv[1]
recs = proc_data(dn + '/raw')

players = {}
for r in recs:
    if r.player_ID not in players:
        players[r.player_ID] = []
    players[r.player_ID].append(r.dk_score)

with open(os.path.join(dn, 'player_stats.csv'), 'w') as wr:
    wr.write('NAME,POS,NUM_GAMES,MEAN,MEDIAN,STDEV\n')
    for p in players:
        arr = np.asarray(players[p])
        wr.write('{},{},{},{},{},{}\n'.format(p,p.split('_')[-1],
            arr.size, arr.mean(), np.median(arr), arr.std()))
