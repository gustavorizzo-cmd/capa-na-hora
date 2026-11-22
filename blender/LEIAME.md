# Assets do Blender

`gerar_assets.py` modela e renderiza todos os sprites de `../assets/`:

- `blocos/`: texturas 64x64 de grama, terra, pedra, minério, madeira, folhas e areia
- `icones/`: os mesmos blocos em 3D isométrico (96x96), para o inventário
- `personagem/`: mineirinho em 96x152 (4x o hitbox 24x38): parado, andar, pulo e quebrar
- `cenario/`: morros em parallax (emendam na horizontal) e 3 nuvens
- `fonte/`: os arquivos `.blend` para abrir e editar no Blender

Para gerar de novo:

    pip install bpy        # Blender como módulo Python (precisa de Python 3.13)
    python blender/gerar_assets.py

ou, com o Blender instalado: `blender -b -P blender/gerar_assets.py`.

`teste.html` é o jogo usando esses assets.
