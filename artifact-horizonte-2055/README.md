# Horizonte Digital 2055 — fonte do site

`index.html` deste diretório (simulação de faturamento, NÃO o site) é a **fonte editável** do Artifact publicado:

- URL: https://claude.ai/code/artifact/91f4d84f-3012-4e71-8fc0-95ce51ec2e38
- Título: `Horizonte Digital 2055`
- Favicon publicado: manter o mesmo entre republicações

## Como republicar

O arquivo é um **fragmento** de HTML, de propósito: sem `<!doctype>`, `<html>`,
`<head>` ou `<body>`. A plataforma envolve o conteúdo nessas tags no momento da
publicação. Para atualizar o site mantendo a MESMA URL, publique este arquivo
passando a URL acima — publicar sem a URL cria um artifact separado.

## O que a página é

Simulação de faturamento da Horizonte Digital de 2026 a 2055. Nenhuma receita é
digitada à mão: tudo é calculado em JS a partir de drivers (visitas, pagantes,
assinantes, unidades vendidas etc.).

Seções: leitura prévia · seis números-resumo · crescimento em dentes · receita
vs. caixa · receita por divisão ano a ano · de onde viria o dinheiro · premissa
que mais move o total · cenários · drivers · fórmula por divisão · o que
precisaria ser verdade · do faturamento ao resultado.

## Onde mexer nos números

Tudo no `<script>` que começa na linha ~448.

| O quê | Onde |
|---|---|
| Janela de anos | `A0=2026`, `A1=2055` |
| Constantes macro | `INFL`, `CAMBIO`, `DEVEX`, `RBX_SHARE`, `CUT`, `YT_SHARE`, `GATE`, `DIST` |
| Custo por divisão | `CUSTO={games,studios,ia,canal,inter}` |
| Imposto (Simples) | `aliq(f)` |
| Lançamentos AeroWorld | `AW_LANC`, `AW_DECAY` |
| Cenários | `CENARIOS` (cauteloso / base / otimista, com multiplicadores `mult`) |
| Divisões, fórmulas e textos | `FRENTES` |

Rampas de driver usam `ramp(ano, {ano:valor,...})` com interpolação linear;
`de(ano, inicio, rampa)` zera tudo antes do ano de estreia da frente.

## Divisões

Horizonte Games (jogos/Roblox/AeroWorld) · Horizonte Studios (filmes, séries,
streaming) · Horizonte IA (assinaturas e API) · canal · internacional.
