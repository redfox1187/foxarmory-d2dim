#!/usr/bin/env python3
import csv, glob, hashlib, json, pathlib, re, sqlite3, statistics, sys
from collections import defaultdict, Counter

MANIFEST_VERSION='244213.26.06.29.2000-1-bnet.65864'
MAINT=('Auto-Loading Holster','Envious Assassin','Overflow','Reconstruction','Rewind Rounds','Subsistence')
PREF={'Submachine Gun','Hand Cannon','Grenade Launcher','Rocket Launcher'}
DIRECT_EX={2357297366,2188764214,3654674561,2208405142,814876684,1364093401}
BREAKNECK=2026755633
RR=re.compile(r'^dimwishlist:item=(-?)(\d+)&perks=([^#]*)#notes:(.*)$')
MR={k:re.compile(r'(?:^|\|\s*)'+k+r':(\d+)([EPV]?)') for k in ('CPVE','PVE','CPVP','PVP')}

def metric(notes,k):
 m=MR[k].search(notes); return (int(m.group(1)),m.group(2)) if m else (None,'')
def repl_pve(notes,n,state=None):
 m=MR['PVE'].search(notes)
 if not m:return notes
 s=state if state is not None else (m.group(2) or 'E'); a,b=m.span(); old=m.group(0); pre=old[:old.find('PVE:')]
 return notes[:a]+pre+f'PVE:{n}{s}'+notes[b:]
def table(con,name):
 out={}
 for r in con.execute(f'SELECT id,json FROM "{name}"'):
  try:o=json.loads(r['json'])
  except:continue
  out[int(r['id']) & 0xffffffff]=o
 return out
def load_manifest(db):
 con=sqlite3.connect(db);con.row_factory=sqlite3.Row;items=table(con,'DestinyInventoryItemDefinition');coll=table(con,'DestinyCollectibleDefinition');con.close();return items,coll
def roll_legend(o):
 inv=o.get('inventory') or {}; ent=((o.get('sockets') or {}).get('socketEntries') or [])
 return o.get('itemType')==3 and inv.get('tierType')==5 and inv.get('isInstanceItem',False) and any(s.get('randomizedPlugSetHash') or s.get('reusablePlugSetHash') for s in ent)
def cmap():
 out={}
 for raw in pathlib.Path('tools/favorite-candidates/catalog-positive-fit-v0.1.txt').read_text().splitlines():
  if not raw or raw.startswith('#'):continue
  h,p,_,b=raw.split('|',3);out[(int(h),tuple(int(x) for x in p.split(',') if x))]=int(b)
 return out
def byhash(lines):
 d=defaultdict(list)
 for i,l in enumerate(lines):
  m=RR.match(l)
  if m:d[int(m.group(2))].append((i,bool(m.group(1)),tuple(int(x) for x in m.group(3).split(',') if x.strip().isdigit()),m.group(4)))
 return d
def community(d,h):
 r=d.get(h,[]);r=[x for x in r if 'match:fallback' in x[3]] or r
 for x in r:
  a,_=metric(x[3],'CPVE');b,_=metric(x[3],'CPVP')
  if a is not None and b is not None:return a,b
 return None,None

def govern_catalog(lines,items,aff):
 out=[];audit=[]
 for l in lines:
  m=RR.match(l)
  if not m or m.group(1) or not m.group(3):out.append(l);continue
  h=int(m.group(2));perks=tuple(int(x) for x in m.group(3).split(',') if x.strip().isdigit());notes=m.group(4);base,_=metric(notes,'PVE')
  if base is None:out.append(l);continue
  typ=(items.get(h) or {}).get('itemTypeDisplayName') or '';a=aff.get((h,perks),0)
  names=[((items.get(x) or {}).get('displayProperties') or {}).get('name','') for x in perks]
  maint=any(any(k in n for k in MAINT) for n in names);ma=1 if maint and a==0 else 0;fam=1 if typ in PREF and (a>0 or maint) else 0;fus=-4 if typ=='Fusion Rifle' else 0
  final=max(0,min(98,base+a+ma+fam+fus));adj=final-base
  if adj:
   notes=repl_pve(notes,final)+f' | score-model:foxfit-v1.0 | fit-adjust:{adj:+d}';l=f'dimwishlist:item={h}&perks={m.group(3)}#notes:{notes}'
  out.append(l);audit.append((h,typ,base,final,adj,a,int(maint),fam,fus))
 return out,audit

def favorite_block(source,items):
 d=byhash(source);leg=[]
 for p in sorted(glob.glob('tools/favorite-candidates/part*.txt')):
  for raw in pathlib.Path(p).read_text().splitlines():
   if raw.strip():
    h,ps,n,k=raw.split('|',3);leg.append([int(h),tuple(int(x) for x in ps.split(',') if x),n,k])
 seen=set();leg=[x for x in leg if not ((x[0],x[1]) in seen or seen.add((x[0],x[1])))]
 for h in {x[0] for x in leg if x[3]=='ambiguous_dual_candidate'}:
  ix=[i for i,x in enumerate(leg) if x[0]==h and x[3]=='ambiguous_dual_candidate']; vals=sorted((leg[i] for i in ix),key=lambda x:x[1])
  for i,v in zip(ix,vals):leg[i]=v
 scores={}
 for raw in pathlib.Path('tools/favorite-candidates/scores-v0.1.txt').read_text().splitlines():
  if raw and not raw.startswith('#'):
   h,p,e,q=raw.split('|',3);scores[(int(h),tuple(int(x) for x in p.split(',') if x))]=(e,q)
 ex={}
 for raw in pathlib.Path('tools/favorite-candidates/exotic-scores-v0.1.txt').read_text().splitlines():
  if raw and not raw.startswith('#'):
   h,e,q=raw.split('|',2);ex[int(h)]=(e,q)
 b=['// FQX Fox Favorite protection + profile-governed Fox Fit — v1.0','// Exact Legendary Favorites precede generic/core and negative fallback rules; Favorite Exotics use item-level rules.','// Community scores remain source-derived. Profile-direct evidence may promote validation to Provisional; no rule is auto-Verified.','// Generic catalog preferences are governed separately; exact Favorites override generic weapon-family priors.','','// --- Favorite Legendary exact rolls ---']
 for h,p,n,k in leg:
  e,q=scores[(h,p)];ce,cq=community(d,h)
  if h==BREAKNECK:e='80P';ev='favorite+profile-direct'
  else:ev='favorite+historical-personal' if e.endswith('P') else 'favorite'
  amb=' | ambiguity:same-name-legal-dual-candidate' if k=='ambiguous_dual_candidate' else ''
  b += [f'// {n} — Fox Favorite',f'dimwishlist:item={h}&perks={",".join(map(str,p))}#notes:CPVE:{ce} | PVE:{e} | CPVP:{cq} | PVP:{q} | match:fox-favorite | evidence:{ev} | source:fox-owned | score-model:foxfit-v1.0{amb}']
 b += ['','// --- Favorite Exotics (item-level preference; variant-specific quality may still differ) ---']
 for h,(e,q) in sorted(ex.items()):
  ce,cq=community(d,h);name=((items.get(h) or {}).get('displayProperties') or {}).get('name') or str(h)
  if h in DIRECT_EX:e=re.sub(r'[EPV]$','P',e);ev='favorite+profile-direct'
  else:ev='favorite+historical-personal' if e.endswith('P') or q.endswith('P') else 'favorite'
  b += [f'// {name} — Fox Favorite Exotic',f'dimwishlist:item={h}&perks=#notes:CPVE:{ce} | PVE:{e} | CPVP:{cq} | PVP:{q} | match:fox-favorite-exotic | evidence:{ev} | source:fox-owned | scope:item-level | score-model:foxfit-v1.0']
 return b,len(leg),len(ex)
def insert(lines,b):
 i=next(i for i,l in enumerate(lines) if l.startswith('dimwishlist:item='))
 while i>0 and lines[i-1].startswith('//') and not lines[i-1].startswith('// 2026 Return'):i-=1
 return lines[:i]+b+['']+lines[i:]

def main(db):
 src=pathlib.Path('foxarmory-2026-return-d2dim.txt').read_text().splitlines();items,coll=load_manifest(db); governed,cat=govern_catalog(src,items,cmap())
 governed[1]='description:[v1.0 2026-10-06] Full-manifest Destiny 2 triage wishlist. Profile-governed Fox Fit, exact Favorite protection, and inferred fallback ratings cover every roll-bearing Legendary definition in the current Bungie manifest.'
 for i,l in enumerate(governed[:12]):
  if l.startswith('// 2026 Return v'):governed[i]='// 2026 Return v1.0 — full-manifest inferred coverage + profile-governed Fox Fit';break
 b,nleg,nex=favorite_block(src,items);lines=insert(governed,b)
 universe={h:o for h,o in items.items() if roll_legend(o)};represented={int(m.group(2)) for l in lines if (m:=RR.match(l))};missing=sorted(set(universe)-represented,key=lambda h:((universe[h].get('itemTypeDisplayName') or ''),((universe[h].get('displayProperties') or {}).get('name') or ''),h))
 tv=defaultdict(lambda:defaultdict(list));gv=defaultdict(list)
 for l in src:
  m=RR.match(l)
  if not m or not m.group(1):continue
  h=int(m.group(2));typ=(items.get(h) or {}).get('itemTypeDisplayName') or ''
  for k in MR:
   v,_=metric(m.group(4),k)
   if v is not None:tv[typ][k].append(v);gv[k].append(v)
 med=lambda t,k:int(round(statistics.median(tv[t][k] or gv[k])))
 inf=[];lines += ['','// --- v1.0 inferred full-manifest Legendary fallbacks ---','// Low-confidence item-level type-prior estimates; not community consensus or exact-roll endorsements.','// Availability labels describe manifest evidence only and do not assert that stale acquisition strings remain active.']
 for h in missing:
  o=universe[h];typ=o.get('itemTypeDisplayName') or '';name=((o.get('displayProperties') or {}).get('name') or str(h));ch=o.get('collectibleHash');c=coll.get(int(ch)) if ch else None;ss=((c or {}).get('sourceString') or '').strip();sd=o.get('sourceData') or {};sh=sd.get('sourceHashes') or [];aq=((c or {}).get('acquisitionInfo') or {});av='source-indicated' if ss or sh or aq else 'manifest-unverified'
  ce,e,cq,q=[med(typ,k) for k in ('CPVE','PVE','CPVP','PVP')]
  if typ=='Fusion Rifle':e=max(0,e-4)
  lines += [f'// {name} — inferred fallback',f'dimwishlist:item=-{h}&perks=#notes:CPVE:{ce}E | PVE:{e}E | CPVP:{cq}E | PVP:{q}E | match:fallback | evidence:inferred-manifest | type:{typ} | availability:{av} | score-model:foxfit-v1.0'];inf.append({'weapon_hash':h,'name':name,'type':typ,'CPVE':ce,'PVE':e,'CPVP':cq,'PVP':q,'availability':av,'collectible_source':ss})
 by=byhash(lines);srcneg={int(m.group(2)):l for l in src if (m:=RR.match(l)) and m.group(1)};mal=[(i+1,l) for i,l in enumerate(lines) if l.startswith('dimwishlist:item=') and not RR.match(l)];dupn=[h for h,r in by.items() if sum(x[1] for x in r)>1];chg=[h for h,l in srcneg.items() if l not in [lines[x[0]] for x in by.get(h,[]) if x[1]]];ordf=[h for h,r in by.items() if (neg:=[x[0] for x in r if x[1]]) and (fav:=[x[0] for x in r if not x[1] and 'match:fox-favorite' in x[3]]) and min(fav)>min(neg)];miss=sorted(set(universe)-set(by))
 text='\n'.join(lines)+'\n';out=pathlib.Path('build');out.mkdir(exist_ok=True);(out/'foxarmory-2026-return-d2dim.v1.0.txt').write_text(text)
 with (out/'D2_v1_Inferred_Fallbacks_20261006.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inf[0]));w.writeheader();w.writerows(inf)
 audit={'manifest_version':MANIFEST_VERSION,'manifest_roll_bearing_legendary':len(universe),'represented_manifest_hashes':len(set(universe)&set(by)),'coverage_missing':len(miss),'new_inferred_fallbacks':len(inf),'favorite_legendary_rules':nleg,'favorite_exotic_rules':nex,'catalog_rules_audited':len(cat),'catalog_rules_changed':sum(x[4]!=0 for x in cat),'malformed':len(mal),'duplicate_negative':len(dupn),'existing_negative_changed':len(chg),'favorite_ordering_failures':len(ordf),'availability_counts':dict(Counter(x['availability'] for x in inf)),'v10_sha256':hashlib.sha256(text.encode()).hexdigest(),'lines':len(lines),'failures':{'missing':miss,'malformed':mal[:20],'duplicate_negative':dupn,'existing_negative_changed':chg,'ordering':ordf}}
 (out/'fqx_v1_release_audit.json').write_text(json.dumps(audit,indent=2));(out/'report_fqx-destiny-2_v1.0-release_20261006.md').write_text(f"# FQX Destiny 2 — v1.0 Release Audit\n\n- Manifest: {MANIFEST_VERSION}\n- Roll-bearing Legendary definitions: **{len(universe)}**\n- Represented after build: **{audit['represented_manifest_hashes']}**\n- New inferred fallbacks: **{len(inf)}**\n- Coverage missing: **{len(miss)}**\n- Favorite rules: **{nleg+nex}** ({nleg} Legendary exact, {nex} Exotic item-level)\n- Malformed rules: **{len(mal)}**\n- Duplicate negative fallbacks: **{len(dupn)}**\n- Existing negative fallbacks changed: **{len(chg)}**\n- Favorite ordering failures: **{len(ordf)}**\n- v1.0 SHA-256: {audit['v10_sha256']}\n\n## Inference policy\n\nEvery roll-bearing Legendary definition in the current Bungie manifest is rated. Existing curated rules remain authoritative. Previously uncovered definitions receive Estimated item-level fallback scores using medians of existing scored fallbacks by weapon type. Fusion Rifle PvE receives the documented Fox-fit -4 family correction. These rows are labeled evidence:inferred-manifest and are not represented as measured community consensus.\n\nThis deliberately forms a coverage superset: Bungie retains historical definitions and stale acquisition strings in the manifest. The availability field therefore distinguishes source-indicated from manifest-unverified without falsely claiming every definition currently drops.\n")
 print(json.dumps(audit,indent=2))
 if miss or mal or dupn or chg or ordf:raise SystemExit('release audit failed')
if __name__=='__main__':main(sys.argv[1])
