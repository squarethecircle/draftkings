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
warnings.filterwarnings("ignore")


parser = argparse.ArgumentParser()

for opt in OPTIMIZE_COMMAND_LINE:
    parser.add_argument(opt[0], help=opt[1], default=opt[2])

args = parser.parse_args()
MAX_SIMILARITY = int(args.s)
df = pd.read_pickle('data/histdata')
get_score=lambda n,w:df[df['Name'] == n][df['Week']==w]['DK points']


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
        variables.append(solver.IntVar(0, 1, player.name))
      
    objective = solver.Objective()
    objective.SetMaximization()
    for i, player in enumerate(all_players):
        objective.SetCoefficient(variables[i], player.proj)
    salary_cap = solver.Constraint(0, SALARY_CAP)
    for i, player in enumerate(all_players):
        salary_cap.SetCoefficient(variables[i], player.cost)

    was_chosen = lambda r,p: int(r in chosen_dict and p in chosen_dict[r])
    for lineup_num in range(len(chosen_dict)):
        diversity_criterion=solver.Constraint(0,MAX_SIMILARITY)
        for i, player in enumerate(all_players):
            res=was_chosen(lineup_num,player.name)
            diversity_criterion.SetCoefficient(variables[i],res)
    for position, limit in max_flex:
        position_cap = solver.Constraint(0, limit)

        for i, player in enumerate(all_players):
            if position == player.pos:
                position_cap.SetCoefficient(variables[i], 1)

    size_cap = solver.Constraint(ROSTER_SIZE, ROSTER_SIZE)
    for variable in variables:
        size_cap.SetCoefficient(variable, 1)

    return variables, solver.Solve()


def run(max_flex, maxed_over, remove, chosen_dict,week):
    solver = pywraplp.Solver('FD', 
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    all_players = []
    if week == 0:
        with open('data/DKSalariesCurrent.csv', 'rb') as csvfile:
            csvdata = csv.reader(csvfile, skipinitialspace=True)

            for idx, row in enumerate(csvdata):
                if idx > 0:
                    all_players.append(Player(row[0], row[1], row[2]))
    else:
        for i, row in df[df['Week']==week].iterrows():
            if not np.isnan(row['DK salary']) and row['DK salary'] > 0:
                all_players.append(Player(row['Pos'], row['Name'], row['DK salary']))
    # give each a ranking
    all_players = sorted(all_players, key=lambda x: x.cost, reverse=True)
    for idx, x in enumerate(all_players):
        x.cost_ranking = idx + 1

    with open('data/week%d.csv'%(week), 'rb') as csvfile:
        csvdata = csv.DictReader(csvfile)
        worked = 0

        for row in csvdata:
            player = filter(lambda x: x.name in row['playername'], all_players)
            try:
                player[0].proj = float(row['points'])
                player[0].marked = 'Y'
            except:
                pass

    #check_missing_players(all_players, args.sp, args.mp)

    # remove previously optimize
    all_players = filter(lambda x: x.name not in remove, all_players)

    variables, solution = run_solver(solver, all_players, max_flex,chosen_dict)

    if solution == solver.OPTIMAL:
        roster = Roster()

        for i, player in enumerate(all_players):
            if variables[i].solution_value() == 1:
                roster.add_player(player)

        #print "Optimal roster for: %s" % maxed_over
        #print roster
        return roster
    else:
      raise Exception('No solution error')


if __name__ == "__main__":
        #subprocess.call(['python', 'scraper.py', args.w])
    chosen_dict = {}
    for x in xrange(0, int(args.i)):
        max_rosters, rosters, remove = [],[], []
        for max_flex in ALL_LINEUPS.iterkeys():
            rosters.append(run(ALL_LINEUPS[max_flex], max_flex, remove,chosen_dict,int(args.w)))
        max_val = 0
        max_roster = None
        for roster in rosters:
            if roster.projected() > max_val:
                max_val = roster.projected()
                max_roster = roster
        print max_roster
        score = 0
        if int(args.w) > 0:
            for player in max_roster.sorted_players():
                player_score = get_score(player.name,int(args.w))
                if len(player_score) > 0:
                    print player.name+": "+str(float(player_score))
                    score += float(player_score)
                else:
                    print player.name+": DID NOT PLAY"
            print "REAL SCORE: " + str(score) + '\n'
        max_names = [player.name for player in max_roster.players]
        chosen_dict[len(chosen_dict)] = max_names



