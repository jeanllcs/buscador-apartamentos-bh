# Buscador de apartamentos em BH

Uma página que reúne, numa lista e num mapa dos bairros de Belo Horizonte, anúncios de aluguel de apartamentos tirados do **QuintoAndar**, do **Zap Imóveis** e do **Viva Real**. A versão publicada mostra apartamentos de **3 quartos com aluguel até R$ 3.000**, coletados em 18 de novembro de 2026.

**Ver a página:** https://jeanllcs.github.io/buscador-apartamentos-bh/

## Como usar a página

- **Filtros:** aluguel máximo, bairro ou rua, regional da Prefeitura, sites e a opção de incluir 4 quartos.
- **Ordenação:** menor aluguel, menor custo total, maior área ou menor preço por m².
- **Mapa:** cada preço fica dentro do bairro do anúncio. Aproxime para ver os preços, clique num preço para abrir o anúncio ou numa regional para filtrar por ela. No celular, use as abas Lista e Mapa.
- Cada cartão leva ao anúncio original. Os anúncios mudam rápido, então confira sempre no site.

A página é um único arquivo (`index.html`) sem servidor nem dependências: dá para abrir direto no navegador.

## Como os dados foram coletados

| Site | Como | Observações |
|---|---|---|
| QuintoAndar | Leitura das páginas de busca | O "total" é o que o site mostra (aluguel + condomínio + IPTU + seguro + taxa). |
| Zap Imóveis e Viva Real | 5 páginas de cada site, a partir de um computador pessoal | Os servidores em nuvem são bloqueados por esses sites. Os dois repetem cerca de 95% dos imóveis (mesmo `id-NNN` na URL), então cada imóvel aparece uma vez só. IPTU acima de R$ 800 é tratado como anual e dividido por 12. |
| OLX | Não foi possível | O site bloqueia coleta automática (Cloudflare). |

Os dados ficam em `dados/`:

- `dados/quintoandar.json`: anúncios do QuintoAndar já no formato final.
- `dados/coleta/*.jsonl`: anúncios do Zap e do Viva Real, um por linha, neste formato:

```json
{"site":"zap","bairro":"Buritis","rua":"Rua Ernani Agricola","area_m2":85,"quartos":3,"vagas":1,"aluguel":3000,"condominio":767,"iptu":168,"url":"https://www.zapimoveis.com.br/imovel/...-id-2914228366/"}
```

  `site` é `zap` ou `vivareal`; `rua`, `condominio` e `iptu` podem ser `null`.
- `dados/coleta/vivareal_ids_dup.txt`: ids do Viva Real que também estão no Zap (para a marca "também no Viva Real").

## Refazer a busca com outros critérios

Precisa de Python 3.9+ e `curl`.

```sh
pip install -r build/requirements.txt   # shapely
sh build/baixar_mapa.sh                 # baixa o mapa de bairros para build/geo/
```

1. **Ajuste os critérios** em `build/config.json`: título da página, data da coleta, número mínimo de quartos e aluguel máximo.
2. **Colete anúncios novos** nos sites, com a busca já filtrada (cidade, quartos, preço), e salve:
   - os do Zap e Viva Real em `dados/coleta/*.jsonl` (formato acima);
   - os do QuintoAndar em `dados/quintoandar.json`.
   Respeite os termos de uso de cada site e não faça muitas requisições seguidas.
3. **Gere a página:**

```sh
python build/merge.py         # junta, remove repetidos e aplica os critérios -> build/saida/anuncios.json
python build/buildgeo.py      # posiciona cada anúncio no seu bairro         -> build/saida/*.json
python build/gerar_pagina.py  # monta o index.html na raiz
```

Abra o `index.html` no navegador para conferir e faça commit para atualizar o site.

**Outra cidade:** a lista e os filtros funcionam com qualquer cidade, mas o mapa é específico de BH (bairros e regionais). Para outra cidade é preciso trocar a base de bairros em `build/buildgeo.py` (polígonos em UTM no formato MapInfo `.MIF/.MID`) e o mapa bairro → região.

## Estrutura

```
index.html              página pronta (gerada)
dados/                  anúncios coletados
build/config.json       critérios e textos da página
build/merge.py          passo 1: junta e deduplica os anúncios
build/buildgeo.py       passo 2: mapa dos bairros e posição dos anúncios
build/gerar_pagina.py   passo 3: preenche o template
build/template.html     layout, filtros e mapa (HTML, CSS e JS)
build/baixar_mapa.sh    baixa os arquivos de origem do mapa
```

## Créditos e avisos

- **Anúncios:** pertencem aos respectivos sites (QuintoAndar, Zap Imóveis, Viva Real). O projeto guarda só dados básicos (bairro, rua, área, quartos, vagas, valores) e o link para o anúncio original, sem fotos, descrições ou contatos. Não há vínculo com esses sites. Os valores podem estar desatualizados.
- **Bairros de BH:** arquivo `BairroBH.MIF/.MID`, distribuído como exemplo da biblioteca [TerraLib](https://github.com/deepin-community/libterralib) (INPE/Tecgraf, licença LGPL-2.1+). Não fica neste repositório; o script `build/baixar_mapa.sh` baixa da fonte.
- **Bairro → regional:** tabela de [argonptg/mercury](https://github.com/argonptg/mercury) (`src/bh_regionals.py`), gerada a partir de anexo de edital da Prefeitura de Belo Horizonte. Também é baixada pelo script, e lida apenas como dado.
- **Posições no mapa:** aproximadas. Os sites não informam o número do prédio, então cada anúncio é colocado num ponto aleatório dentro do bairro.

## Licença

O código deste repositório está sob a [licença MIT](LICENSE). Os dados de terceiros citados acima seguem as licenças e termos de suas fontes.
