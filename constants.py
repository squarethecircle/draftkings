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
    'WR_MAX' : POSITION_LIMITS_WR_MAX,
    'RB_MAX' : POSITION_LIMITS_RB_MAX,
    'TE_MAX': POSITION_LIMITS_TE_MAX
}

OPTIMIZE_COMMAND_LINE = [
  ['-w', 'week of season', 1],
  ['-s', 'max similarity', 5],
  ['-i', 'iterations to run', 3]
]


