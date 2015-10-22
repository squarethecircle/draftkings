import requests
import pandas as pd
import sys
import constants
import argparse


ROTOGURU_DST = ['Carolina Defense', 'Seattle Defense', 'New York J Defense', 'Denver Defense', 'Baltimore Defense', 'Miami Defense', 'Tennessee Defense', 'San Francisco Defense', 'St. Louis Defense', 'Detroit Defense', 'New York G Defense', 'Cincinnati Defense', 'Kansas City Defense', 'Buffalo Defense', 'Jacksonville Defense', 'Washington Defense', 'Minnesota Defense', 'Philadelphia Defense', 'Arizona Defense', 'New England Defense', 'San Diego Defense', 'Atlanta Defense', 'Green Bay Defense', 'Houston Defense', 'Dallas Defense', 'Oakland Defense', 'New Orleans Defense', 'Cleveland Defense', 'Pittsburgh Defense', 'Tampa Bay Defense', 'Indianapolis Defense', 'Chicago Defense']

STANDARD_DST = ['Panthers','Seahawks','Jets','Broncos','Ravens','Dolphins','Titans','49ers','Rams','Lions','Giants','Bengals','Chiefs','Bills','Jaguars','Redskins','Vikings','Eagles','Cardinals','Patriots','Chargers','Falcons','Packers','Texans','Cowboys','Raiders','Saints','Browns','Steelers','Buccaneers','Colts','Bears']

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

def grab_history(week):
	r=requests.get('http://rotoguru1.com/cgi-bin/fyday.pl?week=%s&game=dk&scsv=1' % week)
	page = r.text
	start = page.index('<pre>')
	end = page.index('</pre>')
	return page[start+5:end]

def new_dataframe(input):
	new_frame = pd.read_csv(StringIO(input), sep=";")
	new_frame['Week']=pd.to_numeric(new_frame['Week'])
	new_frame['Year']=pd.to_numeric(new_frame['Year'])
	new_frame['DK points']=pd.to_numeric(new_frame['DK points'])
	new_frame['DK salary']=pd.to_numeric(new_frame['DK salary'])
	new_frame['Name'] = new_frame['Name'].apply(name_rearrange)
	new_frame['Name'] = new_frame['Name'].apply(team_rename)
	new_frame['Pos'] = new_frame['Pos'].apply(dst_rename)
	escaped_name = new_frame['Name'].apply(lambda n: n.replace(' ','_'))
	new_frame['PID'] = escaped_name + '_' + new_frame['Pos']
	return new_frame

def name_rearrange(name):
	split = name.split(', ')
	if len(split) > 1:
		return split[1] + ' ' + split[0]
	else:
		return name

def team_rename(name):
	if name in ROTOGURU_DST:
		return STANDARD_DST[ROTOGURU_DST.index(name)]
	else:
		return name

def dst_rename(name):
	if name == "Def":
		return "DST"
	else:
		return name

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-w', type=int, required = True)
	args = parser.parse_args()
	results = []
	for w in range(1,args.w + 1):
		h = grab_history(w)
		results.append(new_dataframe(h))
	df = pd.concat(results)
	df.to_pickle('data/histdata')
	print "Got history for weeks 1-%s" % args.w

