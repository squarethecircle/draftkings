from bs4 import BeautifulSoup
import datetime
from abbreviations import *
import string

date_format = '%d %b %Y'

weeks = {
	1: ['10 Sep 2015', '15 Sep 2015'],
	2: ['17 Sep 2015', '22 Sep 2015'],
	3: ['24 Sep 2015', '29 Sep 2015'],
	4: ['01 Oct 2015', '06 Oct 2015'],
	5: ['08 Oct 2015', '13 Oct 2015'],
	6: ['15 Oct 2015', '20 Oct 2015'],
	7: ['22 Oct 2015', '27 Oct 2015'],
	8: ['29 Oct 2015', '03 Nov 2015'],
	9: ['05 Nov 2015', '10 Nov 2015'],
	10: ['12 Nov 2015', '17 Nov 2015'],
	11: ['19 Nov 2015', '24 Nov 2015'],
	12: ['26 Nov 2015', '30 Nov 2015']
}
conv_d = {}
for (w, r) in weeks.items():
	beg = datetime.datetime.strptime(r[0], date_format)
	end = datetime.datetime.strptime(r[1], date_format)
	conv_d[(beg,end)] = w

def get_week(d):
	for r, w in conv_d.items():
		if d >= r[0] and d <= r[1]:
			return w
	return False

content = {}

cur_week = None

def extract(filename):
	f = open(filename, 'r')
	text = f.read()
	soup = BeautifulSoup(text)
	table = soup.select('tbody')[0]
	
	for row in table.select('tr'):

		if 'dark' in row['class'] or 'table-dummyrow' in row['class']:
			continue

		##date
		if 'center' in row['class'] and 'nob-border' in row['class']:
			date = row.select('.datet')[0].text
			formatted_date = datetime.datetime.strptime(date, date_format)
			cur_week = get_week(formatted_date)
			if cur_week not in content:
				content[cur_week] = []


		##match
		if 'deactivate' in row['class'] or ' deactivate' in row['class']:
			matchup = row.select('.table-participant')[0].text.split(' - ')
			matchup = [filter(lambda x: x in string.printable, i) for i in matchup]
			score = row.select('.table-score')[0].text
			odds_one = row.select('.odds-nowrp')[0].text
			odds_two = row.select('.odds-nowrp')[1].text
			content[cur_week].append([matchup, odds_one, odds_two, score])

ODDS_DIFFERENCE_THRESHOLD = 1.5

def get_w_l():
	paths = ['odds_data/' + str(i) + '.txt' for i in range(1, 5)]

	for p in paths:
		extract(p)
	w_l_table = {}

	for w, v in content.items():
		for match in v:
			if w not in w_l_table:
				w_l_table[w] = {}
			t1 = ABBREVIATIONS[match[0][0]]
			t2 = ABBREVIATIONS[match[0][1]]
			w_l_table[w][t1], w_l_table[w][t2] = True, True
			if float(match[1]) - float(match[2]) > ODDS_DIFFERENCE_THRESHOLD:
				w_l_table[w][t1] = False
			elif float(match[2]) - float(match[1]) > ODDS_DIFFERENCE_THRESHOLD:
				w_l_table[w][t2] = False
	return w_l_table

if __name__ == '__main__':
	print get_w_l()

	# print content
