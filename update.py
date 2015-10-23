import requests
import pandas as pd
import sys
from constants import *
import argparse
import time


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

def grab_history(week):
	r=requests.get('http://www.rotoguru1.com/cgi-bin/fyday.pl?week=%s&game=dk&scsv=1' % week, timeout=1)
	page = r.text
	start_anchor = '<pre>'
	end_anchor = '</pre>'
	start = page.index(start_anchor)
	end = page.index(end_anchor)
	return page[start+len(start_anchor):end]

def grab_projections(week, pos):
	r=requests.get('http://www.fantasypros.com/nfl/rankings/%s.php?week=%s&export=xls' % (pos, week), timeout=1)
	return r.text.replace('\t\t\n','\n')

def new_history_dataframe(raw_data):
	new_frame = pd.read_csv(StringIO(raw_data), sep=";")
	new_frame['Week']=pd.to_numeric(new_frame['Week'])
	new_frame['Year']=pd.to_numeric(new_frame['Year'])
	new_frame['DK points']=pd.to_numeric(new_frame['DK points'])
	new_frame['DK salary']=pd.to_numeric(new_frame['DK salary'])
	new_frame['Name'] = new_frame['Name'].apply(name_rearrange)
	new_frame['Name'] = new_frame['Name'].apply(lambda t: ROTOGURU_DST_NAMES[t] if t in ROTOGURU_DST_NAMES else t)
	new_frame['Pos'] = new_frame['Pos'].apply(lambda p: 'DST' if p == 'Def' else p)
	new_frame['PID'] = new_frame.apply(lambda row: generate_pid(row['Name'],row['Pos']),axis=1)
	return new_frame

def new_qb_rank_dataframe(raw_data):
	new_frame = pd.read_csv(StringIO(raw_data),sep='\t',
					skipinitialspace=True,header=None,
					names=['Rank','Name','Team','Matchup','Best Rank','Worst Rank','Avg Rank', 'Std Dev'],
					index_col='Rank',skiprows=6,engine='python')
	new_frame['Pos'] = 'QB'
	new_frame['PID'] = new_frame.apply(lambda row: generate_pid(row['Name'],row['Pos']),axis=1)
	return new_frame

def new_flex_rank_dataframe(raw_data):
	new_frame = pd.read_csv(StringIO(raw_data),sep='\t',
				skipinitialspace=True,header=None,
				names=['Rank','Name','Pos','Team','Matchup','Best Rank','Worst Rank','Avg Rank', 'Std Dev'],
				index_col='Rank',skiprows=6,engine='python')
	new_frame['Pos'] = new_frame['Pos'].apply(lambda p: filter(lambda c: str.isalpha(c),p))
	new_frame['PID'] = new_frame.apply(lambda row: generate_pid(row['Name'],row['Pos']),axis=1)
	return new_frame

def new_dst_rank_dataframe(raw_data):
	new_frame = pd.read_csv(StringIO(raw_data),sep='\t',
				skipinitialspace=True,header=None,
				names=['Rank','Name','Team','Matchup','Best Rank','Worst Rank','Avg Rank', 'Std Dev'],
				index_col='Rank',skiprows=6,engine='python')
	new_frame['Pos'] = 'DST'
	new_frame['PID'] = new_frame.apply(lambda row: generate_pid(row['Name'],row['Pos']),axis=1)
	return new_frame

def new_rank_dataframe(raw_data, pos):
	if pos == FP_QB:
		return new_qb_rank_dataframe(raw_data)
	elif pos == FP_FLEX or pos == FP_QBFLEX:
		return new_flex_rank_dataframe(raw_data)
	elif pos == FP_DST:
		return new_dst_rank_dataframe(raw_data)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-w', help="current week", type=int, required = True)
	args = parser.parse_args()
	results = []
	for w in range(1,args.w):
		h = grab_history(w)
		time.sleep(2)
		hf = new_history_dataframe(h)
		for pos in [FP_QB,FP_FLEX,FP_DST]:
			p = grab_projections(w,pos)
			df = new_rank_dataframe(p,pos)
			comb = pd.merge(hf[['DK salary', 'DK points','PID','Pos']],df[['Name','Team',
				'Matchup','Best Rank','Worst Rank','Avg Rank','Std Dev','PID']],on=['PID'])
			comb['Week'] = w
			results.append(comb)
	final_frame = pd.concat(results,ignore_index = True)
	final_frame.to_pickle('data/histdata')
	cur_projs = []
	for pos in [FP_QB,FP_FLEX,FP_DST]:
		p = grab_projections(w + 1,pos)
		df = new_rank_dataframe(p,pos)
		cur_projs.append(df)
	cur_frame = pd.concat(cur_projs, ignore_index = True)
	cur_frame.to_pickle('data/curprojs')
	print "Got history & projections for weeks 1-%s" % args.w
