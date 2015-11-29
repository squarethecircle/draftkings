from abbreviations import *

CUR_WEEK = 12
CUR_YEAR = 2015
MAX_SIMILARITY = 7
ITERATIONS = 15
MAX_EXPOSURE = 14

WINNING_CUTOFFS = {
  11: 105,
  10: 121,
  9: 173, 
  8: 147,
  7: 167,
}

### don't pick these players because of injury
INJURY_LIST = {
  (2015, 10): ['ALSHON_JEFFERY_WR']
}

FFPRO = 'http://www.fantasypros.com/nfl/projections/'

ALL_POS = ['QB', 'RB', 'WR', 'TE', 'DST']
ALL_POS_TEAM = ['QB', 'RB1', 'RB2',
                'WR1', 'WR2', 'WR3', 'FLEX',
                'TE', 'DST']

SALARY_CAP = 50000

POSITION_LIMITS_WR_MAX = [
    ["QB", 1],
    ["RB", 2],
    ["WR", 4],
    ["TE", 1],
    ["DST",  1]
]

POSITION_LIMITS_RB_MAX = [
    ["QB", 1],
    ["RB", 3],
    ["WR", 3],
    ["TE", 1],
    ["DST",  1]
]

POSITION_LIMITS_TE_MAX = [
    ["QB", 1],
    ["RB", 2],
    ["WR", 3],
    ["TE", 2],
    ["DST",  1]
]

ALL_LINEUPS = {
    'WR_MAX': POSITION_LIMITS_WR_MAX,
    'RB_MAX': POSITION_LIMITS_RB_MAX,
    'TE_MAX': POSITION_LIMITS_TE_MAX
}

# only works for int options
OPTIMIZE_COMMAND_LINE = [
    ['-w', 'week of season', CUR_WEEK],
    ['-y', 'year of season', CUR_YEAR],
    ['-s', 'max similarity', MAX_SIMILARITY],
    ['-i', 'iterations to run', ITERATIONS],
    ['-e', 'exposure to player - max avg points per game', MAX_EXPOSURE],
    ['-o', 'use odds', False]
]

RT_YEAR = {2015: 'dk', 2014: 'dk', 2013: 'fd', 2012: 'fd', 2011: 'fd'}
FP_FLEX = 'ppr-flex'
FP_QBFLEX = 'ppr-qb-flex'
FP_QB = 'qb'
FP_DST = 'dst'

PROJECTION_TYPE = {FP_FLEX: ['WR', 'RB', 'TE'], FP_QBFLEX: [
    'QB', 'WR', 'RB', 'TE'], FP_QB: ['QB'], FP_DST: ['DST']}

# standardizing names in this way matches 2-4 more people per week
# in the dataset that otherwise would be key mismatches


def clean_name(nm):
    raw = nm.upper().replace('.', '').replace(' JR', '').replace(' SR', '')\
            .replace(' III', '').strip()
    raw = filter(lambda q: str.isalnum(q) or str.isspace(q), raw)
    nsec = raw.split(' ')
    nsec[0] = nsec[0].replace('CHRISTOPHER', 'CHRIS')\
        .replace('MATTHEW', 'MATT')\
        .replace('DANIEL', 'DAN')\
        .replace('MICHAEL', 'MIKE')\
        .replace('BENJAMIN', 'BEN')\
        .replace('STEVIE', 'STEVE')
    return ' '.join(nsec)


def generate_pid(name, pos):
    dst_replace = lambda t: FANPROS_DST_NAMES[
        t] if t in FANPROS_DST_NAMES else t
    escape = lambda n: filter(lambda q: str.isalnum(q) or str.isspace(q), n)
    underscore = lambda n: n.replace(' ', '_')
    return (underscore(clean_name(escape(dst_replace(name)))) + '_' + pos).upper()
