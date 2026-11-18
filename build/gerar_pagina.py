"""Passo 3: monta o index.html a partir do template e dos dados gerados."""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, 'saida')
cfg = json.load(open(os.path.join(AQUI, 'config.json'), encoding='utf8'))
t = open(os.path.join(AQUI, 'template.html'), encoding='utf8').read()
dados = open(os.path.join(SAIDA, 'anuncios_mapa.json'), encoding='utf8').read()
geo = open(os.path.join(SAIDA, 'geo.json'), encoding='utf8').read()
t = (t.replace('__TITULO__', cfg['titulo'])
      .replace('__DATA_COLETA__', cfg['data_coleta'])
      .replace('__ALUGUEL_MAX__', str(cfg['aluguel_max']))
      .replace('__DATA__', dados.replace('</', '<\\/'))
      .replace('__GEO__', geo))
destino = os.path.join(AQUI, '..', 'index.html')
open(destino, 'w', encoding='utf8').write(t)
print('index.html gerado:', os.path.getsize(destino), 'bytes')
