import sys
sys.path.append('..')
from utils import *

# Run like:
# python procdata.py C:/Users/yourUser/Dropbox/DFS/data/players [year_num] [week_num]

dn = sys.argv[1]
records = proc_data(dn + '/raw')
year = int(sys.argv[2])
week = int(sys.argv[3])
with open(os.path.join(dn, 'player_data_{}_{}.csv'.format(year, week)), 'w') as wr:
    for r in [rec for rec in records if rec.week == week and rec.year == year]:
        wr.write('{},{},{},{},{},{},{},{}\n'\
                .format(r.year, r.week, r.player_ID, r.name, \
                r.pos, r.dk_salary, r.dk_score, r.fp_avg_rank))
