"""Passo 2: desenha o mapa dos bairros de BH e posiciona cada anúncio dentro do seu bairro."""
import re, csv, json, unicodedata, random, sys, ast, os
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union, polylabel

AQUI = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(AQUI, 'geo')
SAIDA = os.path.join(AQUI, 'saida')

# Mapa bairro -> regional (dados lidos como texto, sem executar o arquivo baixado)
_t = open(os.path.join(GEO, 'bh_regionals.py'), encoding='utf8').read()
REG = ast.literal_eval(_t[_t.index('{'):_t.index('}') + 1])

def n(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'[^A-Z0-9]+', ' ', s).strip()

names = [r[0] for r in csv.reader(open(os.path.join(GEO, 'BairroBH.MID'), encoding='latin1'))]
lines = open(os.path.join(GEO, 'BairroBH.MIF'), encoding='latin1').read().split('\n')
i = lines.index('Data') + 1
polys = []
while i < len(lines):
    l = lines[i].strip()
    if l.startswith('Region'):
        k = int(l.split()[1]); rings = []; i += 1
        for _ in range(k):
            c = int(lines[i].strip()); i += 1
            pts = [tuple(map(float, lines[i + j].split())) for j in range(c)]; i += c
            rings.append(Polygon(pts).buffer(0))
        polys.append(unary_union(rings))
    else:
        i += 1
assert len(polys) == len(names), (len(polys), len(names))

MINX = 598000; MAXY = 813000; S = 10
def tx(x, y): return ((x - MINX) / S, (MAXY - y) / S)
def path(g, tol=12):
    g = g.simplify(tol)
    out = []
    for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if p.is_empty: continue
        cs = [tx(*c) for c in p.exterior.coords]
        out.append('M' + 'L'.join(f'{a:.0f} {b:.0f}' for a, b in cs) + 'Z')
    return ''.join(out)

manual = {'ZONA RURAL': 'NORTE', 'MARIZE': 'NORTE', 'MINAS CAIXA': 'VENDA NOVA', 'INDUSTRIAL RODRIGUES DA CUNHA': 'NORDESTE', 'BAIRRO DA GRACA': 'NORDESTE', 'ZONA RURAL SERRA DO CURRAL': 'CENTRO-SUL', 'ITAPUA': 'PAMPULHA', 'UFMG': 'PAMPULHA', 'TUPI': 'NORTE', 'GORDURAS': 'NORDESTE', 'MORRO DAS PEDRAS': 'OESTE', 'ESTRELA DALVA': 'OESTE', 'ALTO DOS CAICARAS': 'NOROESTE', 'BARREIRO DE BAIXO': 'BARREIRO', 'BARREIRO DE CIMA': 'BARREIRO', 'PEDRO II': 'NOROESTE', 'MORRO DO PAPAGAIO': 'CENTRO-SUL', 'PARQUE DAS MANGABEIRAS': 'CENTRO-SUL', 'VILA CAFEZAL': 'CENTRO-SUL', 'SARANDI': 'PAMPULHA', 'CONJUNTO CALIFORNIA': 'NOROESTE', 'CABANA': 'OESTE', 'NOVA BARROCA': 'OESTE', 'FREI EUSTAQUIO': 'NOROESTE', 'IPANEMA': 'NOROESTE'}
breg = {}
for nm in names:
    k = n(nm)
    r = REG.get(k) or manual.get(k)
    if not r:
        r = REG.get(n(re.sub(r'\s*\(.*', '', nm)))
    breg[nm] = r
miss = [nm for nm, r in breg.items() if not r]
for nm in miss:
    g = polys[names.index(nm)]
    best = min((polys[j].distance(g), breg[names[j]]) for j in range(len(names))
               if breg[names[j]] and names[j] != nm)
    breg[nm] = best[1]
print('fallback', [(m, breg[m]) for m in miss], file=sys.stderr)

bairros = [{'n': nm.title(), 'r': breg[nm].title(), 'd': path(g)} for nm, g in zip(names, polys)]
regs = {}
for nm, g in zip(names, polys): regs.setdefault(breg[nm], []).append(g.buffer(2))
regions = []
for r, gs in regs.items():
    u = unary_union(gs); big = max(u.geoms, key=lambda q: q.area) if isinstance(u, MultiPolygon) else u; c = polylabel(big, 20)
    x, y = tx(c.x, c.y)
    regions.append({'r': r.title(), 'd': path(u, 25), 'x': round(x), 'y': round(y)})

alias = {'Itapoã': 'ITAPUA', 'Horto Florestal': 'HORTO', 'Manacás': 'AEROPORTO',
         'São João Batista': 'SAO JOAO BATISTA (VENDA NOVA)', 'São João Batista (Venda Nova)': 'SAO JOAO BATISTA (VENDA NOVA)',
         'Alto Caiçaras': 'ALTO DOS CAICARAS', 'Caiçaras': 'CAICARA', 'Indaiá': 'SANTA AMELIA', 'Fernão Dias': 'PALMARES',
         'Silveira': 'CIDADE NOVA', 'Diamante': 'BARREIRO DE CIMA', 'Araguaia': 'MILIONARIOS', 'Candelária': 'VENDA NOVA',
         'Parque São Pedro': 'VENDA NOVA', 'Barreiro': 'BARREIRO DE CIMA'}
EXACT = {'São João Batista', 'São João Batista (Venda Nova)', 'Alto Caiçaras', 'Caiçaras', 'Barreiro', 'Itapoã'}
data = json.load(open(os.path.join(SAIDA, 'anuncios.json'), encoding='utf8')); rnd = random.Random(7)
data = [d for d in data]
for d in data:
    key = alias.get(d['bairro']) or n(d['bairro'])
    if key not in names:
        print('SEM POLIGONO', d['bairro']); continue
    g = polys[names.index(key)]
    inner = g.buffer(-60)
    if inner.area <= 0: inner = g
    minx, miny, maxx, maxy = inner.bounds
    while True:
        p = Point(rnd.uniform(minx, maxx), rnd.uniform(miny, maxy))
        if inner.contains(p): break
    d['x'], d['y'] = [round(v) for v in tx(p.x, p.y)]
    d['regional'] = (REG.get(n(d['bairro'])) or REG.get(n(d['bairro']).replace(' VENDA NOVA','')) or breg[key]).title()
    d['aprox'] = d['bairro'] in alias and d['bairro'] not in EXACT

W = round((619900 - MINX) / S); H = round((MAXY - 781600) / S)
json.dump({'w': W, 'h': H, 'bairros': bairros, 'regions': regions},
          open(os.path.join(SAIDA, 'geo.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
json.dump(data, open(os.path.join(SAIDA, 'anuncios_mapa.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(os.path.getsize(os.path.join(SAIDA, 'geo.json')), W, H, sorted(set(d['regional'] for d in data)))
print(sorted(set(r['r'] for r in regions)))
