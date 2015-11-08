import sys
sys.path.append('..')
import operator
import os
import numpy as np
import zipfile
from constants import *

#################################################################################
# Run like this:
#
# python eval_users.py [DATA_FOLDER]
#
# [DATA_FOLDER] is a folder containing a subfolder marked '1', '2' etc for each
# week. within each folder, put the raw zip files from draftkings contest as
# well as a file called 'playervals.csv' with player point values for that week.
# player values must be formatted like "Aaron Rodgers,22.187" etc.
#
#################################################################################

dn = sys.argv[1]
contests_by_week = {}
pvals_by_week = {}
for w in [w for w in os.listdir(dn) if os.path.isdir(os.path.join(dn, w))]:
    contests_by_week[w] = {}
    with open(os.path.join(dn, w, 'playervals.csv'), 'r') as re:
        pvals_by_week[w] = dict((' '.join(x[0].split('_')[:-1]), x[1]) for x in
                map(lambda l: l.strip().split(','), re.readlines()))
    for zf in [f for f in os.listdir(os.path.join(dn, w)) if 'zip' in f]:
        z = zipfile.ZipFile(os.path.join(dn, w, zf))
        for f in z.namelist():
            if f[0] == '_':
                continue
            contest_id = f.split('.')[0].split('-')[2]
            with z.open(f) as re:
                contests_by_week[w][contest_id] = \
                        map(lambda l: l.strip().split(','), re.readlines()[1:])

def conv_player_string(player_str):
    delim_strs = ['QB', 'RB', 'WR', 'TE', 'FLEX', 'DST']
    splits = player_str.split(' ')
    players_list = []
    nums = {}
    if player_str.strip() == '':
        return {}
    for s in splits:
        if s in delim_strs:
            if s not in nums:
                nums[s] = 0
            nums[s] = nums[s] + 1
            players_list.append([s + str(nums[s]), []])
        else:
            players_list[-1][1].append(s)
    return dict((p[0], clean_name(' '.join(p[1]))) for p in players_list)

users = {}
for w in contests_by_week:
    benchmark = max(contests_by_week[w].iteritems(), key=lambda x:len(x[1]))[0]
    maxtot = 0
    mintot = 1e12
    pvals = pvals_by_week[w]
    users_thisweek = {}
    not_found = {}
    for contest_id in contests_by_week[w]:
        print contest_id
        outputs = ['Name,QB,RB1,RB2,WR1,WR2,WR3,TE,FLEX,DST,TOTAL\n']
        for s in contests_by_week[w][contest_id]:
            lineup = conv_player_string(s[5].strip())
            if len(lineup) == 0:
                continue
            allfound = True
            for l in lineup:
                if lineup[l] in pvals:
                    lineup[l] = pvals[lineup[l]]
                else:
                    allfound = False
                    if lineup[l] != 'LOCKED':
                        if lineup[l] not in not_found:
                            not_found[lineup[l]] = 0
                        not_found[lineup[l]] += 1
            if allfound:
                lis = [lineup['QB1'],
                        lineup['RB1'],
                        lineup['RB2'],
                        lineup['WR1'],
                        lineup['WR2'],
                        lineup['WR3'],
                        lineup['TE1'],
                        lineup['FLEX1'],
                        lineup['DST1']]
                tot = sum(map(lambda f: float(f), lis))
                if contest_id == benchmark:
                    if tot > maxtot:
                        maxtot = tot
                    if tot < mintot:
                        mintot = tot
                lis.append(tot)
                username = s[2].split(' ')[0]
                #outputs.append('{},{},{},{},{},{},{},{},{},{},{}\n'.format(username, *lis))
                if username not in users_thisweek:
                    users_thisweek[username] = []
                users_thisweek[username].append(tot)
        #with open(os.path.join(dn, w, 'processed_{}.csv'.format(contest_id)), 'w') as wr:
        #    wr.writelines(outputs)
    rg = maxtot - mintot
    for n in not_found:
        print n, not_found[n]
    for username in users_thisweek:
        if username not in users:
            users[username]=[]
        users[username] += map(lambda s: 1.-(maxtot-s)/rg, users_thisweek[username])

with open(os.path.join(dn, 'users.csv'), 'w') as wr:
    for username in users:
        scores = np.asarray(users[username])
        wr.write('{},{},{},{}\n'.format(username, scores.size, np.median(scores), scores.std()))
