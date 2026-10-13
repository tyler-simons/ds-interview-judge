import json,sys,collections
p=sys.argv[1] if len(sys.argv)>1 else '/workspace/ds-judge-site/questions.json'
Q=[q for q in json.load(open(p)) if 'flaws' in q]
lt=0;bad=[];spreads=[];ranks=collections.Counter()
for q in Q:
    L=[len(f) for f in q['flaws']]; mx,mn=max(L),min(L); s=(mx-mn)/mx; spreads.append(s)
    if L[0]==mx and L.count(mx)==1: lt+=1
    ranks[sorted(L,reverse=True).index(L[0])+1]+=1
    if s>0.15: bad.append((q['id'],round(s,2),L))
print(f"{len(Q)} flawed questions")
print(f"true option strictly longest: {lt} ({lt/len(Q):.0%})")
print("rank of true option by length (1=longest):",dict(sorted(ranks.items())))
print(f"max spread {max(spreads):.0%}, mean {sum(spreads)/len(spreads):.0%}, over 15%: {len(bad)}")
for b in bad: print('  ',b)
