from optimize import *

year = 2015

numweeks = CUR_WEEK - 1
max_similarity = MAX_SIMILARITY
max_exposure = MAX_EXPOSURE
iterations = ITERATIONS

skip_week = 3
total_score, total_dev = 0, 0

for week in range(numweeks, skip_week, -1):
	median_score, std_dev, scores = optimize(week, year, iterations, max_similarity, max_exposure, False, False)
	total_score += median_score
	total_dev += std_dev
	if week in WINNING_CUTOFFS:
		good_lineups = len(filter(lambda x: x > WINNING_CUTOFFS[week], scores))
		returns = (good_lineups * 0.8 - (iterations - good_lineups)) / iterations
		print "Week %s: %s/%s above cutoff" % (week, good_lineups, iterations)
		print "Return: %s%%" % (returns * 100)
		print "Median, Stdev: (%s, %s)" % (median_score, std_dev)
	else:
		print "Week %s: (%s, %s)" % (week, median_score, std_dev)

	print "Cutoff: %d" % WINNING_CUTOFFS[week] if week in WINNING_CUTOFFS else "No Cutoff data"
	print '----'


print '======'
print 'Year: ' + str(year)
print 'Avg Score ' + str(total_score / (numweeks - skip_week))
print 'Std: ' + str (total_dev / (numweeks - skip_week))