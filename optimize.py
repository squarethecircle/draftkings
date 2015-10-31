# A huge thanks to swanson
# this solution is almost wholly based off
# https://github.com/swanson/degenerate

import csv
import subprocess
from sys import argv
import time
import argparse
from ortools.linear_solver import pywraplp
import pdb
import numpy as np
from orm import Player, Roster
from constants import *
import pandas as pd
import warnings
import csv

warnings.filterwarnings("ignore")


parser = argparse.ArgumentParser()

for opt in OPTIMIZE_COMMAND_LINE:
    parser.add_argument(opt[0], help=opt[1], default=opt[2], type=int)

args = parser.parse_args()
MAX_SIMILARITY = args.s
df = pd.read_pickle('data/histdata')
get_score = lambda n, y, w: df[df['PID'] == n][
    df['Year'] == y][df['Week'] == w]['Points']


def check_missing_players(all_players, min_cost, e_raise):
    '''
    check for significant missing players
    as names from different data do not match up
    continues or stops based on inputs
    '''
    contained_report = len(filter(lambda x: x.marked == 'Y', all_players))
    total_report = len(all_players)

    miss = len(filter(lambda x: x.marked != 'Y' and x.cost > min_cost,
                      all_players))

    if e_raise < miss:
        print 'Got {0} out of {1} total'.format(str(contained_report),
                                                str(total_report))
        raise Exception('Total missing players at price point: ' + str(miss))


def run_solver(solver, all_players, max_flex, chosen_dict):
    '''
    handle or-tools logic
    '''
    variables = []

    for player in all_players:
        variables.append(solver.IntVar(0, 1, player.pid))

    objective = solver.Objective()
    objective.SetMaximization()
    for i, player in enumerate(all_players):
        objective.SetCoefficient(variables[i], player.proj)
    salary_cap = solver.Constraint(0, SALARY_CAP)
    for i, player in enumerate(all_players):
        salary_cap.SetCoefficient(variables[i], player.cost)

    was_chosen = lambda r, p: int(r in chosen_dict and p in chosen_dict[r])
    for lineup_num in range(len(chosen_dict)):
        diversity_criterion = solver.Constraint(0, MAX_SIMILARITY)
        for i, player in enumerate(all_players):
            res = was_chosen(lineup_num, player.pid)
            diversity_criterion.SetCoefficient(variables[i], res)
    for position, limit in max_flex:
        position_cap = solver.Constraint(limit, limit)

        for i, player in enumerate(all_players):
            if position == player.pos:
                position_cap.SetCoefficient(variables[i], 1)

    return variables, solver.Solve()


def run(max_flex, maxed_over, remove, chosen_dict, year, week):
    solver = pywraplp.Solver('FD',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    all_players = []
    if year == CUR_YEAR and week == CUR_WEEK:
        with open('data/DKSalariesCurrent.csv', 'rb') as csvfile:
            csvdata = csv.reader(csvfile, skipinitialspace=True)
            for idx, row in enumerate(csvdata):
                if idx > 0:
                    all_players.append(
                        Player(row[0], generate_pid(row[1], row[0]), row[1], row[2]))
    else:
        for i, row in df[df['Year'] == year][df['Week'] == week].iterrows():
            if not np.isnan(row['Salary']) and row['Salary'] > 0:
                all_players.append(
                    Player(row['Pos'], row['PID'], row['Name'], row['Salary']))
    # give each a ranking
    all_players = sorted(all_players, key=lambda x: x.cost, reverse=True)
    for idx, x in enumerate(all_players):
        x.cost_ranking = idx + 1

    with open('data/%s-Week%s.csv' % (year, week), 'rb') as csvfile:
        csvdata = csv.DictReader(csvfile)
        worked = 0

        for row in csvdata:
            player = filter(lambda x: x.pid in row['playername'], all_players)
            try:
                player[0].proj = float(row['points'])
                player[0].marked = 'Y'
            except:
                pass

    #check_missing_players(all_players, args.sp, args.mp)

    # remove previously optimize
    all_players = filter(lambda x: x.pid not in remove, all_players)

    variables, solution = run_solver(
        solver, all_players, max_flex, chosen_dict)

    if solution == solver.OPTIMAL:
        roster = Roster()

        for i, player in enumerate(all_players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        # print "Optimal roster for: %s" % maxed_over
        # print roster
        return roster
    else:
        raise Exception('No solution error')


if __name__ == "__main__":
        #subprocess.call(['python', 'scraper.py', args.w])
    chosen_dict = {}
    real_scores = []
    for x in xrange(0, int(args.i)):
        max_rosters, rosters, remove = [], [], []
        for max_flex in ALL_LINEUPS.iterkeys():
            rosters.append(
                run(ALL_LINEUPS[max_flex], max_flex, remove, chosen_dict, args.y, args.w))
        max_val = 0
        max_roster = None
        for roster in rosters:
            if roster.projected() > max_val:
                max_val = roster.projected()
                max_roster = roster
                if not (args.w == CUR_WEEK and args.y == CUR_YEAR):
                    for player in max_roster.sorted_players():
                        player.score = float(
                            get_score(player.pid, args.y, args.w))
        print max_roster
        real_scores.append(max_roster.real())
        max_pids = [player.pid for player in max_roster.players]
        chosen_dict[len(chosen_dict)] = max_pids
    print "Median Score: %d" % np.median(real_scores)
    print "Standard Deviation: %d" % np.std(real_scores)
