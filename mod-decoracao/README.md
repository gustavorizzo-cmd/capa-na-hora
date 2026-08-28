# Decoração+ — Add-on de decoração para Minecraft Bedrock

Add-on com **17 blocos decorativos** para Minecraft **Bedrock Edition**
(o da Play Store: celular, tablet, Windows 10/11 e console).

Arquivos prontos (o conteúdo é exatamente o mesmo nos dois):

- **[`Decoracao_Plus.mcaddon`](Decoracao_Plus.mcaddon)** — instala com um toque
- **[`Decoracao_Plus.zip`](Decoracao_Plus.zip)** — mesmo pacote em `.zip`, para
  quando o navegador ou o app de arquivos não deixa baixar/abrir o `.mcaddon`

## Blocos

| Bloco | ID | Detalhe |
|---|---|---|
| Mármore Polido | `deco:marmore_polido` | bloco cheio |
| Mármore Preto | `deco:marmore_preto` | bloco cheio |
| Mármore Dourado | `deco:marmore_dourado` | bloco cheio |
| Papel de Parede Azul | `deco:papel_parede_azul` | quebra rápido, inflamável |
| Papel de Parede Rosa | `deco:papel_parede_rosa` | quebra rápido, inflamável |
| Papel de Parede Verde | `deco:papel_parede_verde` | quebra rápido, inflamável |
| Estante Decorativa | `deco:estante_decorativa` | bloco cheio |
| Cristal de Luz | `deco:cristal_luz` | **luz 15** |
| Aquário | `deco:aquario` | translúcido, **luz 6** |
| Vaso de Planta | `deco:vaso_planta` | modelo 3D |
| Vaso de Flores | `deco:vaso_flor` | modelo 3D |
| Luminária de Teto | `deco:luminaria_teto` | modelo 3D, **luz 15** |
| Abajur | `deco:abajur` | modelo 3D, **luz 12** |
| Mesa de Centro | `deco:mesa_centro` | modelo 3D |
| Almofada | `deco:almofada` | modelo 3D |
| Tapete de Luxo | `deco:tapete` | modelo 3D, sem colisão |
| Pilar de Mármore | `deco:pilar_marmore` | modelo 3D |

Todos aparecem no criativo na aba **Construção** (Construction).
No modo sobrevivência dá para pegar por comando, por exemplo:
`/give @s deco:vaso_flor 1`

## Como instalar no tablet Android

1. Abra este arquivo no navegador do tablet e baixe:
   **`Decoracao_Plus.mcaddon`**
   (no GitHub: entre no arquivo e toque no botão de download / *Raw*).
2. Abra a pasta **Downloads** e toque no arquivo `Decoracao_Plus.mcaddon`.
   O Android vai perguntar com qual app abrir → escolha **Minecraft**.
3. O Minecraft abre sozinho e mostra "Importação iniciada / concluída".
4. Entre no mundo → **Editar mundo** (lápis) →
   **Pacotes de comportamento** → *Decoração+ (Comportamento)* → **Ativar**.
   O pacote visual é ativado junto automaticamente; se não for,
   ative também em **Pacotes de recursos**.
5. Importante: o mundo precisa estar com **"Criar novos mundos com..."**
   nada extra — este add-on **não** precisa de nenhuma opção experimental.

> Se ao tocar no arquivo o Android não oferecer o Minecraft, tente abrir pelo
> gerenciador de arquivos do Samsung ("Meus Arquivos") em vez do navegador.

### Se você baixou o `.zip`

O `.zip` e o `.mcaddon` são o **mesmo arquivo** — o Minecraft só reconhece
pela extensão. Duas saídas:

- **Renomear** (mais fácil): em "Meus Arquivos", segure o arquivo →
  *Renomear* → troque `Decoracao_Plus.zip` por `Decoracao_Plus.mcaddon` →
  toque nele. Se o Android esconder a extensão, ative
  "Mostrar extensões dos arquivos" nas opções do gerenciador.
- **Instalar na mão**: descompacte o `.zip` e copie a pasta `behavior_pack`
  para `Android/data/com.mojang.minecraftpe/files/games/com.mojang/behavior_packs/`
  e a pasta `resource_pack` para `.../com.mojang/resource_packs/`.
  Depois ative os dois nas configurações do mundo.

## Requisitos

Minecraft Bedrock **1.21.0 ou mais novo**. Não usa recursos experimentais
nem scripts — só JSON, texturas e modelos, que é o formato mais estável.

## Estrutura do projeto

```
mod-decoracao/
├── behavior_pack/          pacote de comportamento (define os blocos)
│   ├── manifest.json
│   └── blocks/*.json       um arquivo por bloco
├── resource_pack/          pacote visual
│   ├── manifest.json
│   ├── textures/blocks/    PNGs das texturas
│   ├── textures/terrain_texture.json
│   └── models/blocks/      modelos 3D (.geo.json)
├── tools/                  geradores das texturas, modelos e ícone
└── build.sh                gera tudo e empacota o .mcaddon
```

As texturas dos blocos com modelo 3D são de 32×32 e ficam divididas em
4 regiões de 16×16 (A/B/C/D). Cada face de cada cubo do modelo aponta para
uma dessas regiões — é o que permite um vaso ter barro, terra e folhas
usando uma textura só.

## Mexendo no add-on

Adicionar um bloco novo:

1. Crie a textura em `resource_pack/textures/blocks/` (ou adicione uma
   função em `tools/gen_textures.py`).
2. Registre a textura em `resource_pack/textures/terrain_texture.json`.
3. Crie o arquivo do bloco em `behavior_pack/blocks/` copiando um parecido.
4. Se for um bloco com formato próprio, adicione o modelo em
   `tools/gen_models.py`.
5. Adicione o nome em `resource_pack/texts/pt_BR.lang` e `en_US.lang`.

Depois é só rodar:

```bash
./build.sh
```

Isso regenera texturas/modelos/ícone, roda a validação
(`tools/validate.py` confere JSON, UUIDs, texturas e modelos que faltam) e
gera o `Decoracao_Plus.mcaddon` novo.

**Ao publicar uma versão nova**, suba o número em `version` nos dois
`manifest.json` — o Minecraft só substitui o pacote instalado se a versão
for maior. Não troque os UUIDs: eles são a identidade do add-on.
