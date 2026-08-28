#!/usr/bin/env bash
# Gera as texturas, os modelos e empacota o add-on.
# Sai em dois formatos com o mesmo conteudo:
#   Decoracao_Plus.mcaddon -> instala com um toque no Android/Windows
#   Decoracao_Plus.zip      -> mesmo arquivo, para quem prefere .zip
#   *.mcpack                -> um pacote por arquivo, para apps importadores
set -euo pipefail
cd "$(dirname "$0")"

python3 tools/gen_textures.py
python3 tools/gen_models.py
python3 tools/gen_icon.py
python3 tools/validate.py

OUT="Decoracao_Plus.mcaddon"
ZIP="Decoracao_Plus.zip"
rm -f "$OUT" "$ZIP"
zip -r -q -X "$OUT" behavior_pack resource_pack \
  -x '*/.DS_Store' '*__pycache__*'
cp "$OUT" "$ZIP"

# .mcpack: cada pacote sozinho, com o manifest.json na RAIZ do arquivo
# (e' assim que os apps importadores de zip esperam encontrar).
rm -f Decoracao_Plus_Comportamento.mcpack Decoracao_Plus_Visual.mcpack
( cd behavior_pack && zip -r -q -X ../Decoracao_Plus_Comportamento.mcpack . \
    -x '.DS_Store' '*__pycache__*' )
( cd resource_pack && zip -r -q -X ../Decoracao_Plus_Visual.mcpack . \
    -x '.DS_Store' '*__pycache__*' )

for f in "$OUT" "$ZIP" Decoracao_Plus_Comportamento.mcpack Decoracao_Plus_Visual.mcpack; do
  echo "Pronto: $(pwd)/$f ($(du -h "$f" | cut -f1))"
done
