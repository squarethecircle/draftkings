from optimize import *

year = 2015
numweeks = 8
max_similarity = 7
iterations = 10

total_score = 0
total_dev = 0


skip_week = 3

total_score, total_dev = 0, 0

for week in range(skip_week + 1, numweeks + 1):
	median_score, std_dev = optimize(week, year, iterations, max_similarity, False)
	total_score += median_score
	total_dev += std_dev
	print "Week %s: (%s,%s)" % (week, median_score, std_dev)


print 'Year: ' + str(year)
print 'Avg Score ' + str(total_score / (numweeks - skip_week))
print 'Std: ' + str (total_dev / (numweeks - skip_week))