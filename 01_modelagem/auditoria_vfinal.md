# Auditoria Somente Leitura e Relatório de Gaps — `problemaescola vFinal` (`rbowxcvpcaqrycrvfowh`)

- **Data da Auditoria:** 2026-11-24
- **Projeto Alvo:** `problemaescola vFinal` (Organização: `biblioteca`)
- **Project Ref:** `rbowxcvpcaqrycrvfowh`
- **Engine:** PostgreSQL `17.11.0.003` (Supabase)
- **Migrations registradas (`supabase_migrations`):** `0` (lista vazia; schema aplicado diretamente via SQL)
- **Referências comparadas:**
  - `00_docs_originais/Dicionario_de_Dados_A3_EEB_Benonivio.docx` (modelo vFinal de 15 tabelas)
  - `00_docs_originais/A3 Banco de Dados __ Jefherson.docx.pdf` (especificação acadêmica anterior com 14 tabelas e 2 views)
  - `.agents/rules/database_architecture.md` (padrões arquiteturais obrigatórios)

---

## 1. Resumo Executivo do Estado Atual (`public`)

| Categoria | Quantidade Atual | Observação |
|---|---:|---|
| Tabelas base (`BASE TABLE`) | **15** | Nomes idênticos às 15 tabelas do `Dicionario_de_Dados_A3_EEB_Benonivio.docx` |
| Tipos `ENUM` | **5** | `importancia_enum`, `publicacao_status_enum`, `status_enum`, `turno_enum`, `usuario_role_enum` |
| `VIEW`s | **0** | `escola_avisos_publicos` e `escola_eventos_publicos` **não existem** |
| Funções (`pg_proc`) | **4** | `escola_is_admin`, `escola_is_editor`, `escola_set_updated_at` (órfã), `trigger_set_updated_at` |
| Triggers (`pg_trigger`) | **11** | Todas executam `trigger_set_updated_at()` em `BEFORE UPDATE` |
| Índices (`pg_index`) | **39** | 15 PKs, 4 `UNIQUE`s, 20 índices secundários (3 redundantes) |
| Políticas RLS (`pg_policies`) | **29** | RLS ativo nas 15 tabelas, porém com falhas graves de autorização e exposição de rascunhos |
| Comentários (`COMMENT ON`) | **0** | Nenhuma tabela ou coluna possui comentário no catálogo |
| Registros totais (`COUNT(*)`) | **17** | 1 registro por tabela, exceto `escola_avisos_imagens` (2) e `escola_turmas_links` (2) |

---

## 2. Inventário Exato do Banco Atual (`rbowxcvpcaqrycrvfowh`)

### 2.1. Contagem de Registros e Status RLS por Tabela

| # | Tabela (`public`) | Registros (`COUNT(*)`) | RLS Habilitado | RLS Forçado | Trigger `updated_at` | Comentário |
|---:|---|---:|:---:|:---:|:---:|---|
| 1 | `escola_usuarios` | 1 | `true` | `false` | `trg_escola_usuarios_updated_at` | `null` |
| 2 | `escola_avisos` | 1 | `true` | `false` | `trg_escola_avisos_updated_at` | `null` |
| 3 | `escola_avisos_imagens` | 2 | `true` | `false` | *(sem coluna `updated_at`)* | `null` |
| 4 | `escola_acervo` | 1 | `true` | `false` | `trg_escola_acervo_updated_at` | `null` |
| 5 | `escola_acervo_imagens` | 1 | `true` | `false` | *(sem coluna `updated_at`)* | `null` |
| 6 | `escola_documentos` | 1 | `true` | `false` | `trg_escola_documentos_updated_at` | `null` |
| 7 | `escola_conteudo_paginas` | 1 | `true` | `false` | `trg_escola_conteudo_paginas_updated_at` | `null` |
| 8 | `escola_turmas` | 1 | `true` | `false` | `trg_escola_turmas_updated_at` | `null` |
| 9 | `escola_turmas_links` | 2 | `true` | `false` | *(sem coluna `updated_at`)* | `null` |
| 10 | `escola_whatsapp_grupos` | 1 | `true` | `false` | `trg_escola_whatsapp_grupos_updated_at` | `null` |
| 11 | `escola_turmas_posts` | 1 | `true` | `false` | `trg_escola_turmas_posts_updated_at` | `null` |
| 12 | `escola_eventos` | 1 | `true` | `false` | `trg_escola_eventos_updated_at` | `null` |
| 13 | `escola_turmas_eventos` | 1 | `true` | `false` | *(sem coluna `updated_at`)* | `null` |
| 14 | `escola_refeicoes` | 1 | `true` | `false` | `trg_escola_refeicoes_updated_at` | `null` |
| 15 | `escola_notificacoes` | 1 | `true` | `false` | `trg_escola_notificacoes_updated_at` | `null` |

### 2.2. Tipos ENUM Existentes (`public`)

| ENUM | Valores (em ordem) |
|---|---|
| `importancia_enum` | `normal`, `importante`, `urgente` |
| `publicacao_status_enum` | `rascunho`, `publicado`, `arquivado` |
| `status_enum` | `ativo`, `inativo`, `expirado` |
| `turno_enum` | `matutino`, `vespertino`, `noturno`, `integral` |
| `usuario_role_enum` | `admin`, `editor` |

### 2.3. Colunas, Tipos, Nulabilidade e Defaults por Tabela

<details>
<summary>Expandir estrutura completa das 15 tabelas (extraída de <code>information_schema.columns</code>)</summary>

#### `escola_usuarios`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `nome` | `text` | `NO` | `null` |
| 3 | `email` | `text` | `NO` | `null` |
| 4 | `role` | `usuario_role_enum` | `NO` | `'editor'::usuario_role_enum` |
| 5 | `ativo` | `bool` | `NO` | `true` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 7 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_avisos`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `titulo` | `text` | `NO` | `null` |
| 3 | `resumo` | `text` | `NO` | `null` |
| 4 | `conteudo` | `text` | `YES` | `null` |
| 5 | `categoria` | `text` | `NO` | `null` |
| 6 | `imagem_url` | `text` | `YES` | `null` |
| 7 | `importancia` | `importancia_enum` | `NO` | `'normal'::importancia_enum` |
| 8 | `destaque_home` | `bool` | `NO` | `false` |
| 9 | `status` | `publicacao_status_enum` | `NO` | `'publicado'::publicacao_status_enum` |
| 10 | `data_publicacao` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 11 | `data_expiracao` | `timestamptz` | `YES` | `null` |
| 12 | `autor_id` | `uuid` | `YES` | `null` |
| 13 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 14 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_avisos_imagens`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `aviso_id` | `uuid` | `NO` | `null` |
| 3 | `url` | `text` | `NO` | `null` |
| 4 | `legenda` | `text` | `YES` | `null` |
| 5 | `ordem` | `int4` | `NO` | `0` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_acervo`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `ano` | `text` | `NO` | `null` |
| 3 | `categoria` | `text` | `NO` | `null` |
| 4 | `titulo` | `text` | `NO` | `null` |
| 5 | `descricao` | `text` | `YES` | `null` |
| 6 | `capa_url` | `text` | `YES` | `null` |
| 7 | `status` | `publicacao_status_enum` | `NO` | `'publicado'::publicacao_status_enum` |
| 8 | `data_publicacao` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 9 | `autor_id` | `uuid` | `YES` | `null` |
| 10 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 11 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_acervo_imagens`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `acervo_id` | `uuid` | `NO` | `null` |
| 3 | `url` | `text` | `NO` | `null` |
| 4 | `legenda` | `text` | `YES` | `null` |
| 5 | `ordem` | `int4` | `NO` | `0` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_documentos`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `titulo` | `text` | `NO` | `null` |
| 3 | `descricao` | `text` | `YES` | `null` |
| 4 | `categoria` | `text` | `NO` | `null` |
| 5 | `url_arquivo` | `text` | `NO` | `null` |
| 6 | `nome_arquivo` | `text` | `NO` | `null` |
| 7 | `mime_type` | `text` | `NO` | `null` |
| 8 | `tamanho_bytes` | `int8` | `NO` | `null` |
| 9 | `status` | `publicacao_status_enum` | `NO` | `'publicado'::publicacao_status_enum` |
| 10 | `autor_id` | `uuid` | `YES` | `null` |
| 11 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 12 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_conteudo_paginas`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `slug` | `text` | `NO` | `null` |
| 3 | `titulo` | `text` | `NO` | `null` |
| 4 | `resumo` | `text` | `YES` | `null` |
| 5 | `conteudo_html` | `text` | `YES` | `null` |
| 6 | `imagem_url` | `text` | `YES` | `null` |
| 7 | `publicado` | `bool` | `NO` | `true` |
| 8 | `autor_id` | `uuid` | `YES` | `null` |
| 9 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 10 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_turmas`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `ano_letivo` | `int4` | `NO` | `2026` |
| 3 | `ano` | `text` | `NO` | `null` |
| 4 | `nome` | `text` | `NO` | `null` |
| 5 | `turno` | `turno_enum` | `NO` | `null` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 7 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_turmas_links`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `turma_id` | `uuid` | `NO` | `null` |
| 3 | `titulo` | `text` | `NO` | `null` |
| 4 | `url` | `text` | `NO` | `null` |
| 5 | `ordem` | `int4` | `NO` | `0` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_whatsapp_grupos`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `turma_id` | `uuid` | `NO` | `null` |
| 3 | `nome` | `text` | `NO` | `null` |
| 4 | `link_convite` | `text` | `NO` | `null` |
| 5 | `ativo` | `bool` | `NO` | `true` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 7 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_turmas_posts`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `turma_id` | `uuid` | `NO` | `null` |
| 3 | `titulo` | `text` | `NO` | `null` |
| 4 | `resumo` | `text` | `YES` | `null` |
| 5 | `conteudo` | `text` | `YES` | `null` |
| 6 | `imagem_url` | `text` | `YES` | `null` |
| 7 | `link_referencia` | `text` | `YES` | `null` |
| 8 | `status` | `publicacao_status_enum` | `NO` | `'publicado'::publicacao_status_enum` |
| 9 | `data_publicacao` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 10 | `data_expiracao` | `timestamptz` | `YES` | `null` |
| 11 | `autor_id` | `uuid` | `YES` | `null` |
| 12 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 13 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_eventos`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `titulo` | `text` | `NO` | `null` |
| 3 | `descricao` | `text` | `YES` | `null` |
| 4 | `local` | `text` | `YES` | `null` |
| 5 | `data_inicio` | `timestamptz` | `NO` | `null` |
| 6 | `data_fim` | `timestamptz` | `YES` | `null` |
| 7 | `dia_inteiro` | `bool` | `NO` | `false` |
| 8 | `imagem_url` | `text` | `YES` | `null` |
| 9 | `status` | `status_enum` | `NO` | `'ativo'::status_enum` |
| 10 | `autor_id` | `uuid` | `YES` | `null` |
| 11 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 12 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_turmas_eventos`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `evento_id` | `uuid` | `NO` | `null` |
| 2 | `turma_id` | `uuid` | `NO` | `null` |
| 3 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_refeicoes`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `data` | `date` | `NO` | `null` |
| 3 | `turno` | `turno_enum` | `NO` | `null` |
| 4 | `descricao` | `text` | `NO` | `null` |
| 5 | `observacoes` | `text` | `YES` | `null` |
| 6 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 7 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

#### `escola_notificacoes`
| Pos | Coluna | Tipo (`udt_name`) | Nulo? | Default |
|---:|---|---|---:|---|
| 1 | `id` | `uuid` | `NO` | `gen_random_uuid()` |
| 2 | `titulo` | `text` | `NO` | `null` |
| 3 | `mensagem` | `text` | `NO` | `null` |
| 4 | `importancia` | `importancia_enum` | `NO` | `'normal'::importancia_enum` |
| 5 | `ativa` | `bool` | `NO` | `true` |
| 6 | `data_inicio` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 7 | `data_fim` | `timestamptz` | `YES` | `null` |
| 8 | `created_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |
| 9 | `updated_at` | `timestamptz` | `NO` | `timezone('utc'::text, now())` |

</details>

### 2.4. Constraints Existentes (`PK`, `FK`, `UNIQUE`, `CHECK`)

- **Chaves Primárias (`PRIMARY KEY`)**: Presentes nas 15 tabelas (`id` em 14 tabelas; composta `(evento_id, turma_id)` em `escola_turmas_eventos`).
- **Chaves Estrangeiras (`FOREIGN KEY`) — 13 FKs existentes**:

| Tabela | Constraint | Coluna | Referência | `ON UPDATE` | `ON DELETE` |
|---|---|---|---|---|---|
| `escola_acervo` | `escola_acervo_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_acervo_imagens` | `escola_acervo_imagens_acervo_id_fkey` | `acervo_id` | `escola_acervo(id)` | `NO ACTION` | `CASCADE` |
| `escola_avisos` | `escola_avisos_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_avisos_imagens` | `escola_avisos_imagens_aviso_id_fkey` | `aviso_id` | `escola_avisos(id)` | `NO ACTION` | `CASCADE` |
| `escola_conteudo_paginas` | `escola_conteudo_paginas_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_documentos` | `escola_documentos_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_eventos` | `escola_eventos_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_turmas_eventos` | `escola_turmas_eventos_evento_id_fkey` | `evento_id` | `escola_eventos(id)` | `NO ACTION` | `CASCADE` |
| `escola_turmas_eventos` | `escola_turmas_eventos_turma_id_fkey` | `turma_id` | `escola_turmas(id)` | `NO ACTION` | `CASCADE` |
| `escola_turmas_links` | `escola_turmas_links_turma_id_fkey` | `turma_id` | `escola_turmas(id)` | `NO ACTION` | `CASCADE` |
| `escola_turmas_posts` | `escola_turmas_posts_autor_id_fkey` | `autor_id` | `escola_usuarios(id)` | `NO ACTION` | `SET NULL` |
| `escola_turmas_posts` | `escola_turmas_posts_turma_id_fkey` | `turma_id` | `escola_turmas(id)` | `NO ACTION` | `CASCADE` |
| `escola_whatsapp_grupos` | `escola_whatsapp_grupos_turma_id_fkey` | `turma_id` | `escola_turmas(id)` | `NO ACTION` | `CASCADE` |

- **Restrições `UNIQUE` — 5 existentes**:
  - `escola_usuarios_email_key`: `UNIQUE (email)`
  - `escola_conteudo_paginas_slug_key`: `UNIQUE (slug)`
  - `uq_turmas_ano_letivo_serie_nome_turno`: `UNIQUE (ano_letivo, ano, nome, turno)`
  - `escola_whatsapp_grupos_turma_id_key`: `UNIQUE (turma_id)`
  - `uq_refeicoes_data_turno`: `UNIQUE (data, turno)`

- **Restrições `CHECK` — 32 existentes**:
  - **Intervalos de data (`4`)**: `ck_avisos_datas`, `ck_eventos_datas`, `ck_notificacoes_datas`, `ck_turmas_posts_datas` (todas usando `>=`, permitindo igualdade).
  - **Numéricas (`5`)**: `escola_acervo_imagens_ordem_check` (`ordem >= 0`), `escola_avisos_imagens_ordem_check` (`ordem >= 0`), `escola_turmas_links_ordem_check` (`ordem >= 0`), `escola_documentos_tamanho_bytes_check` (`tamanho_bytes >= 0`), `escola_turmas_ano_letivo_check` (`ano_letivo >= 2000`).
  - **E-mail normalizado (`1`)**: `escola_usuarios_email_check` (`email = lower(btrim(email))`).
  - **Textos não vazios (`22`)**: `length(btrim(col)) > 0` em colunas `NOT NULL` de texto (`ano`, `categoria`, `titulo`, `resumo`, `url`, `slug`, `nome_arquivo`, `mime_type`, `url_arquivo`, `mensagem`, `descricao`, `nome`, `link_convite`).

### 2.5. Índices Secundários Existentes (além de PKs e UNIQUEs)

| Tabela | Índice | Definição |
|---|---|---|
| `escola_acervo` | `ix_escola_acervo_autor` | `(autor_id)` |
| `escola_acervo_imagens` | `ix_escola_acervo_imagens_acervo` | `(acervo_id)` |
| `escola_avisos` | `ix_escola_avisos_autor` | `(autor_id)` |
| `escola_avisos` | `ix_escola_avisos_pub` | `(status, data_publicacao DESC)` |
| `escola_avisos_imagens` | `ix_escola_avisos_imagens_aviso` | `(aviso_id)` |
| `escola_conteudo_paginas` | `ix_escola_conteudo_paginas_autor` | `(autor_id)` |
| `escola_documentos` | `ix_escola_documentos_autor` | `(autor_id)` |
| `escola_documentos` | `ix_escola_documentos_cat` | `(categoria, status)` |
| `escola_eventos` | `ix_escola_eventos_autor` | `(autor_id)` |
| `escola_eventos` | `ix_escola_eventos_datas` | `(data_inicio, data_fim)` |
| `escola_notificacoes` | `ix_escola_notificacoes_ativa` | `(ativa, data_inicio, data_fim)` |
| `escola_refeicoes` | `ix_escola_refeicoes_data` | `(data)` *(redundante)* |
| `escola_turmas` | `ix_escola_turmas_ano_letivo` | `(ano_letivo, ano)` *(prefixo de `uq_turmas_...`)* |
| `escola_turmas_eventos` | `ix_escola_turmas_eventos_turma` | `(turma_id)` |
| `escola_turmas_links` | `ix_escola_turmas_links_turma` | `(turma_id)` |
| `escola_turmas_posts` | `ix_escola_turmas_posts_autor` | `(autor_id)` |
| `escola_turmas_posts` | `ix_escola_turmas_posts_pub` | `(turma_id, status, data_publicacao DESC)` |
| `escola_turmas_posts` | `ix_escola_turmas_posts_turma` | `(turma_id)` *(redundante)* |
| `escola_whatsapp_grupos` | `ix_escola_whatsapp_grupos_turma` | `(turma_id)` *(redundante)* |

### 2.6. Funções, Triggers e Views Existentes

- **Views**: `[]` (nenhuma view encontrada no schema `public`).
- **Funções**:
  1. `public.trigger_set_updated_at()` — `LANGUAGE plpgsql` (`SECURITY INVOKER`, sem `SET search_path`). Usada pelas 11 triggers.
  2. `public.escola_set_updated_at()` — `LANGUAGE plpgsql` (`SECURITY INVOKER`, sem `SET search_path`). **Função duplicada e sem uso.**
  3. `public.escola_is_admin()` — `LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO 'public'`. Checa `escola_usuarios` com `id = auth.uid() AND ativo = true AND role = 'admin'`. **Não usada em nenhuma política RLS.**
  4. `public.escola_is_editor()` — `LANGUAGE sql STABLE SECURITY DEFINER SET search_path TO 'public'`. Checa `escola_usuarios` com `id = auth.uid() AND ativo = true AND role IN ('admin', 'editor')`. **Não usada em nenhuma política RLS.**

### 2.7. Políticas RLS Atuais

- **14 tabelas de conteúdo/domínio** (`escola_acervo`, `escola_acervo_imagens`, `escola_avisos`, `escola_avisos_imagens`, `escola_conteudo_paginas`, `escola_documentos`, `escola_eventos`, `escola_notificacoes`, `escola_refeicoes`, `escola_turmas`, `escola_turmas_eventos`, `escola_turmas_links`, `escola_turmas_posts`, `escola_whatsapp_grupos`):
  1. `"Leitura publica permitida"` — `PERMISSIVE` | `FOR SELECT TO public` | `USING (true)`
  2. `"Gestao restrita a autenticados"` — `PERMISSIVE` | `FOR ALL TO authenticated` | `USING ((SELECT auth.uid()) IS NOT NULL)` | `WITH CHECK ((SELECT auth.uid()) IS NOT NULL)`
- **`escola_usuarios`**:
  1. `"Acesso autenticado aos usuarios"` — `PERMISSIVE` | `FOR ALL TO authenticated` | `USING ((SELECT auth.uid()) IS NOT NULL)` | `WITH CHECK ((SELECT auth.uid()) IS NOT NULL)`

---

## 3. Relatório de Gaps e Divergências (Priorizado)

### 3.1. Gaps Críticos (Segurança e Integridade Estrutural)

1. **RLS expõe dados não publicados para qualquer visitante anônimo (`anon` / `public`)**
   - **Estado atual:** `"Leitura publica permitida"` usa `USING (true)` em todas as 14 tabelas públicas.
   - **Impacto:** Rascunhos (`status = 'rascunho'`), arquivados (`status = 'arquivado'`), páginas ocultas (`publicado = false`), alertas desativados (`ativa = false`), eventos expirados e grupos inativos (`ativo = false`) ficam acessíveis via API REST do Supabase.
   - **Ação esperada:** Restringir `SELECT` para `anon` apenas a registros vigentes/publicados (ex.: `status = 'publicado' AND (data_expiracao IS NULL OR data_expiracao >= timezone('utc', now()))`, `publicado = true`, `ativa = true`, `ativo = true`, etc.), mantendo leitura total apenas para operadores autorizados (`escola_is_editor()`).

2. **RLS de escrita/gestão sem autorização por papel (`role`) ou status (`ativo`)**
   - **Estado atual:** `FOR ALL TO authenticated USING ((SELECT auth.uid()) IS NOT NULL)` permite que **qualquer usuário autenticado** (mesmo `ativo = false`, ou sem vínculo em `escola_usuarios`) crie, edite e exclua qualquer registro, incluindo **auto-promoção para `admin` em `escola_usuarios`**. As funções `escola_is_admin()` e `escola_is_editor()` existem no banco mas foram ignoradas.
   - **Ação esperada:** Separar políticas por operação (`SELECT`, `INSERT`, `UPDATE`, `DELETE` para `TO authenticated`, nunca `FOR ALL` genérico sobreposto), exigindo `(SELECT public.escola_is_admin())` em `escola_usuarios` (e eventual leitura do próprio perfil `id = (SELECT auth.uid())`) e `(SELECT public.escola_is_editor())` nas tabelas editoriais.

3. **Falta de `FOREIGN KEY` de `escola_usuarios(id)` para `auth.users(id)`**
   - **Estado atual:** `escola_usuarios.id` tem `DEFAULT gen_random_uuid()` e nenhuma FK ligando ao sistema de autenticação (`auth.users(id)`), divergindo do que está descrito no Dicionário (`integra-se à autenticação do sistema` / PDF `id referencia auth.users(id)`).
   - **Ação esperada:** Remover dependência de `gen_random_uuid()` em `escola_usuarios.id` (ou vincular `FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE`, após validar que o registro semente existente corresponde a um usuário em `auth.users`).

4. **Views Públicas Inexistentes (`escola_avisos_publicos` e `escola_eventos_publicos`)**
   - **Estado atual:** Nenhuma view existe em `public` (`0` views).
   - **Impacto:** Quebra compatibilidade com consultas ou documentação que esperam as 2 views de apresentação pública (`escola_avisos_publicos` e `escola_eventos_publicos`), além da necessidade de aplicar `WITH (security_invoker = true)` no PostgreSQL 17.
   - **Observação documental:** O `Dicionario_de_Dados_A3_EEB_Benonivio.docx` também omitiu a seção de Views (que constava no PDF anterior de 14 tabelas) — precisa ser atualizado junto com o SQL.

5. **Funções sem `SET search_path = ''` (Risco de Search Path Hijacking)**
   - **Estado atual:** `trigger_set_updated_at()` e `escola_set_updated_at()` não possuem `SET search_path = ''`; `escola_is_admin()` e `escola_is_editor()` usam `SET search_path TO 'public'` e `auth.uid()` direto (sem `(SELECT auth.uid())`). Além disso, `escola_set_updated_at()` está duplicada e sem uso.
   - **Ação esperada:** Unificar em uma única função `public.set_updated_at()` (ou manter `trigger_set_updated_at()` migrando com `SET search_path = ''` e removendo a função órfã), e ajustar `escola_is_admin()` / `escola_is_editor()` com `SET search_path = ''` e `(SELECT auth.uid())`.

---

### 3.2. Gaps de Constraints (`CHECK`, `UNIQUE`, `FK`)

| Tabela / Objeto | Gap Identificado | Detalhe Atual vs Esperado |
|---|---|---|
| `escola_usuarios.email` | Aceita string vazia `''` | Possui `CHECK (email = lower(btrim(email)))`, porém `'' = lower(btrim(''))` retorna `true`. Falta `CHECK (length(btrim(email)) > 0)` (e opcionalmente validação de formato `@`). |
| `escola_conteudo_paginas.slug` | Sem `CHECK` de formato de slug | Possui apenas `length(btrim(slug)) > 0`. Falta `CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$')` (documentado no PDF e exigido em `database_architecture.md`). |
| Colunas `text` anuláveis | Aceitam strings vazias ou só espaços (`'   '`) | Colunas como `conteudo`, `descricao`, `local`, `legenda`, `resumo`, `observacoes`, `imagem_url`, `capa_url`, `link_referencia` aceitam `''`. Recomenda-se `CHECK (col IS NULL OR length(btrim(col)) > 0)`. |
| `escola_avisos_imagens`, `escola_acervo_imagens`, `escola_turmas_links` | Sem `UNIQUE (pai_id, ordem)` | Permite cadastrar duas imagens ou links com a mesma `ordem = 0` dentro do mesmo pai (ou criar índice composto `(pai_id, ordem)`). |
| `escola_avisos`, `escola_turmas_posts`, `escola_eventos`, `escola_notificacoes` | `CHECK` de datas usa `>=` | Atualmente `data_fim >= data_inicio` (e `data_expiracao >= data_publicacao`). O Dicionário (`escola_eventos`, `escola_notificacoes`) aceita `>=`, enquanto o texto do PDF antigo falava em "posterior". Funcionalmente `>=` atende eventos instantâneos/mesma data, mas deve ser padronizado na documentação. |
| `escola_avisos.status`, `escola_acervo.status`, `escola_turmas_posts.status` | Default é `'publicado'` | No banco atual o default é `'publicado'`; verificar se a regra editorial prefere `'rascunho'` (como no PDF antigo) ou `'publicado'` (como na refatoração atual) e alinhar no Dicionário. |

---

### 3.3. Gaps de Índices (Performance Física)

1. **Índices redundantes a remover (3 redundâncias claras + 1 parcial):**
   - `escola_whatsapp_grupos`: `ix_escola_whatsapp_grupos_turma` é duplicata exata de `escola_whatsapp_grupos_turma_id_key` (`UNIQUE (turma_id)`).
   - `escola_refeicoes`: `ix_escola_refeicoes_data` é prefixo exato de `uq_refeicoes_data_turno (data, turno)`.
   - `escola_turmas_posts`: `ix_escola_turmas_posts_turma` é prefixo exato de `ix_escola_turmas_posts_pub (turma_id, status, data_publicacao DESC)`.
   - `escola_turmas`: `ix_escola_turmas_ano_letivo (ano_letivo, ano)` é prefixo de `uq_turmas_ano_letivo_serie_nome_turno (ano_letivo, ano, nome, turno)` (redundante para filtros por `ano_letivo` / `(ano_letivo, ano)`).

2. **Índices recomendados que estão ausentes:**
   - `escola_eventos`: criar índice composto `(status, data_inicio, data_fim)` para o calendário público (o atual `ix_escola_eventos_datas` não filtra `status`).
   - `escola_acervo`: criar índice composto `(status, ano, data_publicacao DESC)` para listagens filtradas por status/ano.
   - `escola_conteudo_paginas`: criar índice parcial/composto `(publicado, slug)` para resolução rápida de páginas públicas.
   - `escola_avisos_imagens (aviso_id, ordem)`, `escola_acervo_imagens (acervo_id, ordem)`, `escola_turmas_links (turma_id, ordem)`: substituem os índices simples apenas na FK, cobrindo simultaneamente a FK e o `ORDER BY ordem`.

> **Nota positiva sobre FKs:** Todas as 13 chaves estrangeiras atualmente declaradas no banco possuem cobertura de índice.

---

### 3.4. Gaps de Documentação Nativa e Consistência Documental

- **Catálogo PostgreSQL sem comentários (`0` `COMMENT ON`)**:
  - `database_architecture.md` exige `COMMENT ON TABLE` e `COMMENT ON COLUMN` para regras de negócio não óbvias. Hoje todas as 15 tabelas e todas as colunas têm comentário `null`.
- **Diferenças entre `Dicionario_de_Dados_A3_EEB_Benonivio.docx` e o banco real**:
  1. **Views**: O Dicionário Word não lista `escola_avisos_publicos` e `escola_eventos_publicos`, e o banco também não as possui.
  2. **FK de `escola_usuarios`**: O Dicionário cita integração de `id` com a autenticação do sistema, mas o DDL atual do banco não tem FK para `auth.users(id)`.
  3. **Defaults não explícitos no Word**: O Dicionário Word omite a coluna "Valor padrão" (presente no PDF antigo), deixando implícitos defaults como `ano_letivo = 2026`, `status = 'publicado'`, `role = 'editor'`, `ordem = 0`.
  4. **Nomes padronizados de constraints/índices**: As constraints geradas automaticamente (`escola_avisos_titulo_check`, `escola_usuarios_email_key`, etc.) misturam nomenclatura implícita do Postgres com prefixos explícitos (`ck_avisos_datas`, `uq_turmas_...`), diferindo parcialmente da convenção `pk_<table>`, `uq_<table>_<cols>`, `ck_<table>_<regra>`, `fk_<table>_<ref>`, `ix_<table>_<cols>` de `.agents/rules/database_architecture.md`.

---

## 4. Checklist de Ações Recomendadas (Próximos Passos em `02_sql/`)

1. **Migration incremental limpa (`BEGIN; ... COMMIT;`)** em `rbowxcvpcaqrycrvfowh` para:
   - Padronizar função única `public.set_updated_at()` com `SET search_path = ''` e remover `escola_set_updated_at()`.
   - Endurecer `escola_is_admin()` e `escola_is_editor()` com `SET search_path = ''` e `(SELECT auth.uid())`.
   - Adicionar `CHECK` de `email` não vazio em `escola_usuarios`, `CHECK` de formato de `slug` em `escola_conteudo_paginas`, e `CHECK`s de strings opcionais não vazias.
   - Avaliar/aplicar `FK escola_usuarios(id) -> auth.users(id) ON DELETE CASCADE` (verificando antes o `id` do registro existente em `escola_usuarios`).
   - Remover os 3–4 índices redundantes e criar os índices compostos orientados às consultas públicas e ordenação de galerias/links.
   - Criar as 2 views públicas (`escola_avisos_publicos` e `escola_eventos_publicos`) com `WITH (security_invoker = true)`.
   - Corrigir todas as políticas RLS separando `SELECT` público (somente dados publicados/ativos/vigentes) de `SELECT`/`INSERT`/`UPDATE`/`DELETE` autenticados (restritos a `escola_is_editor()` / `escola_is_admin()`).
   - Adicionar `COMMENT ON TABLE` e `COMMENT ON COLUMN` nas regras de negócio.
2. **Atualizar Dicionário Unificado e DBML/Mermaid** em `01_modelagem/` refletindo exatamente o schema final consolidado.
3. **Criar scripts separados em `02_sql/`** (DDL final, Views, RLS, Seed idempotente, Crash Tests com `ROLLBACK` e Consultas DQL para apresentação ao vivo).
