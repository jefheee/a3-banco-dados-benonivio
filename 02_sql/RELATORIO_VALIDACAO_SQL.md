# Relatório de Validação SQL — `problemaescola vFinal` (`rbowxcvpcaqrycrvfowh`)

- **Data da Validação:** 2026-11-24
- **Projeto Alvo:** `problemaescola vFinal` (Organização: `biblioteca`)
- **Project Ref:** `rbowxcvpcaqrycrvfowh`
- **Engine:** PostgreSQL `17.11.0.003` (Supabase)
- **Execução confirmada:**
  - `01_migration_ajustes_vfinal.sql` (`Success. No rows returned`)
  - `02_views_publicas.sql` (`Success`)
  - `03_rls_policies.sql` (`Success. No rows returned`)
  - `04_seed_escola_benonivio.sql` (`Success. No rows returned`)
  - `05_crash_test_integridade.sql` (todos os 6 cenários de falha executados ao vivo e revertidos sem gravar linhas)
  - `06_consultas_apresentacao.sql` (todas as 8 consultas executadas ao vivo)

---

## 1. Estado Estrutural Pós-Consolidação (`public`)

| Objeto de Catálogo | Quantidade Atual | Detalhe Verificado |
|---|---:|---|
| Tabelas Base | **15** | Todas com RLS habilitado, PKs, FKs com `ON DELETE` explícito, `CHECK`s e `COMMENT ON` |
| Tipos `ENUM` | **5** | `importancia_enum`, `publicacao_status_enum`, `status_enum`, `turno_enum`, `usuario_role_enum` |
| `VIEW`s Públicas | **2** | `escola_avisos_publicos`, `escola_eventos_publicos` (ambas com `security_invoker = true`) |
| Funções | **3** | `escola_is_admin()`, `escola_is_editor()`, `trigger_set_updated_at()` (todas com `SET search_path = ''`; `escola_set_updated_at()` removida) |
| Índices | **38** | Índices redundantes removidos; índices compostos para listagens públicas criados |
| Políticas RLS | **70** | Políticas individuais por operação (`SELECT` `anon`, `SELECT`/`INSERT`/`UPDATE`/`DELETE` `authenticated`) |

### Resultado dos Advisors do Supabase
- **Performance Advisor:**
  - `multiple_permissive_policies`: **0 avisos** (reduzido de 15 para 0)
  - `auth_rls_initplan`: **0 avisos**
  - `unused_index`: `12` avisos informativos (`INFO`) normais em base recém-populada
- **Security Advisor:**
  - `function_search_path_mutable`: **0 avisos** (eliminado após remoção de `escola_set_updated_at`)
  - `rls_disabled_in_public`: **0 avisos**
  - `security_definer_view`: **0 avisos**
  - `authenticated_security_definer_function_executable`: `2` avisos (`WARN`) para `public.escola_is_admin()` e `public.escola_is_editor()`, mantidas propositalmente como helpers `STABLE SECURITY DEFINER` chamadas pelas políticas RLS de `authenticated` (evitando recursão em `escola_usuarios` e retornando apenas `boolean` para `(SELECT auth.uid())`).

---

## 2. Contagem Final de Registros (`COUNT(*)`)

| # | Tabela | Registros (`COUNT(*)`) |
|---:|---|---:|
| 1 | `escola_usuarios` | **4** |
| 2 | `escola_turmas` | **6** |
| 3 | `escola_whatsapp_grupos` | **5** |
| 4 | `escola_turmas_links` | **11** |
| 5 | `escola_turmas_posts` | **9** |
| 6 | `escola_avisos` | **6** |
| 7 | `escola_avisos_imagens` | **10** |
| 8 | `escola_acervo` | **4** |
| 9 | `escola_acervo_imagens` | **8** |
| 10 | `escola_documentos` | **6** |
| 11 | `escola_conteudo_paginas` | **4** |
| 12 | `escola_eventos` | **5** |
| 13 | `escola_turmas_eventos` | **11** |
| 14 | `escola_refeicoes` | **10** |
| 15 | `escola_notificacoes` | **3** |
| **Total** | **15 tabelas** | **102** |

---

## 3. Validação dos Crash Tests (`05_crash_test_integridade.sql`)

Todos os testes falharam exatamente nas constraints esperadas do PostgreSQL 17, sem persistir nenhum dado inválido:

| Teste | Regra Validada | `SQLSTATE` | Constraint Violada | Resultado |
|---|---|---:|---|---|
| **T1** | `UNIQUE` composta em `escola_turmas` | `23505` | `uq_turmas_ano_letivo_serie_nome_turno` | Bloqueado com sucesso |
| **T2** | `UNIQUE` composta em `escola_refeicoes` | `23505` | `uq_refeicoes_data_turno` | Bloqueado com sucesso |
| **T3** | `UNIQUE` 1:1 em `escola_whatsapp_grupos` | `23505` | `escola_whatsapp_grupos_turma_id_key` | Bloqueado com sucesso |
| **T4** | `CHECK` de data invertida em `escola_eventos` | `23514` | `ck_eventos_datas` | Bloqueado com sucesso |
| **T5a** | `CHECK` de formato de e-mail em `escola_usuarios` | `23514` | `ck_escola_usuarios_email_valido` | Bloqueado com sucesso |
| **T5b** | `CHECK` de nome em branco em `escola_usuarios` | `23514` | `escola_usuarios_nome_check` | Bloqueado com sucesso |
| **T5c** | `CHECK` de formato `slug` em `escola_conteudo_paginas` | `23514` | `ck_escola_conteudo_paginas_slug_formato` | Bloqueado com sucesso |
| **T6** | `FOREIGN KEY` de `turma_id` inexistente em `escola_turmas_posts` | `23503` | `escola_turmas_posts_turma_id_fkey` | Bloqueado com sucesso |

---

## 4. Validação das 8 Consultas DQL (`06_consultas_apresentacao.sql`)

| # | Consulta | Status | Resumo do Retorno Observado ao Vivo |
|---:|---|---|---|
| **1** | `JOIN` multi-tabela 3FN (Turmas 2026 + WhatsApp ativo + Links) | **OK** | 3 turmas de 2026 com grupo ativo retornadas (`101` = 3 links, `201` = 2 links, `301` = 3 links) |
| **2** | Agregação `COUNT`, `SUM`, `AVG` com `GROUP BY` em `escola_documentos` | **OK** | 4 categorias: `Pedagógico` (1 arq / 2.50 MB), `Calendários` (2 arq / 1.50 MB), `Editais` (2 arq / 1.34 MB), `Atas` (1 arq / 0.38 MB) |
| **3** | `MIN`/`MAX` + `COUNT` N:N em `escola_eventos` / `escola_turmas_eventos` | **OK** | 3 eventos ativos; mais próximo `2026-12-06`, mais distante `2027-02-02`; contagem correta de turmas por evento (`2`, `3`, `4`, `2`, `0`) |
| **4** | `GROUP BY` + `HAVING COUNT(l.id) >= 2` | **OK** | 4 turmas retornadas (`2026-101` com 3, `2026-301` com 3, `2026-201` com 2, `2025-101` com 2) |
| **5** | `LEFT JOIN` + `COALESCE` em `escola_turmas_posts` | **OK** | Todas as 6 turmas retornadas, incluindo `2026 - 901` (`0`) e `2025 - 101` (`0` publicados, pois seus 2 posts são arquivados) |
| **6** | `NOT EXISTS` (Turmas sem grupo de WhatsApp) | **OK** | 1 turma identificada: `2026 - 9º Ano Ensino Fundamental - 901 (matutino)` |
| **7** | Preservação Histórica (`2025` vs `2026`) | **OK** | `2025`: 2 turmas, 3 posts (1 pub, 2 arq); `2026`: 4 turmas, 6 posts (5 pub, 1 rasc) |
| **8** | Views Públicas (`escola_avisos_publicos` e `escola_eventos_publicos`) | **OK** | `escola_avisos`: 6 na base vs **4** na view; `escola_eventos`: 5 na base vs **3** na view (rascunhos, arquivados, inativos e expirados ocultados) |
