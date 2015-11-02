from optimize import *

year = 2014
numweeks = 15
max_similarity = 5
iterations = 10

total_score = 0
total_dev = 0

for week in range(4, numweeks + 1):
	median_score, std_dev = optimize(week, year, iterations, max_similarity, False)
	total_score += median_score
	total_dev += std_dev
	print "Week %s: (%s,%s)" % (week, median_score, std_dev)


print 'Year: ' + str(year)
print 'Avg Score ' + str(total_score / (numweeks - 3))
print 'Std: ' + str (total_dev / (numweeks - 3))
