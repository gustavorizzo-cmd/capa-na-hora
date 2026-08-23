# Horizonte Digital — site

Site público: https://horizonte-digital-projeto.gustavo-rizzo.chatgpt.site/

**O código-fonte ainda NÃO está neste diretório.** O handoff de 22/08/2026 diz
que o pacote de código acompanharia a entrega, mas apenas os dois documentos de
`docs/` foram recebidos. Quando o código chegar, ele entra aqui.

## Documentos recebidos

| Arquivo | O que é | Peso na decisão |
|---|---|---|
| `docs/HANDOFF-2026-08-22.md` | Entrega de 22/08/2026, estado atual do produto | Prioridade 3 |
| `docs/MEMORIA-V2-2026-08-03.txt` | Memória consolidada V2, 10.090 linhas | Prioridade 4 — contém decisões antigas |

Ordem de prioridade em caso de conflito, definida pelo handoff:

1. pedido atual e explícito de Theo ou Gustavo;
2. código-fonte atual;
3. `docs/HANDOFF-2026-08-22.md`;
4. `docs/MEMORIA-V2-2026-08-03.txt`.

Não reintroduzir algo só porque aparece na memória V2.

## Autoria

**Theo é o criador, desenvolvedor principal e decisor final.** As IAs analisam,
programam, revisam, testam, explicam e documentam — não substituem a autoria
nem as decisões dele. Gustavo administra o projeto junto com Theo. Arthur é
colaborador criativo (sugestão não é aprovação). Weltton é participante
autorizado da área da equipe.

Nunca apresentar IA como autora dos jogos.

## Regras que não podem ser violadas

- **Não publicar, substituir, apagar ou alterar acesso do site público** sem
  autorização explícita.
- **Horizonte Engine própria e ferramenta própria de modelagem foram
  canceladas** (removidas em `d31144d`). Não recriar páginas, links, cards,
  demos ou promessas dessas ferramentas. Cuidado com dois falsos positivos:
  CSS órfão `.engine-*` em `app/globals.css` (confirmar referências antes de
  limpar, e como mudança técnica separada) e as variáveis `engine` em
  `app/horizonte-ia/mobile-chat.tsx`, que são do WebLLM e devem ficar.
  Referências educacionais a Unity, Blender e Unreal continuam válidas.
- **Correção do vídeo do Weltton deve ser preservada** (commits `e8c2c2e` e
  `8df019c`; migração `drizzle/0008_replace_task_video.sql`). A playlist só vale
  para a atividade `d772a2b0-284b-49bf-b419-786b120e4f17`. Cada card renderiza
  exclusivamente o `videoUrl` da própria atividade; nada de estado, chave ou
  cache compartilhado.
- **Não resetar banco** para resolver bug de interface ou dado pontual. Mudança
  de esquema exige migração nova, preservando dados. Não renomear nem remover
  migrações já aplicadas.
- **Não commitar credenciais, tokens, senhas ou dados privados.**
- Dados de produção (contas, hashes, sessões, tarefas, conversas, notificações,
  avaliações, anexos) vivem no D1/R2 e não estão no pacote. Não inventar
  registros.
- Mudanças pequenas, testáveis e fáceis de reverter. Nada é "concluído" sem
  teste proporcional ao risco.

## Arquitetura (conforme o handoff)

Node `>=22.13.0` · Next.js 16.2.6 · React 19.2.6 · TypeScript · Vinext + Vite ·
Cloudflare Workers · D1 (binding `DB`) · R2 (binding `BUCKET`) · Drizzle ORM.

Preservar `vinext()`, o plugin `sites()` e o plugin Cloudflare em
`vite.config.ts`; preservar `.openai/hosting.json` e os nomes dos bindings.
Não introduzir APIs exclusivas de Node que não rodem em Workers.

Arquivos centrais: `app/page.tsx` (página pública) · `app/globals.css` (sistema
visual) · `app/layout.tsx` · `app/horizonte-ia/` · `app/equipe/` ·
`app/api/equipe/` · `lib/team-auth.ts` · `lib/team-tasks.ts` ·
`lib/team-conversations.ts` · `lib/web-push.ts` · `db/schema.ts` · `drizzle/` ·
`.openai/hosting.json` · `public/` · `android-app/` ·
`tests/rendered-html.test.mjs`.

## Áreas do site

- **`/`** — navegação, apresentação, mascotes Hori (onça-pintada tecnológica) e
  Nexo (raposa robótica), divisões Studios/Games/Interactive, quatro pilares,
  catálogo de 12 projetos (o primeiro é *Criador de Heróis e Vilões*, no
  Roblox), destaque Horizonte IA, planos de aprendizagem, método, YouTube,
  área da equipe, pedido de participação, avaliações, FAQ e rodapé.
  O catálogo válido é o de `app/page.tsx`, não a lista antiga da memória V2.
- **`/horizonte-ia`** — chat no navegador (WebLLM/Transformers), memória e
  arquivos locais, PWA para iPhone/iPad, APKs Android 1.0.0–1.5.0 em
  `public/downloads/`, editor em `/horizonte-ia/editor`.
- **`/equipe`** — participantes `theo`, `arthur` (alias `artur`), `weltton`;
  senha criada no primeiro acesso, PBKDF2-SHA256 com salt; sessão em cookie
  `HttpOnly`/`Secure`/`SameSite=Lax` por sete dias; só Theo envia atividades;
  mensagens, notificações, presença e anexos (R2); dados em D1.

## Comandos

```bash
npm install
npm run dev
npm run build
npm test
npm run lint
```

`npm run db:generate` **somente** quando houver mudança deliberada em
`db/schema.ts` — nunca por rotina.

## Critério de conclusão de qualquer edição

1. mostrar os arquivos alterados;
2. explicar a mudança em linguagem clara;
3. rodar ao menos build e testes relevantes;
4. validar `/`, `/horizonte-ia` e `/equipe` contra regressão quando a mudança
   puder afetá-las;
5. confirmar que nenhum dado, autenticação, migração ou asset foi perdido;
6. não publicar sem autorização explícita;
7. registrar o que não pôde ser testado.
