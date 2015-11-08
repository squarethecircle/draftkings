import sys
import os
sys.path.append('..')
import collections
from constants import *
import numpy as np
import pandas as pd

# Run like
# python pos_correls.py C:/Users/YourUser/Dropbox/DFS/data/players

hf = pd.read_pickle('../data/histdata')

def pairs(arr1, arr2):
    ret = []
    for a1 in arr1:
        for a2 in arr2:
            ret.append([a1, a2])
    return ret

teams = set([v[0] for v in hf[['Team']].values])
correls = collections.OrderedDict()
correls['dst_qb'] = []
correls['dst_wr'] = []
correls['dst_rb'] = []
correls['dst_te'] = []
correls['qb_wr'] = []
correls['qb_rb'] = []
correls['qb_te'] = []
correls['wr_rb'] = []
correls['wr_te'] = []
correls['rb_te'] = []
outputs = [',,' + ','.join(correls.keys()).upper() + '\n']
corr_bymo = {}
for pr in correls:
    corr_bymo[pr]=[]
for year in [2015]:
    for week in xrange(1,16):
        tw = hf[hf['Week']==week]
        if tw.empty:
            continue
        for pr in correls:
            correls[pr] = []
        for t in teams:
            tm = tw[tw['Team']==t]
            dst_d = tw[tw.apply(lambda s: isinstance(s['Matchup'], str) and
                s['Matchup'].split(' ')[2]==t, axis=1)][tw['Pos']=='DST']['DK points'].values
            qbs = tm[tm['Pos']=='QB']['DK points'].values
            wr = tm[tm['Pos']=='WR']['DK points'].values
            rb = tm[tm['Pos']=='RB']['DK points'].values
            te = tm[tm['Pos']=='TE']['DK points'].values
            correls['dst_qb'] += pairs(dst_d, qbs)
            correls['dst_wr'] += pairs(dst_d, wr)
            correls['dst_rb'] += pairs(dst_d, rb)
            correls['dst_te'] += pairs(dst_d, te)
            correls['qb_wr'] += pairs(qbs, wr)
            correls['qb_rb'] += pairs(qbs, rb)
            correls['qb_te'] += pairs(qbs, te)
            correls['wr_rb'] += pairs(wr, rb)
            correls['wr_te'] += pairs(wr, te)
            correls['rb_te'] += pairs(rb, te)
        line=''
        nonzero = False
        for pr in correls:
            arr = np.asarray(correls[pr]).transpose()[:,:50]
            corr = 0 if arr.size == 0 else np.corrcoef(arr)[0,1]
            if corr != 0 and not np.isnan(corr):
                corr_bymo[pr].append(corr)
                nonzero = True
            line = line + ',{:.4f}'.format(corr)
        if nonzero:
            outputs.append('{},{}'.format(year,week) + line + '\n')
with open(os.path.join(sys.argv[1], 'pos_correls_bymo.csv'), 'w') as wr:
    wr.writelines(outputs)
with open(os.path.join(sys.argv[1], 'pos_correls.csv'), 'w') as wr:
    wr.write('POS_PR,CORR\n')
    for pr in corr_bymo:
        wr.write('{},{}\n'.format(pr.upper(), np.mean(corr_bymo[pr])))
        ps=pr.upper().split('_')
        wr.write('{},{}\n'.format(ps[1]+'_'+ps[0], np.mean(corr_bymo[pr])))
