-- ============================================================================
-- 05_crash_test_integridade.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: 6 testes de falha intencional (Crash Tests) para demonstrar na
--           apresentacao que UNIQUE, CHECK e FOREIGN KEY bloqueiam dados
--           invalidos na camada do SGBD sem depender do frontend.
--
-- COMO USAR NA APRESENTACAO:
--   Descomente e execute UM bloco por vez (cada bloco termina em ROLLBACK;
--   e, caso falhe conforme esperado, nenhum registro e gravado no banco).
--   Abaixo de cada teste consta o erro exato retornado ao vivo pelo PostgreSQL
--   17.11 no projeto rbowxcvpcaqrycrvfowh.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TESTE 1: Violacao de UNIQUE composta em escola_turmas
--          (mesmo ano_letivo, serie, nome e turno)
-- ----------------------------------------------------------------------------
/*
BEGIN;
  INSERT INTO public.escola_turmas (ano_letivo, ano, nome, turno)
  VALUES (2026, '1º Ano Ensino Médio', '101', 'matutino');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23505
--   CONSTRAINT: uq_turmas_ano_letivo_serie_nome_turno
--   MESSAGE: duplicate key value violates unique constraint "uq_turmas_ano_letivo_serie_nome_turno"

-- ----------------------------------------------------------------------------
-- TESTE 2: Violacao de UNIQUE composta em escola_refeicoes
--          (dois cardapios para o mesmo dia e turno)
-- ----------------------------------------------------------------------------
/*
BEGIN;
  INSERT INTO public.escola_refeicoes (data, turno, descricao)
  VALUES (CURRENT_DATE, 'matutino', 'Cardápio duplicado no mesmo dia e turno');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23505
--   CONSTRAINT: uq_refeicoes_data_turno
--   MESSAGE: duplicate key value violates unique constraint "uq_refeicoes_data_turno"

-- ----------------------------------------------------------------------------
-- TESTE 3: Violacao de UNIQUE 1:1 em escola_whatsapp_grupos
--          (tentar cadastrar segundo grupo de WhatsApp para a mesma turma)
-- ----------------------------------------------------------------------------
/*
BEGIN;
  INSERT INTO public.escola_whatsapp_grupos (turma_id, nome, link_convite)
  SELECT t.id, 'Segundo Grupo Mesma Turma', 'https://chat.whatsapp.com/duplicado'
  FROM public.escola_turmas t
  WHERE t.ano_letivo = 2026 AND t.nome = '101'
  LIMIT 1;
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23505
--   CONSTRAINT: escola_whatsapp_grupos_turma_id_key
--   MESSAGE: duplicate key value violates unique constraint "escola_whatsapp_grupos_turma_id_key"

-- ----------------------------------------------------------------------------
-- TESTE 4: Violacao de CHECK de data invertida em escola_eventos
--          (data_fim anterior a data_inicio)
-- ----------------------------------------------------------------------------
/*
BEGIN;
  INSERT INTO public.escola_eventos (titulo, data_inicio, data_fim)
  VALUES ('Evento com Data Invertida', '2026-11-20 10:00:00+00', '2026-11-19 10:00:00+00');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23514
--   CONSTRAINT: ck_eventos_datas
--   MESSAGE: new row for relation "escola_eventos" violates check constraint "ck_eventos_datas"

-- ----------------------------------------------------------------------------
-- TESTE 5: Violacao de CHECK de texto em branco / e-mail invalido / slug invalido
-- ----------------------------------------------------------------------------
-- 5a) E-mail invalido em escola_usuarios:
/*
BEGIN;
  INSERT INTO public.escola_usuarios (nome, email)
  VALUES ('Operador Teste', 'Email Invalido');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23514
--   CONSTRAINT: ck_escola_usuarios_email_valido
--   MESSAGE: new row for relation "escola_usuarios" violates check constraint "ck_escola_usuarios_email_valido"

-- 5b) Nome apenas com espacos em branco em escola_usuarios:
/*
BEGIN;
  INSERT INTO public.escola_usuarios (nome, email)
  VALUES ('   ', 'teste.valido@eebbenonivio.sc.gov.br');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23514
--   CONSTRAINT: escola_usuarios_nome_check
--   MESSAGE: new row for relation "escola_usuarios" violates check constraint "escola_usuarios_nome_check"

-- 5c) Slug fora do padrao kebab-case em escola_conteudo_paginas:
/*
BEGIN;
  INSERT INTO public.escola_conteudo_paginas (slug, titulo)
  VALUES ('Pagina Com Espaco!', 'Página Inválida');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23514
--   CONSTRAINT: ck_escola_conteudo_paginas_slug_formato
--   MESSAGE: new row for relation "escola_conteudo_paginas" violates check constraint "ck_escola_conteudo_paginas_slug_formato"

-- ----------------------------------------------------------------------------
-- TESTE 6: Violacao de FOREIGN KEY em escola_turmas_posts
--          (tentar inserir post para uma turma_id UUID inexistente)
-- ----------------------------------------------------------------------------
/*
BEGIN;
  INSERT INTO public.escola_turmas_posts (turma_id, titulo)
  VALUES ('00000000-0000-0000-0000-000000000000', 'Post para Turma Inexistente');
ROLLBACK;
*/
-- Erro real retornado pelo PostgreSQL:
--   SQLSTATE: 23503
--   CONSTRAINT: escola_turmas_posts_turma_id_fkey
--   MESSAGE: insert or update on table "escola_turmas_posts" violates foreign key constraint "escola_turmas_posts_turma_id_fkey"
