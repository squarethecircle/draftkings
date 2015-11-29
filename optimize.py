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
import odds_analyzer

warnings.filterwarnings("ignore")
pd.set_option('display.width', 400)

parser = argparse.ArgumentParser()

for opt in OPTIMIZE_COMMAND_LINE:
    parser.add_argument(opt[0], help=opt[1], default=opt[2], type=int)

args = parser.parse_args()

df = pd.read_pickle('data/histdata')
odds_dict = odds_analyzer.get_w_l()

get_score = lambda n, y, w: df[df['PID'] == n][
    df['Year'] == y][df['Week'] == w]['Points']

def run_solver(solver, all_players, year, week, max_flex, chosen_dict, max_similarity, exposure, max_exposure):
    '''
    handle or-tools logic
    '''
    variables = []

    

    # ineligible list of players, hit max exposure
    ineligible = set(filter(lambda x: x.pid in exposure and exposure[x.pid][1] >= max_exposure, all_players))

    for player in all_players:
        team = player.team
        if player.team == 'FA':
            winning = False
        elif team in odds_dict[week]:
            winning = odds_dict[week][team]
        else:
            winning = True
            
        if player in ineligible or not winning:
            variables.append(solver.IntVar(0, 0, player.pid))
        else:
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
        diversity_criterion = solver.Constraint(0, max_similarity)
        for i, player in enumerate(all_players):
            res = was_chosen(lineup_num, player.pid)
            diversity_criterion.SetCoefficient(variables[i], res)

    for position, limit in max_flex:
        position_cap = solver.Constraint(limit, limit)

        for i, player in enumerate(all_players):
            if position == player.pos:
                position_cap.SetCoefficient(variables[i], 1)

    return variables, solver.Solve()


def run(max_flex, maxed_over, remove, chosen_dict, year, week, max_similarity, exposure, max_exposure):
    solver = pywraplp.Solver('FD',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    all_players = []
    if year == CUR_YEAR and week == CUR_WEEK:
        with open('data/DKSalariesCurrent.csv', 'rb') as csvfile:
            csvdata = csv.reader(csvfile, skipinitialspace=True)
            for idx, row in enumerate(csvdata):
                if idx > 0:
                    all_players.append(
                        Player(row[0], generate_pid(row[1], row[0]), row[1], row[2], DK_TO_PD[row[-1]]))
    else:
        for i, row in df[df['Year'] == year][df['Week'] == week].iterrows():
            if not np.isnan(row['Salary']) and row['Salary'] > 0:
                all_players.append(
                    Player(row['Pos'], row['PID'], row['Name'], row['Salary'], row['Team']))
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
                if float(row['points']) > 5:
                    player[0].proj = float(row['points'])
                else:
                    player[0].proj = float(0)
                player[0].marked = 'Y'
            except:
                pass

    # remove previously optimize
    all_players = filter(lambda x: x.pid not in remove, all_players)

    variables, solution = run_solver(
        solver, all_players, year, week, max_flex, chosen_dict, max_similarity, exposure, max_exposure)

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

def update_exposure(exposure, roster):
    for p in roster.players:
        if p.pid in exposure:
            exposure[p.pid][0] += 1
            exposure[p.pid][1] += p.proj
        else:
            exposure[p.pid] = [1, p.proj]

def print_exposure(exposure):
    print '===='
    for p in sorted(exposure.items(), key=lambda x: x[1], reverse=True):
        print "{0: <20}({1} picks, {2} score)".format(p[0], str(p[1][0]), str(p[1][1]))

def optimize(week = args.w, year = args.y, iterations = args.i, max_similarity = args.s, \
                max_exposure = args.e, print_terminal = True):
    chosen_dict = {}
    exposure = {} ## key: pid, val = [num picks, total proj_score]
    real_scores = []
    for x in xrange(0, int(iterations)):
        max_rosters, rosters, remove = [], [], []
        if (year, week) in INJURY_LIST:
            remove = remove + INJURY_LIST[(year,week)]

        for max_flex in ALL_LINEUPS.iterkeys():
            rosters.append(
                run(ALL_LINEUPS[max_flex], max_flex, remove, chosen_dict, year, week, max_similarity,\
                     exposure, max_exposure * iterations))
        max_val = 0
        max_roster = None
        for roster in rosters:
            if roster.projected() > max_val:
                max_val = roster.projected()
                max_roster = roster
                if not (week == CUR_WEEK and year == CUR_YEAR):
                    for player in max_roster.sorted_players():
                        player.score = float(
                            get_score(player.pid, year, week))
        if print_terminal:
            print max_roster

        update_exposure(exposure, max_roster)
        real_scores.append(max_roster.real())
        max_pids = [player.pid for player in max_roster.players]
        chosen_dict[len(chosen_dict)] = max_pids

    median_score = np.median(real_scores)
    std_dev = np.std(real_scores)
    if print_terminal:
        print "Median Score: %d" % median_score
        print "Standard Deviation: %d" % std_dev
        print_exposure(exposure)

    return (median_score, std_dev, real_scores)

if __name__ == "__main__":
    optimize()
