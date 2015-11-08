import requests
import pandas as pd
import sys
from constants import *
import argparse
import time
import numpy as np
import pdb

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


def name_rearrange(name):
    split = name.split(', ')
    if len(split) > 1:
        return split[1] + ' ' + split[0]
    else:
        return name


def set_first_zero(arr):
    arr[0] = 0
    return arr

DISCOUNT_RATE = 0.2
def calc_ppg(final_frame):
    sort_frame = final_frame.sort_values(['PID', 'Year', 'Week'])
    sort_frame['Total Points'] = 0
    sort_frame['Total Discounted Points'] = 0
    sort_frame['# Games'] = 0
    last_pid = None
    last_year = None
    last_pts = 0
    last_games = 0
    for index, row in sort_frame.iterrows():
        if row['PID'] == last_pid and row['Year'] == last_year:
            sort_frame.loc[index, 'Total Points'] = last_pts
            sort_frame.loc[index, 'Total Discounted Points'] = discounted_points
            sort_frame.loc[index, '# Games'] = last_games + 1
        last_pid = sort_frame.loc[index, 'PID']
        last_year = sort_frame.loc[index, 'Year']
        last_pts = sort_frame.loc[
            index, 'Total Points'] + sort_frame.loc[index, 'Points']
        discounted_points = sort_frame.loc[
            index, 'Total Discounted Points'] * DISCOUNT_RATE + sort_frame.loc[index, 'Points']
        last_games = sort_frame.loc[index, '# Games']
    sort_frame['PPG'] = sort_frame['Total Points'] / sort_frame['# Games']
    sort_frame['D_PPG'] = sort_frame['Total Discounted Points'] / (((1-(DISCOUNT_RATE**sort_frame['# Games']))/(1-DISCOUNT_RATE)))
    return sort_frame


def safe_get(url):
    sleep_time = 4
    while True:
        try:
            r = requests.get(url, timeout=1)
            break
        except:
            print "Got blocked!  Retrying"
            time.sleep(sleep_time)
            sleep_time *= 2
    return r.text


def grab_history(week, year):
    url = 'http://www.rotoguru1.com/cgi-bin/fyday.pl?week=%s&year=%s&game=%s&scsv=1' % (
        week, year, RT_YEAR[year])
    print url
    page = safe_get(url)
    start_anchor = '<pre>'
    end_anchor = '</pre>'
    start = page.index(start_anchor)
    end = page.index(end_anchor)
    return page[start + len(start_anchor):end]


def grab_projections(week, year, pos):
    if year < CUR_YEAR:
        url = 'http://www.fantasypros.com/nfl/rankings/%s.php?week=%s&year=%s&export=xls' % (
            pos, week, year)
    else:
        url = 'http://www.fantasypros.com/nfl/rankings/%s.php?week=%s&export=xls' % (
            pos, week)
    print url
    return safe_get(url).replace('\t\t\n', '\n')


def new_history_dataframe(raw_data):
    new_frame = pd.read_csv(StringIO(raw_data), sep=";", dtype=np.dtype(str), names=[
                            'Week', 'Year', 'GID', 'Name', 'Pos', 'Team', 'h/a', 'Oppt', 'Points', 'Salary'], skiprows=1)
    new_frame['Week'] = pd.to_numeric(new_frame['Week'])
    new_frame['Year'] = pd.to_numeric(new_frame['Year'])
    new_frame['Points'] = pd.to_numeric(new_frame['Points'])
    new_frame['Salary'] = pd.to_numeric(new_frame['Salary'])
    new_frame = new_frame[new_frame['GID'] != 'ERR0']
    new_frame['Name'] = new_frame['Name'].apply(name_rearrange)
    new_frame['Name'] = new_frame['Name'].apply(
        lambda t: ROTOGURU_DST_NAMES[t] if t in ROTOGURU_DST_NAMES else t)
    new_frame['Pos'] = new_frame['Pos'].apply(
        lambda p: 'DST' if p == 'Def' else p)
    new_frame['PID'] = new_frame.apply(
        lambda row: generate_pid(row['Name'], row['Pos']), axis=1)
    return new_frame


def new_qb_rank_dataframe(raw_data):
    new_frame = pd.read_csv(StringIO(raw_data), sep='\t',
                            skipinitialspace=True, header=None,
                            names=['Rank', 'Name', 'Team', 'Matchup',
                                   'Best Rank', 'Worst Rank', 'Avg Rank', 'Std Dev'],
                            index_col='Rank', skiprows=6, engine='python')
    new_frame['Pos'] = 'QB'
    new_frame['PID'] = new_frame.apply(
        lambda row: generate_pid(row['Name'], row['Pos']), axis=1)
    return new_frame


def new_flex_rank_dataframe(raw_data):
    new_frame = pd.read_csv(StringIO(raw_data), sep='\t',
                            skipinitialspace=True, header=None,
                            names=['Rank', 'Name', 'Pos', 'Team', 'Matchup',
                                   'Best Rank', 'Worst Rank', 'Avg Rank', 'Std Dev'],
                            index_col='Rank', skiprows=6, engine='python')
    new_frame['Pos'] = new_frame['Pos'].apply(
        lambda p: filter(lambda c: str.isalpha(c), p))
    new_frame['PID'] = new_frame.apply(
        lambda row: generate_pid(row['Name'], row['Pos']), axis=1)
    return new_frame


def new_dst_rank_dataframe(raw_data):
    new_frame = pd.read_csv(StringIO(raw_data), sep='\t',
                            skipinitialspace=True, header=None,
                            names=['Rank', 'Name', 'Team', 'Matchup',
                                   'Best Rank', 'Worst Rank', 'Avg Rank', 'Std Dev'],
                            index_col='Rank', skiprows=6, engine='python')
    new_frame['Pos'] = 'DST'
    new_frame['PID'] = new_frame.apply(
        lambda row: generate_pid(row['Name'], row['Pos']), axis=1)
    return new_frame


def new_rank_dataframe(raw_data, pos):
    if pos == FP_QB:
        return new_qb_rank_dataframe(raw_data)
    elif pos == FP_FLEX or pos == FP_QBFLEX:
        return new_flex_rank_dataframe(raw_data)
    elif pos == FP_DST:
        return new_dst_rank_dataframe(raw_data)


def get_history_projections(year, week):
    h = grab_history(week, year)
    hf = new_history_dataframe(h)
    results = []
    for pos in [FP_QB, FP_FLEX, FP_DST]:
        p = grab_projections(week, year, pos)
        df = new_rank_dataframe(p, pos)
        comb = pd.merge(hf[['Salary', 'Points', 'PID', 'Pos']], df[['Name', 'Team',
                                                                    'Matchup', 'Best Rank', 'Worst Rank', 'Avg Rank', 'Std Dev', 'PID']], on=['PID'])
        comb['Week'] = week
        comb['Year'] = year
        results.append(comb)
    return pd.concat(results, ignore_index=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', help="current week", type=int, required=True)
    parser.add_argument('-a', help="download all", action='store_true')
    args = parser.parse_args()
    results = []
    if args.a:
        for y in range(2011, CUR_YEAR + 1):
            max_week = 16
            if y == CUR_YEAR:
                max_week = args.w - 1
            for w in range(1, max_week):
                results.append(get_history_projections(y, w))
            hist_frame = pd.concat(results, ignore_index=True)
        hist_frame.to_pickle('data/histdata')
    hist_frame = pd.read_pickle('data/histdata')
    recent_results = get_history_projections(CUR_YEAR, args.w - 1)
    hist_frame = pd.concat([hist_frame, recent_results], ignore_index=True).drop_duplicates(
        ['PID', 'Year', 'Week'], keep='last')
    cur_projs = []
    for pos in [FP_QB, FP_FLEX, FP_DST]:
        p = grab_projections(args.w, CUR_YEAR, pos)
        df = new_rank_dataframe(p, pos)
        cur_projs.append(df)
    cur_frame = pd.concat(cur_projs, ignore_index=True)
    cur_frame['Week'] = args.w
    cur_frame['Year'] = CUR_YEAR
    final_frame = pd.concat([hist_frame, cur_frame], ignore_index=True).drop_duplicates(
        ['PID', 'Year', 'Week'], keep='last')
    final_frame = calc_ppg(final_frame)
    final_frame['Variance'] = final_frame.groupby(['PID'])['Points'].var() / (final_frame.groupby(['PID'])['Points'].mean() ** 2)

    cur_frame.to_pickle('data/curprojs')
    final_frame.to_pickle('data/histdata')

    if args.a:
        print "Got all historical data"
    else:
        print "Got history & projections for week %s" % args.w
