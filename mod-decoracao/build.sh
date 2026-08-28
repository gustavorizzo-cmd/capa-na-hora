#!/usr/bin/env bash
# Gera as texturas, os modelos e empacota o add-on em Decoracao_Plus.mcaddon
set -euo pipefail
cd "$(dirname "$0")"

python3 tools/gen_textures.py
python3 tools/gen_models.py
python3 tools/gen_icon.py
python3 tools/validate.py

OUT="Decoracao_Plus.mcaddon"
rm -f "$OUT"
zip -r -q -X "$OUT" behavior_pack resource_pack \
  -x '*/.DS_Store' '*__pycache__*'
echo "Pronto: $(pwd)/$OUT ($(du -h "$OUT" | cut -f1))"
