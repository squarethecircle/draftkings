import sys
sys.path.append('..')
import collections
from utils import *
import numpy as np

# Run like
# python pos_correls.py C:/Users/YourUser/Dropbox/DFS/data/players

dn = sys.argv[1]
recs = proc_data(dn + '/raw')

def pairs(arr1, arr2):
    ret = []
    for a1 in arr1:
        for a2 in arr2:
            ret.append([a1, a2])
    return ret

teams = set([r.team for r in recs])
correls = collections.OrderedDict()
correls['opp_qb'] = []
correls['opp_wr'] = []
correls['opp_rb'] = []
correls['opp_te'] = []
correls['qb_wr'] = []
correls['qb_rb'] = []
correls['qb_te'] = []
correls['wr_rb'] = []
correls['wr_te'] = []
correls['rb_te'] = []
outputs = [',,' + ','.join(correls.keys()) + '\n']
for year in [2014,2015]:
    for week in xrange(1,16):
        thisweek = [r for r in recs if r.week==week and r.year==year]
        for pr in correls:
            correls[pr] = []
        for t in teams:
            thisteam = [r for r in thisweek if r.team==t]
            opp_d = [r.dk_score for r in thisweek if r.opp==t and r.pos == 'DST']
            qbs = [r.dk_score for r in thisteam if r.pos == 'QB']
            wr = [r.dk_score for r in thisteam if r.pos == 'WR']
            rb = [r.dk_score for r in thisteam if r.pos == 'RB']
            te = [r.dk_score for r in thisteam if r.pos == 'TE']
            correls['opp_qb'] += pairs(opp_d, qbs)
            correls['opp_wr'] += pairs(opp_d, wr)
            correls['opp_rb'] += pairs(opp_d, rb)
            correls['opp_te'] += pairs(opp_d, te)
            correls['qb_wr'] += pairs(qbs, wr)
            correls['qb_rb'] += pairs(qbs, rb)
            correls['qb_te'] += pairs(qbs, te)
            correls['wr_rb'] += pairs(wr, rb)
            correls['wr_te'] += pairs(wr, te)
            correls['rb_te'] += pairs(rb, te)
        line=''
        nonzero = False
        for pr in correls:
            arr = np.asarray(correls[pr]).transpose()
            corr = 0 if arr.size == 0 else np.corrcoef(arr)[0,1]
            if corr != 0 and not np.isnan(corr):
                nonzero = True
            line = line + ',{:.4f}'.format(corr)
        if nonzero:
            outputs.append('{},{}'.format(year,week) + line + '\n')
with open(os.path.join(dn, 'pos_correls.csv'), 'w') as wr:
    wr.writelines(outputs)
