#!/usr/bin/env sh
# Baixa os arquivos de origem do mapa de bairros de BH para build/geo/.
# Eles não ficam no repositório por terem licenças próprias (veja o README).
set -e
cd "$(dirname "$0")"
mkdir -p geo
BASE=https://raw.githubusercontent.com/deepin-community/libterralib/master/examples/data
curl -fsSL -o geo/BairroBH.MIF "$BASE/BairroBH.MIF"
curl -fsSL -o geo/BairroBH.MID "$BASE/BairroBH.MID"
curl -fsSL -o geo/bh_regionals.py https://raw.githubusercontent.com/argonptg/mercury/HEAD/src/bh_regionals.py
echo "Mapa baixado em build/geo/"
