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

FP_FLEX = 'ppr-flex'
FP_QBFLEX = 'ppr-qb-flex'
FP_QB = 'qb'
FP_DST = 'dst'

PROJECTION_TYPE = {FP_FLEX: ['WR','RB','TE'], FP_QBFLEX: ['QB','WR','RB','TE'], FP_QB: ['QB'], FP_DST:['DST']}

ROTOGURU_DST_NAMES = {'Detroit Defense': 'Lions', 'New York G Defense': 'Giants', 'New York J Defense': 'Jets', 
'Jacksonville Defense': 'Jaguars', 'Buffalo Defense': 'Bills', 'Seattle Defense': 'Seahawks', 
'Denver Defense': 'Broncos', 'Indianapolis Defense': 'Colts', 'Tampa Bay Defense': 'Buccaneers', 
'Arizona Defense': 'Cardinals', 'Green Bay Defense': 'Packers', 'Tennessee Defense': 'Titans', 
'Cincinnati Defense': 'Bengals', 'San Francisco Defense': '49ers', 'New Orleans Defense': 'Saints', 
'Washington Defense': 'Redskins', 'Oakland Defense': 'Raiders', 'Carolina Defense': 'Panthers', 
'New England Defense': 'Patriots', 'Kansas City Defense': 'Chiefs', 'Minnesota Defense': 'Vikings', 
'Chicago Defense': 'Bears', 'Pittsburgh Defense': 'Steelers', 'Philadelphia Defense': 'Eagles', 
'San Diego Defense': 'Chargers', 'Miami Defense': 'Dolphins', 'Baltimore Defense': 'Ravens', 
'Houston Defense': 'Texans', 'Dallas Defense': 'Cowboys', 'St. Louis Defense': 'Rams', 
'Atlanta Defense': 'Falcons', 'Cleveland Defense': 'Browns'}

FANPROS_DST_NAMES = {'Detroit Lions': 'Lions', 'New York Giants': 'Giants', 'New York Jets': 'Jets', 
'Jacksonville Jaguars': 'Jaguars', 'Buffalo Bills': 'Bills', 'Seattle Seahawks': 'Seahawks', 
'Denver Broncos': 'Broncos', 'Indianapolis Colts': 'Colts', 'Tampa Bay Buccaneers': 'Buccaneers', 
'Arizona Cardinals': 'Cardinals', 'Green Bay Packers': 'Packers', 'Tennessee Titans': 'Titans', 
'Cincinnati Bengals': 'Bengals', 'San Francisco 49ers': '49ers', 'New Orleans Saints': 'Saints', 
'Washington Redskins': 'Redskins', 'Oakland Raiders': 'Raiders', 'Carolina Panthers': 'Panthers', 
'New England Patriots': 'Patriots', 'Kansas City Chiefs': 'Chiefs', 'Minnesota Vikings': 'Vikings', 
'Chicago Bears': 'Bears', 'Pittsburgh Steelers': 'Steelers', 'Philadelphia Eagles': 'Eagles', 
'San Diego Chargers': 'Chargers', 'Miami Dolphins': 'Dolphins', 'Baltimore Ravens': 'Ravens', 
'Houston Texans': 'Texans', 'Dallas Cowboys': 'Cowboys', 'St. Louis Rams': 'Rams', 
'Atlanta Falcons': 'Falcons', 'Cleveland Browns': 'Browns'}

# standardizing names in this way matches 2-4 more people per week
# in the dataset that otherwise would be key mismatches
def clean_name(nm):
    raw = nm.upper().replace('.', '').replace(' JR', '').replace(' SR', '')\
            .replace(' III', '').strip()
    nsec = raw.split(' ')
    nsec[0] = nsec[0].replace('CHRISTOPHER', 'CHRIS')\
            .replace('MATTHEW', 'MATT')\
            .replace('DANIEL', 'DAN')\
            .replace('MICHAEL', 'MIKE')\
            .replace('BENJAMIN', 'BEN')
    return ' '.join(nsec)

def generate_pid(name, pos):
  dst_replace = lambda t: FANPROS_DST_NAMES[t] if t in FANPROS_DST_NAMES else t
  escape = lambda n: filter(lambda q: str.isalnum(q) or str.isspace(q),n)
  underscore = lambda n: n.replace(' ','_')
  return (underscore(clean_name(escape(dst_replace(name))))+'_'+pos).upper()
