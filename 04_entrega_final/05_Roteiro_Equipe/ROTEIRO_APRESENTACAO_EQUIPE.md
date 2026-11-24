# Roteiro de Apresentação — Avaliação A3 (Banco de Dados)

- **Projeto:** Portal Escolar EEB Prof. Benonívio João Martins (`problemaescola vFinal` · `rbowxcvpcaqrycrvfowh`)
- **Disciplina:** Banco de Dados — UNISUL (Campus Pedra Branca, 2026)
- **Professores:** Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves
- **Tempo Total:** ~12 minutos (~3 minutos por integrante)

---

## Checklist — 5 Minutos Antes de Apresentar

1. **Aba 1 (Navegador):** Abrir `https://escolabenonivio.vercel.app` para a demonstração rápida de 30s na abertura.
2. **Aba 2 (Supabase SQL Editor):** Deixar `05_crash_test_integridade.sql` aberto no projeto `problemaescola vFinal` (conferir a URL antes de rodar).
3. **Aba 3 (Supabase SQL Editor):** Deixar `06_consultas_apresentacao.sql` pronto em outra aba.
4. **Projeção:** Abrir `04_entrega_final/02_Apresentacao_A3_Portal_Escolar.pptx` (e deixar o `.pdf` como backup).
5. **Documento de Apoio:** Ter `04_entrega_final/01_Dicionario_de_Dados_A3_EEB_Benonivio.pdf` aberto para consulta rápida na fala do Daniel.

---

## Divisão das Falas (Cola para Celular)

### 1. Jefherson Luiz — Abertura, Diagnóstico e Segurança (00:00 – 03:00)

- **Portal real (30s):** Mostra `escolabenonivio.vercel.app` no navegador. Explica que é um portal real da EEB Benonívio (Palhoça/SC) que rodava com 9 tabelas e vários arrays JSONB.
- **Slide 2 e 3 (Antes vs. Depois):**
  - Antes: JSONB sem integridade, sem `ano_letivo` nas turmas, turno repetido no WhatsApp, RLS `USING (true)` expondo rascunhos.
  - Depois: **15 tabelas (3FN)**, **5 ENUMs**, **13 FKs**, **2 Views** e **70 políticas RLS**.
- **Slide 6 (Segurança no SGBD):**
  - Visitante anônimo (`anon`) só enxerga conteúdo `publicado` / `ativo` dentro da vigência.
  - Edição restrita a operadores ativos (`escola_is_editor()` e `escola_is_admin()`).
  - Views públicas usam `WITH (security_invoker = true)` no PostgreSQL 17.
- **Gancho:** *"O Daniel vai mostrar como estruturamos essas 15 entidades no Dicionário e nos diagramas."*

---

### 2. Daniel Alves — Normalização, Dicionário e DER (03:00 – 06:00)

- **Slide 4 (1FN, 2FN, 3FN):**
  - **1FN:** Fim do JSONB — fotos e links viraram tabelas filhas (`escola_avisos_imagens`, `escola_acervo_imagens`, `escola_turmas_links`) com `ordem >= 0` e `UNIQUE (pai_id, ordem)`.
  - **2FN:** Eventos e turmas (N:N) ligam-se pela associativa `escola_turmas_eventos` com PK composta `(evento_id, turma_id)`.
  - **3FN:** Tiramos `turno` de `escola_whatsapp_grupos` (vem por `JOIN` da turma) e colocamos `ano_letivo` em `escola_turmas` para preservar 2025 e 2026 sem sobrescrever nada.
- **Slide 5 + PDF do Dicionário:**
  - Aponta os 5 subsistemas no DER (`dbdiagram.io`) e resume as cardinalidades:
    - **1:1:** Turma e Grupo de WhatsApp (`turma_id` `UNIQUE`).
    - **1:N:** Usuário para publicações (`ON DELETE SET NULL`), Aviso/Acervo para imagens e Turma para links/posts (`ON DELETE CASCADE`).
    - **N:N:** Evento para Turma via `escola_turmas_eventos`.
- **Gancho:** *"Agora o Maicon vai provar ao vivo no Supabase que o banco barra qualquer dado inválido."*

---

### 3. Maicon Lodetti — Crash Tests ao Vivo (06:00 – 09:00)

- **Slide 7 + SQL Editor (`05_crash_test_integridade.sql`):**
  - Explica que cada teste roda em `BEGIN; ... ROLLBACK;` para provar a trava sem sujar o banco.
  - Descomentar e rodar ao vivo 3 ou 4 testes:
    1. **T1 (`23505`):** Tentar duplicar a turma `2026 / 1º Ano Ensino Médio / 101 / matutino` → `uq_turmas_ano_letivo_serie_nome_turno` bloqueia.
    2. **T3 (`23505`):** Tentar cadastrar 2º grupo de WhatsApp para a mesma turma → `escola_whatsapp_grupos_turma_id_key` bloqueia.
    3. **T4 (`23514`):** Tentar criar evento com `data_fim < data_inicio` → `ck_eventos_datas` bloqueia.
    4. **T5c ou T6 (`23514` / `23503`):** Slug com espaço (`ck_escola_conteudo_paginas_slug_formato`) ou post para `turma_id` inexistente (`escola_turmas_posts_turma_id_fkey`).
- **Gancho:** *"Com a integridade provada, o Gabriel mostra os 102 registros e as consultas analíticas ao vivo."*

---

### 4. Gabriel Grando — Consultas DQL ao Vivo e Fechamento (09:00 – 12:00)

- **Slides 8 e 9 + SQL Editor (`06_consultas_apresentacao.sql`):**
  - Destaca que o seed populou **102 registros** nas 15 tabelas com **0 alertas** de políticas duplicadas ou `search_path` mutável.
  - Executa ao vivo as consultas destaque:
    - **Q1 (JOIN 3FN):** Turmas de 2026 com grupo de WhatsApp ativo e contagem de links.
    - **Q2 (`COUNT`, `SUM`, `AVG`):** Documentos por categoria em MB e média em KB.
    - **Q4 (`GROUP BY` + `HAVING`):** Só turmas com 2 ou mais links (`HAVING COUNT(l.id) >= 2`).
    - **Q5 e Q6 (`LEFT JOIN` + `COALESCE` e `NOT EXISTS`):** Mostra a turma `2026-901` aparecendo com `0` posts publicados e sendo localizada pelo `NOT EXISTS` por não ter WhatsApp.
    - **Q7 e Q8 (Histórico + Views):** Compara `2025` vs. `2026` e prova que `escola_avisos_publicos` retorna `4` de `6` e `escola_eventos_publicos` retorna `3` de `5`.
- **Slide 10 (Fechamento):**
  - Próximo passo pós-A3: ETL controlado do legado para o schema 3FN e atualização das queries em `lib/data/` no Next.js.

---

## Cola de Defesa — 8 Perguntas Prováveis dos Professores

1. **Qual a diferença entre DDL, DML e DQL no projeto?**
   - **DDL:** `CREATE TABLE`, `ALTER TABLE`, `CREATE VIEW`, `CREATE INDEX` (`00_ddl_completo_do_zero.sql`).
   - **DML:** `INSERT`, `UPDATE`, `DELETE` (`04_seed_escola_benonivio.sql`).
   - **DQL:** `SELECT` com `JOIN`, `GROUP BY`, `HAVING`, `NOT EXISTS` (`06_consultas_apresentacao.sql`).

2. **Por que remover JSONB de imagens e links se o PostgreSQL suporta JSONB?**
   - Porque listas de imagens e links têm ciclo de vida próprio, ordenação (`ordem`) e exigem validação individual (`NOT NULL`, `UNIQUE (pai_id, ordem)`). Armazenar lista em JSONB viola a **1FN** e impede chaves estrangeiras nativas.

3. **Qual a diferença entre `WHERE` e `HAVING`?**
   - `WHERE` filtra linhas individuais **antes** do `GROUP BY`; `HAVING` filtra grupos agregados **depois** do `GROUP BY` (ex.: `HAVING COUNT(l.id) >= 2`).

4. **Por que usar `NOT EXISTS` em vez de `NOT IN` na Consulta 6?**
   - `NOT IN` falha silenciosamente e retorna zero linhas se houver qualquer `NULL` na subconsulta; `NOT EXISTS` é imune a `NULL` e permite *anti-join* eficiente no otimizador do PostgreSQL.

5. **Quando vocês usaram `ON DELETE CASCADE` vs. `ON DELETE SET NULL`?**
   - `CASCADE` apenas em entidades dependentes fracas (imagens de aviso/acervo, links, posts, WhatsApp da turma, vínculos N:N).
   - `SET NULL` nas 6 FKs de `autor_id`, preservando os registros institucionais caso um operador seja excluído.

6. **O que faz `WITH (security_invoker = true)` nas Views públicas?**
   - Faz a View executar com as permissões e políticas RLS de quem consulta (`anon` ou `authenticated`), evitando que uma View contorne o RLS do criador (`security_definer`).

7. **Por que `escola_usuarios` não apaga avisos quando um autor sai, e para que serve `ativo`?**
   - O campo `ativo` permite bloqueio imediato do operador nas funções `escola_is_admin()` e `escola_is_editor()` sem apagar seu histórico. Mesmo em remoção física, `ON DELETE SET NULL` preserva os documentos e avisos da escola.

8. **Por que colocar `ano_letivo` na chave única de `escola_turmas`?**
   - Porque todo ano existe uma turma `"101 - 1º Ano Ensino Médio - Matutino"`. Sem `ano_letivo` na `UNIQUE (ano_letivo, ano, nome, turno)`, a virada de 2025 para 2026 sobrescreveria os dados ou geraria duplicidade ambígua.
