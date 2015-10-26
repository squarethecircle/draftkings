import re
import sys
import os

teams_dict = { "DALLAS":"COWBOYS",
        "MINNESOTA":"VIKINGS",
        "SAN FRANCISCO":"49ERS",
        "NEW ORLEANS":"SAINTS",
        "CAROLINA":"PANTHERS",
        "INDIANAPOLIS":"COLTS",
        "TAMPA BAY":"BUCCANEERS",
        "PITTSBURGH":"STEELERS",
        "NEW ENGLAND":"PATRIOTS",
        "SAN DIEGO":"CHARGERS",
        "TENNESSEE":"TITANS",
        "ATLANTA":"FALCONS",
        "JACKSONVILLE":"JAGUARS",
        "MIAMI":"DOLPHINS",
        "KANSAS CITY":"CHIEFS",
        "DETROIT":"LIONS",
        "PHILADELPHIA":"EAGLES",
        "ARIZONA":"CARDINALS",
        "BUFFALO":"BILLS",
        "BALTIMORE":"RAVENS",
        "ST LOUIS":"RAMS",
        "HOUSTON":"TEXANS",
        "OAKLAND":"RAIDERS",
        "WASHINGTON":"REDSKINS",
        "NEW YORK":"JETS",
        "CLEVELAND":"BROWNS",
        "CINCINNATI":"BENGALS",
        "DENVER":"BRONCOS",
        "NEW YORK J":"JETS",
        "NEW YORK G":"GIANTS",
        "CHICAGO":"BEARS",
        "GREEN BAY":"PACKERS",
        "SEATTLE":"SEAHAWKS" }

def clean_name(nm):
    raw = nm.upper().replace('.', '').replace(' JR', '').replace(' SR', '')\
            .replace(' III', '').strip()
    nsec = raw.split(' ')
    nsec[0] = nsec[0].replace('CHRISTOPHER', 'CHRIS')\
            .replace('MATTHEW', 'MATT')\
            .replace('DANIEL', 'DAN')\
            .replace('BENJAMIN', 'BEN')
    return ' '.join(nsec)

class PlayerRecord:
    def __init__(self):
        self.rec_ID=None
        self.player_ID=None
        self.name=None
        self.pos=None
        self.year=0
        self.week=0
        self.dk_score=0
        self.dk_salary=0
        self.team=None
        self.opp=None
        self.fp_avg_rank = -1
    def add_dk(self, dkstr):
        sec = dkstr.split(';')
        if len(sec) >= 10 and sec.count('') == 0:
            namesec = sec[3].split(', ')
            self.name= clean_name(namesec[1]+' '+namesec[0]) if ', ' in sec[3]\
                    else teams_dict[clean_name(' '.join(sec[3].split(' ')[:-1]))]
            self.pos='DST' if sec[4] == 'Def' else sec[4].upper()
            self.player_ID=self.name.replace(' ', '_') + '_' + self.pos
            self.year=int(sec[1])
            self.week=int(sec[0])
            self.team=sec[5].upper()
            self.opp=sec[7].upper()
            self.dk_score=float(sec[8])
            self.dk_salary=int(sec[9])
            self.rec_ID='{}_{}_{}'.format(self.year, self.week, self.player_ID).upper()
    def add_fp(self, fpstr, fpfn):
        self.fp_avg_rank = process_fp(fpstr, fpfn)[1]
    def add_dksal(self, dksalstr, dkfn):
        sec = dksalstr.split(',')
        fnsec = dkfn.split('.')[0].split('_')
        self.name=clean_name(sec[1])
        self.pos=sec[0].upper()
        self.player_ID = self.name.replace(' ', '_') + '_' + self.pos
        self.year=int(fnsec[1])
        self.week=int(fnsec[2])
        self.team=sec[5].upper()
        tsec = sec[3].upper().split(' ')[0].split('@')
        self.opp = tsec[0] if tsec[1] == self.team else tsec[1]
        self.dk_score=0
        self.dk_salary=int(sec[2])
        self.rec_ID='{}_{}_{}'.format(self.year, self.week, self.player_ID).upper()

def process_fp(fpstr, fn):
    fnsec = fn.split('_')
    sec = fpstr.split('\t')
    adj = 0
    if fnsec[4] == 'DST':
        pn = sec[1].split(' ')[-1].upper()
        pos = 'DST'
    elif fnsec[4] == 'QB':
        pn = clean_name(sec[1])
        pos = 'QB'
    else:
        pn = clean_name(sec[1])
        pos = re.sub('\d', '', sec[2])
        adj = 1
    rec_ID = '{}_{}_{}_{}'.format(fnsec[1], fnsec[3], pn.replace(' ', '_'), pos)
    return rec_ID, sec[6+adj]

def proc_data(dn):
    records_dict = {}
    for fn in [f for f in os.listdir(dn) if 'draftkings' in f]:
        for line in open(os.path.join(dn, fn), 'r').readlines():
            if ';' in line:
                rec = PlayerRecord()
                rec.add_dk(line.strip())
                if rec.rec_ID is not None:
                    records_dict[rec.rec_ID] = rec
    for fn in [f for f in os.listdir(dn) if 'DKSalaries' in f]:
        for line in open(os.path.join(dn, fn), 'r').readlines():
            if 'GameInfo' in line:
                continue
            fnsec = fn.split('.')[0].split('_')
            sec = line.replace('"', '').split(',')
            rec_ID = '{}_{}_{}_{}'.format(fnsec[1], fnsec[2],
                    clean_name(sec[1]).replace(' ', '_'), sec[0])
            if rec_ID not in records_dict:
                rec = PlayerRecord()
                rec.add_dksal(line.replace('"','').strip(), fn)
                records_dict[rec_ID] = rec
    for fn in [f for f in os.listdir(dn) if 'xls' in f]:
        for line in open(os.path.join(dn, fn), 'r').readlines():
            if line[0].isdigit():
                ID = process_fp(line, fn)[0]
                if ID in records_dict:
                    records_dict[ID].add_fp(line, fn)
    return records_dict.values()
