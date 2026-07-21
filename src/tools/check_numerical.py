import json
from pathlib import Path
from statistics import mean, stdev
PROJECT = Path(__file__).resolve().parent.parent

RESULTS = Path(r'PROJECT / "experiments\results"')
with open(RESULTS / 'baselines_200.json', encoding='utf-8') as f:
    bl = json.load(f)

def load_progress(name):
    p = RESULTS / name / '_progress.json'
    with open(p, encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        for k,v in data.items():
            if isinstance(v, dict):
                return v
    return data

m2 = load_progress('moea_2obj')
m3 = load_progress('moea_3obj')
b2 = load_progress('b2_profit_bl')

def stats(loader, cls, key='f1'):
    keys = [k for k in loader if k.startswith(cls + '/')]
    vals = []
    for k in keys:
        entry = loader[k]
        if isinstance(entry, dict) and key in entry:
            vals.append(entry[key])
        elif isinstance(entry, dict):
            # try nested b1/b3
            for sub in ['b1','b3',key]:
                if sub in entry and isinstance(entry[sub], dict):
                    if key in entry[sub]:
                        vals.append(entry[sub][key])
                        break
    if not vals:
        return None
    return {'mean': mean(vals), 'std': stdev(vals), 'n': len(vals)}

for cls in ['S1','S2','S3','S4']:
    print(f'\n=== {cls} ===')
    print('G-BL:', stats(bl, cls, 'f1'))
    print('G-SM:', stats({k:v.get('b3',{}) for k,v in bl.items()}, cls, 'f1'))
    print('MOEA-2 f1:', stats(m2, cls, 'f1'))
    print('MOEA-2 f2:', stats(m2, cls, 'f2'))
    print('MOEA-2 f3:', stats(m2, cls, 'f3'))
    print('MOEA-3 f1:', stats(m3, cls, 'f1'))
    print('MOEA-3 f2:', stats(m3, cls, 'f2'))
    print('MOEA-3 f3:', stats(m3, cls, 'f3'))
    print('GA-P-BL f1:', stats(b2, cls, 'f1'))

print('\n=== Scale sensitivity MOEA-2 vs G-BL ===')
for cls in ['S1','S2','S3','S4']:
    keys = [k for k in bl if k.startswith(cls+'/')]
    ratios=[]; f2_imp=[]; trade=0
    for k in keys:
        g = bl[k].get('b1',{})
        m = m2.get(k,{})
        if not g or not m: continue
        f1_g, f1_m = g.get('f1',1), m.get('f1',0)
        f2_g, f2_m = g.get('f2',0), m.get('f2',0)
        if f1_g>0: ratios.append(f1_m/f1_g)
        if f2_g>0: f2_imp.append((f2_m-f2_g)/f2_g*100)
        if f1_g>0 and (f1_m/f1_g) < 0.95: trade += 1
    print(f"{cls}: f1* ratio={mean(ratios):.4f}±{stdev(ratios):.4f}, f2 imp={mean(f2_imp):.2f}%±{stdev(f2_imp):.2f}%, trade={trade}/{len(keys)}={100*trade/len(keys):.1f}%")

print('\n=== Frontier counts ===')
for cls in ['S1','S2','S3','S4']:
    for name, data in [('MOEA-2', m2), ('MOEA-3', m3)]:
        keys = [k for k in data if k.startswith(cls+'/')]
        nf = [data[k]['n_frontier'] for k in keys if isinstance(data.get(k), dict) and 'n_frontier' in data[k]]
        if nf:
            print(f"{cls} {name}: frontier mean={mean(nf):.1f} std={stdev(nf):.1f}")

print('\n=== Effect sizes ===')
with open(RESULTS / 'statistical_results.json', encoding='utf-8') as f:
    sr = json.load(f)
for pair, v in sr['pairwise_wilcoxon'].items():
    if any(x in pair for x in ['MOEA-2_vs_MOEA-3','G-BL_vs_G-SM','G-BL_vs_GA-P-BL']):
        print(pair, 'delta=', v['cliffs_delta'], 'p=', v['p_value'])
