"""Passo 1: junta os anúncios coletados num só arquivo (saida/anuncios.json).

Lê dados/quintoandar.json e dados/coleta/*.jsonl (Zap Imóveis e Viva Real),
remove repetições entre Zap e Viva Real pelo id do imóvel e aplica os
critérios de build/config.json (quartos mínimos e aluguel máximo).
"""
import glob, json, os, re
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, '..', 'dados')
SAIDA = os.path.join(AQUI, 'saida')
os.makedirs(SAIDA, exist_ok=True)
cfg = json.load(open(os.path.join(AQUI, 'config.json'), encoding='utf8'))

# QuintoAndar (já no formato final)
qa = json.load(open(os.path.join(DADOS, 'quintoandar.json'), encoding='utf8'))
out = [d for d in qa if d['site'] == 'QuintoAndar']

# Imóveis do Viva Real que também estão no Zap (mesmo id) -> marca "também no Viva Real"
dup_txt = os.path.join(DADOS, 'coleta', 'vivareal_ids_dup.txt')
dup = set(re.findall(r'\b(\d{10})\b', open(dup_txt, encoding='utf8').read())) if os.path.exists(dup_txt) else set()

vistos = set()
for f in sorted(glob.glob(os.path.join(DADOS, 'coleta', '*.jsonl'))):
    for line in open(f, encoding='utf8'):
        if not line.strip():
            continue
        r = json.loads(line)
        m = re.search(r'id-(\d+)', r['url'])
        iid = m.group(1) if m else r['url']
        if iid in vistos:          # Zap e Viva Real repetem o mesmo imóvel
            continue
        vistos.add(iid)
        iptu = r.get('iptu'); anual = False
        if iptu and iptu > 800:    # alguns anúncios trazem o IPTU anual
            iptu = round(iptu / 12); anual = True
        cond = r.get('condominio') or 0
        extras = cond + (iptu or 0)
        site = 'Zap Imóveis' if r['site'] == 'zap' else 'Viva Real'
        bairro = r['bairro']
        if bairro.startswith(('Diamante', 'Santa Helena', 'Parque São Pedro')):
            bairro = re.sub(r'\s*\((Barreiro|Venda Nova)\)', '', bairro)
        out.append(dict(site=site, tambem='Viva Real' if (site == 'Zap Imóveis' and iid in dup) else None,
                        bairro=bairro, bairroOrig=r['bairro'], rua=r.get('rua') or '', area=r.get('area_m2'),
                        quartos=r['quartos'], vagas=r.get('vagas'), aluguel=r['aluguel'], extras=extras,
                        extrasTipo='cond', semCond=r.get('condominio') is None, iptuAnual=anual,
                        total=r['aluguel'] + extras, url=r['url']))

out = [d for d in out if (d['quartos'] or 0) >= cfg['quartos_min'] and d['aluguel'] <= cfg['aluguel_max']]
json.dump(out, open(os.path.join(SAIDA, 'anuncios.json'), 'w', encoding='utf8'), ensure_ascii=False)
print(len(out), 'anúncios', dict(Counter(d['site'] for d in out)))
