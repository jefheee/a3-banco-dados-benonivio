# Roteiro de Apresentação — Avaliação A3 (Banco de Dados)

- **Projeto:** Modelagem, Normalização e Implementação Relacional do Portal Escolar — **EEB Prof. Benonívio João Martins**
- **Disciplina:** Banco de Dados — UNISUL (Campus Pedra Branca, 2026)
- **Professor:** Henrique Pereira Oliveira D'Eça Neves
- **Tempo Total Alvo:** ~12 minutos (divisão equilibrada: ~3 minutos por integrante)
- **Ambiente ao Vivo:**
  - Portal em produção (demonstração rápida): `https://escolabenonivio.vercel.app`
  - Banco homologado da A3 (Supabase / PostgreSQL 17): projeto **`problemaescola vFinal`** (`rbowxcvpcaqrycrvfowh`)
  - Scripts no SQL Editor: `02_sql/05_crash_test_integridade.sql` e `02_sql/06_consultas_apresentacao.sql`

---

## Cronograma e Divisão de Falas

| Ordem | Integrante | Tempo | Slides | Foco Principal |
|---:|---|---:|---|---|
| 1 | **Jefherson Luiz** | 00:00 – 03:00 (3 min) | Slides 1, 2, 3 e 6 | Abertura no portal real, diagnóstico Antes vs. Depois e arquitetura/segurança (RLS + Views) |
| 2 | **Daniel Alves** | 03:00 – 06:00 (3 min) | Slides 4 e 5 + DOCX | Dicionário de Dados Unificado, Normalização (1FN/2FN/3FN), DER e cardinalidades (1:1, 1:N, N:N) |
| 3 | **Maicon Lodetti** | 06:00 – 09:00 (3 min) | Slide 7 + SQL Editor | Execução ao vivo dos **Crash Tests** (`05_crash_test_integridade.sql`) |
| 4 | **Gabriel Grando** | 09:00 – 12:00 (3 min) | Slides 8, 9 e 10 + SQL Editor | Execução ao vivo das **Consultas DQL** (`06_consultas_apresentacao.sql`), evidências e fechamento |

---

## Roteiro Detalhado por Integrante

### 1. Jefherson Luiz — Abertura, Diagnóstico e Segurança (~3 min)
- **Slides 1 e 2 (00:00 – 01:00):**
  - Cumprimenta a turma e o professor Henrique.
  - Mostra rapidamente (30 segundos) o portal real `escolabenonivio.vercel.app` no navegador: *"Esse é um sistema real que construímos para a EEB Prof. Benonívio João Martins, aqui da região. Hoje ele roda em produção, mas o banco inicial foi criado às pressas com 9 tabelas e vários arrays em JSONB."*
- **Slide 3 — Antes vs. Depois (01:00 – 02:00):**
  - Explica a refatoração: saímos de 9 tabelas com JSONB e sem controle histórico de ano letivo para **15 tabelas normalizadas até a 3FN**, **5 tipos ENUM**, **13 FKs explícitas**, **2 Views públicas** e **70 políticas RLS**.
- **Slide 6 — Integridade e Segurança no SGBD (02:00 – 03:00):**
  - Destaca que a regra de negócio foi blindada dentro do PostgreSQL: `CHECK` contra strings vazias e datas invertidas, `UNIQUE` naturais, `ON DELETE CASCADE` vs. `SET NULL`, triggers automáticas de `updated_at` e Views com `security_invoker = true` respeitando RLS.
  - Passa a palavra para o **Daniel**: *"O Daniel vai detalhar como organizamos essas 15 entidades no Dicionário de Dados e nos diagramas."*

### 2. Daniel Alves — Dicionário de Dados, Normalização e DER (~3 min)
- **Slide 4 — Normalização na Prática (03:00 – 04:30):**
  - **1FN:** Fim dos atributos multivalorados em JSONB — galerias de imagens viraram `escola_avisos_imagens` e `escola_acervo_imagens`; links das turmas viraram `escola_turmas_links`, todos com `ordem >= 0` e `UNIQUE (pai_id, ordem)`.
  - **2FN:** Relacionamento N:N entre eventos e turmas resolvido pela associativa `escola_turmas_eventos` com PK composta `(evento_id, turma_id)`.
  - **3FN:** Remoção da coluna transitiva `turno` de `escola_whatsapp_grupos` (pois o turno pertence à turma e é obtido por `JOIN`) e inclusão de `ano_letivo` em `escola_turmas` para virar o ano letivo sem sobrescrever o histórico.
- **Slide 5 + Dicionário (`Dicionario_de_Dados_A3_FINAL.docx`) (04:30 – 06:00):**
  - Exibe rapidamente o Dicionário de Dados (padrão de 6 colunas + restrições reais + 5 ENUMs + 13 FKs) e aponta no DER os 5 subsistemas e cardinalidades:
    - **1:1:** `escola_turmas` ↔ `escola_whatsapp_grupos` (`turma_id` com `UNIQUE`).
    - **1:N:** `escola_usuarios` → publicações, `escola_avisos` → imagens, `escola_turmas` → links/posts.
    - **N:N:** `escola_eventos` ↔ `escola_turmas` via `escola_turmas_eventos`.
  - Passa a palavra para o **Maicon**: *"Agora o Maicon vai provar ao vivo no Supabase que essas restrições realmente impedem dados inválidos."*

### 3. Maicon Lodetti — Crash Tests ao Vivo (~3 min)
- **Slide 7 + Supabase SQL Editor (`02_sql/05_crash_test_integridade.sql`) (06:00 – 09:00):**
  - Explica: *"Em vez de confiar apenas no formulário do frontend, colocamos barreiras físicas no SGBD. Vou rodar ao vivo os testes de falha intencional."*
  - Executa 3 a 4 testes selecionados no SQL Editor (descomentando um bloco `BEGIN; ... ROLLBACK;` por vez):
    1. **Teste 1 (`23505`):** Tentar duplicar a turma `2026 / 1º Ano Ensino Médio / 101 / matutino` → barrada por `uq_turmas_ano_letivo_serie_nome_turno`.
    2. **Teste 3 (`23505`):** Tentar cadastrar um segundo grupo de WhatsApp para a mesma turma → barrada pela `UNIQUE` 1:1 `escola_whatsapp_grupos_turma_id_key`.
    3. **Teste 4 (`23514`):** Tentar criar evento com `data_fim < data_inicio` → barrada por `ck_eventos_datas`.
    4. **Teste 5c / 6 (`23514` / `23503`):** Tentar inserir `slug` com espaço/maiúscula (`ck_escola_conteudo_paginas_slug_formato`) ou post com `turma_id` inexistente (`escola_turmas_posts_turma_id_fkey`).
  - Mostra rapidamente que os demais testes (`T2` cardápio duplicado e `T5a/b` e-mail/nome em branco) seguem o mesmo rigor.
  - Passa a palavra para o **Gabriel**: *"Com o banco protegido contra lixo, o Gabriel vai mostrar os 102 registros populados e as consultas analíticas ao vivo."*

### 4. Gabriel Grando — Consultas DQL ao Vivo e Fechamento (~3 min)
- **Slides 8 e 9 + Supabase SQL Editor (`02_sql/06_consultas_apresentacao.sql`) (09:00 – 11:30):**
  - Destaca que o banco foi populado com **102 registros reais** em 15 tabelas (cobrindo 2025 e 2026) e **0 alertas críticos** nos Advisors.
  - Executa ao vivo as consultas destaque:
    - **Q1 (JOIN 3FN):** Lista turmas de `2026` trazendo o grupo de WhatsApp ativo e a contagem de links (sem coluna redundante `turno` na tabela de WhatsApp).
    - **Q2 (`COUNT`, `SUM`, `AVG`):** Documentos por categoria com total em MB e média em KB.
    - **Q4 (`GROUP BY` + `HAVING`):** Apenas turmas com `>= 2` links complementares (`HAVING COUNT(l.id) >= 2`).
    - **Q5 e Q6 (`LEFT JOIN` + `COALESCE` e `NOT EXISTS`):** Mostra que a turma `2026 - 901` aparece com `0` posts publicados (sem sumir do relatório) e é localizada automaticamente pelo `NOT EXISTS` por ainda não ter grupo de WhatsApp.
    - **Q7 e Q8 (Histórico + Views):** Compara `2025` vs. `2026` e prova que `escola_avisos_publicos` retorna `4` de `6` avisos e `escola_eventos_publicos` retorna `3` de `5` eventos (ocultando rascunhos, arquivados e expirados).
- **Slide 10 — Próximos Passos e Encerramento (11:30 – 12:00):**
  - Explica a etapa pós-A3: migração controlada (ETL) do banco legado em produção para esse schema 3FN e atualização das queries do Next.js (`lib/data/`).
  - Agradece ao professor e abre para perguntas.

---

## Cola de Defesa — 8 Perguntas Prováveis do Professor

1. **Qual a diferença entre DDL, DML e DQL no projeto de vocês?**
   - **DDL** (*Data Definition Language*): `CREATE TABLE`, `ALTER TABLE`, `CREATE VIEW`, `CREATE INDEX` — define a estrutura (`00_ddl_completo_do_zero.sql` e `01_migration_ajustes_vfinal.sql`).
   - **DML** (*Data Manipulation Language*): `INSERT`, `UPDATE`, `DELETE` — manipula os dados (`04_seed_escola_benonivio.sql`).
   - **DQL** (*Data Query Language*): `SELECT` com `JOIN`, `GROUP BY`, `HAVING`, subconsultas — consulta e gera informação (`06_consultas_apresentacao.sql`).

2. **Por que vocês tiraram o `JSONB` de imagens e links se o PostgreSQL suporta `JSONB` bem?**
   - Porque listas de imagens e links têm **ciclo de vida próprio, ordenação (`ordem`) e exigem integridade individual** (como `NOT NULL` em `url` e `UNIQUE (pai_id, ordem)`). Armazená-las em `JSONB` viola a **1ª Forma Normal (1FN)** (atributo multivalorado), impede FKs nativas e dificulta consultas/ordenação relacionais em SQL padrão.

3. **Qual a diferença entre `WHERE` e `HAVING` (usado na Consulta 4)?**
   - `WHERE` filtra **linhas individuais antes** do agrupamento (`GROUP BY`).
   - `HAVING` filtra **grupos já agregados depois** do `GROUP BY` — por isso usamos `HAVING COUNT(l.id) >= 2` para retornar só turmas com 2 ou mais links.

4. **Por que usaram `NOT EXISTS` na Consulta 6 em vez de `NOT IN`?**
   - Além de otimizar melhor com *anti-join* no PostgreSQL, `NOT IN` tem a armadilha clássica do **`NULL`**: se a subconsulta retornar qualquer `NULL`, `NOT IN` avalia tudo como `UNKNOWN` e devolve 0 linhas. `NOT EXISTS` é imune a `NULL` e expressa diretamente ausência relacional.

5. **Qual a diferença entre `ON DELETE CASCADE` e `ON DELETE SET NULL` no esquema de vocês?**
   - **`CASCADE`** foi usado apenas em **entidades fracas/dependentes** que não fazem sentido isoladas: se um aviso é apagado, suas fotos (`escola_avisos_imagens`) somem; se um evento ou turma é apagado, o vínculo em `escola_turmas_eventos` é removido.
   - **`SET NULL`** foi usado nas 6 FKs de **`autor_id`**: se um operador sair da escola e for removido, o aviso, documento ou evento institucional **permanece preservado**, ficando apenas com `autor_id = NULL`.

6. **O que faz `WITH (security_invoker = true)` nas Views públicas?**
   - Por padrão no PostgreSQL, uma View executa com as permissões de quem a **criou** (`security_definer`), podendo contornar o RLS das tabelas base. Com `security_invoker = true` (PostgreSQL 15+), a View executa com as permissões e políticas RLS de quem está **consultando** (`anon` ou `authenticated`), eliminando risco de vazamento.

7. **Por que `escola_usuarios` não apaga o conteúdo quando um professor/gestor deixa a escola, e por que existe a coluna `ativo`?**
   - Primeiro, porque a coluna `ativo` permite **desativação lógica** imediata sem perder rastreabilidade de quem publicou os comunicados (`escola_is_admin()` e `escola_is_editor()` exigem `ativo = true`). Segundo, mesmo em remoção física, `ON DELETE SET NULL` garante que o histórico público da escola não seja destruído em cascata.

8. **Por que incluir `ano_letivo` na chave única de `escola_turmas`?**
   - Todo ano a escola tem uma turma `"101 - 1º Ano Ensino Médio - Matutino"`. Sem `ano_letivo` na chave candidata `UNIQUE (ano_letivo, ano, nome, turno)`, a escola teria que sobrescrever a turma na virada de 2025 para 2026 ou permitir duplicatas ambíguas. Com `ano_letivo`, cada ano letivo tem sua identidade única em 3FN e o histórico de posts/eventos de 2025 fica 100% preservado.
