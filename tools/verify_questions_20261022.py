"""Independent executable checks for the six 2026-10-22 questions.

Run from the repository root. Uses only the Python standard library; SQLite
checks the SQL subset shared with PostgreSQL. PostgreSQL semantics are also
linked in each question's answer details.
"""
import collections
import itertools
import json
import random
import sqlite3
from fractions import Fraction
from pathlib import Path
from statistics import NormalDist

all_questions = json.loads(Path('questions.json').read_text())
new = {q['id']: q for q in all_questions if q['id'].startswith('dsj-20261022-')}
assert len(new) == 6
assert len({q['id'] for q in all_questions}) == len(all_questions)
required = {'id','topic','sub','difficulty','title','prompt','ai','verdict','fix',
            'lang','track','model','mech','breaks','contrast','details','why','bug'}
for q in new.values():
    assert required <= q.keys()
    assert q['difficulty'] == 'Hard'
    assert (q['topic'], q['track'], q['lang']) in {
        (p['topic'], p['track'], p['lang']) for p in all_questions if p not in new.values()
    }
    if q['verdict'] == 'correct':
        assert q['bug'] == '' and 'flaws' not in q
    else:
        assert q['bug'] and len(q['flaws']) == 4 and len(set(q['flaws'])) == 4
        lengths = list(map(len, q['flaws']))
        assert (max(lengths)-min(lengths))/max(lengths) <= .15
        print(q['id'], 'flaw lengths', lengths)
assert collections.Counter(q['verdict'] for q in new.values()) == {'correct':3,'wrong':3}
text = Path('index.html').read_text()
start = text.index('const Q=')+len('const Q=')
end = text.index(';\nconst QI=', start)
assert json.loads(text[start:end]) == all_questions
assert "${fresh?'':`<span class=\"tag\">${esc(q.sub)}</span>`}" in text

con = sqlite3.connect(':memory:')
q = new['dsj-20261022-sql-01']
con.execute('CREATE TABLE sessions(interval_id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL, start_min INTEGER NOT NULL, end_min INTEGER NOT NULL)')
rows = [(1,1,0,10),(2,1,2,3),(3,1,4,5),(4,1,12,13)]
con.executemany('INSERT INTO sessions VALUES (?,?,?,?)', rows)
assert con.execute(q['ai']).fetchall() == [(1,0,10),(1,4,5),(1,12,13)]
assert con.execute(q['fix']).fetchall() == [(1,0,10),(1,12,13)]
# Oracle: direct interval union; not the SQL window algorithm.
def union_oracle(rows):
    out=[]
    for account in sorted({r[1] for r in rows}):
        merged=[]
        for _,_,a,b in sorted((r for r in rows if r[1]==account), key=lambda r:(r[2],r[0])):
            if merged and a <= merged[-1][1]:
                merged[-1][1]=max(merged[-1][1],b)
            else:
                merged.append([a,b])
        out.extend((account,a,b) for a,b in merged)
    return out
rng=random.Random(20261022)
for _ in range(200):
    rows=[]
    for i in range(rng.randrange(40)):
        a=rng.randrange(30)
        rows.append((i,rng.randrange(3),a,a+rng.randrange(1,15)))
    con.execute('DELETE FROM sessions')
    con.executemany('INSERT INTO sessions VALUES (?,?,?,?)',rows)
    assert con.execute(q['fix']).fetchall()==union_oracle(rows)
print('Interval union: AI counterexample and 200 corrected-query oracle cases passed')

q=new['dsj-20261022-sql-02']
con.executescript('CREATE TABLE accounts(account_id INTEGER PRIMARY KEY); CREATE TABLE required_features(feature TEXT PRIMARY KEY NOT NULL); CREATE TABLE usage_events(account_id INTEGER NOT NULL, feature TEXT NOT NULL); INSERT INTO accounts VALUES(1),(2),(3);')
# Every requirement subset and every account-feature coverage pattern, with repeats.
for required in [[],['a'],['b'],['a','b']]:
    con.execute('DELETE FROM required_features')
    con.executemany('INSERT INTO required_features VALUES(?)',[(x,) for x in required])
    for mask in range(64):
        coverage={(a,f) for i,(a,f) in enumerate(itertools.product([1,2,3],['a','b'])) if mask & (1<<i)}
        con.execute('DELETE FROM usage_events')
        con.executemany('INSERT INTO usage_events VALUES(?,?)', list(coverage)*2+[(3,'c')])
        expected=[(a,) for a in [1,2,3] if set(required) <= {f for acct,f in coverage if acct==a}]
        assert con.execute(q['ai']).fetchall()==expected
print('Feature coverage: all 256 requirement/coverage combinations passed')

q=new['dsj-20261022-sql-03']
con.execute('CREATE TABLE edges(src INTEGER NOT NULL,dst INTEGER NOT NULL)')
con.executemany('INSERT INTO edges VALUES(?,?)',[(1,2),(1,2),(2,3),(3,2),(3,4),(5,5)])
assert con.execute(q['ai']).fetchall()==[(1,),(2,),(3,),(4,)]
# All directed graphs on three nodes, including self-loops; duplicate every edge.
possible=list(itertools.product(range(1,4),repeat=2))
for mask in range(512):
    edges=[e for i,e in enumerate(possible) if mask & (1<<i)]
    seen=set(); pending=[1]
    while pending:
        node=pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(b for a,b in edges if a==node)
    con.execute('DELETE FROM edges')
    con.executemany('INSERT INTO edges VALUES(?,?)',edges*2)
    assert con.execute(q['ai']).fetchall()==[(x,) for x in sorted(seen)]
print('Reachability: sample and all 512 three-node directed graphs passed')

# Integrate remaining wait by equally spaced midpoint observations over clock time.
waits=[]
for i in range(20000):
    t=Fraction(2*i+1,2000)
    waits.append((2 if t<2 else 20)-t)
assert sum(waits)/len(waits)==Fraction(41,5)
assert Fraction(2*2+18*18,2*(2+18))==Fraction(41,5)
print('Shuttle: independent clock-time integration gives 8.2 minutes')

counts=collections.Counter(sum(i==x for i,x in enumerate(p)) for p in itertools.permutations(range(6)))
assert sum(counts.values())==720
assert counts[0]==265 and counts[1]==264
retained=sum(n for k,n in counts.items() if k>=2)
fixed_sum=sum(k*n for k,n in counts.items() if k>=2)
assert retained==191 and fixed_sum==456
assert Fraction(fixed_sum,retained)==Fraction(456,191)
print('Permutations: exhaustive 720 outcomes give 456/191')

normal=NormalDist()
zlo=(.2+1)/.45
zhi=(1-.2)/.45
pvals=[1-normal.cdf(zlo),1-normal.cdf(zhi)]
ci90=(.2-normal.inv_cdf(.95)*.45,.2+normal.inv_cdf(.95)*.45)
ci95=(.2-normal.inv_cdf(.975)*.45,.2+normal.inv_cdf(.975)*.45)
assert all(p<.05 for p in pvals) and pvals[1]>.025
assert -1<ci90[0]<ci90[1]<1 and ci95[1]>1
print('Equivalence: p-values',pvals,'90% CI',ci90,'95% CI',ci95)
print('PASS: schema, unique IDs, verdict balance, option lengths, hidden subtopic, embedded parity, all six answer checks')
