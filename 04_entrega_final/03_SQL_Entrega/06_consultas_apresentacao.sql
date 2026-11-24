-- ============================================================================
-- 06_consultas_apresentacao.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: 8 consultas DQL analiticas para execucao ao vivo na apresentacao A3.
-- ============================================================================

-- 1. JOIN multi-tabela (3FN em acao):
--    Turmas de 2026 com grupo de WhatsApp ativo e quantidade de links complementares.
SELECT
  t.ano_letivo,
  t.ano AS serie,
  t.nome AS turma,
  t.turno,
  w.nome AS grupo_whatsapp,
  w.link_convite,
  COUNT(l.id) AS total_links
FROM public.escola_turmas t
INNER JOIN public.escola_whatsapp_grupos w
  ON w.turma_id = t.id
 AND w.ativo = true
LEFT JOIN public.escola_turmas_links l
  ON l.turma_id = t.id
WHERE t.ano_letivo = 2026
GROUP BY t.id, t.ano_letivo, t.ano, t.nome, t.turno, w.nome, w.link_convite
ORDER BY t.turno, t.nome;

-- 2. Agregacao (COUNT, SUM, AVG) com GROUP BY:
--    Resumo de documentos oficiais por categoria (quantidade, total em MB e media em KB).
SELECT
  d.categoria,
  COUNT(*) AS qtd_arquivos,
  ROUND(SUM(d.tamanho_bytes) / 1048576.0, 2) AS total_mb,
  ROUND(AVG(d.tamanho_bytes) / 1024.0, 1) AS media_kb
FROM public.escola_documentos d
GROUP BY d.categoria
ORDER BY total_mb DESC, d.categoria;

-- 3. Agregacao (MIN e MAX) + N:N:
--    3a) Evento ativo mais proximo e mais distante no calendario escolar.
SELECT
  MIN(e.data_inicio) AS evento_mais_proximo,
  MAX(e.data_inicio) AS evento_mais_distante,
  COUNT(*) AS total_eventos_ativos
FROM public.escola_eventos e
WHERE e.status = 'ativo'::public.status_enum;

--    3b) Total de turmas participantes por evento (provando a associativa N:N).
SELECT
  e.titulo AS evento,
  e.status,
  e.data_inicio,
  COUNT(te.turma_id) AS qtd_turmas_participantes,
  STRING_AGG(t.ano_letivo || ' - ' || t.nome || ' (' || t.turno::text || ')', ', ' ORDER BY t.ano_letivo, t.nome) AS turmas
FROM public.escola_eventos e
LEFT JOIN public.escola_turmas_eventos te
  ON te.evento_id = e.id
LEFT JOIN public.escola_turmas t
  ON t.id = te.turma_id
GROUP BY e.id, e.titulo, e.status, e.data_inicio
ORDER BY e.data_inicio;

-- 4. GROUP BY + HAVING:
--    Listar apenas turmas que possuem 2 ou mais links complementares cadastrados.
SELECT
  t.ano_letivo,
  t.ano AS serie,
  t.nome AS turma,
  t.turno,
  COUNT(l.id) AS total_links
FROM public.escola_turmas t
INNER JOIN public.escola_turmas_links l
  ON l.turma_id = t.id
GROUP BY t.id, t.ano_letivo, t.ano, t.nome, t.turno
HAVING COUNT(l.id) >= 2
ORDER BY total_links DESC, t.ano_letivo DESC, t.nome;

-- 5. LEFT JOIN + COALESCE:
--    Todas as turmas e contagem de posts publicados (exibindo 0 sem omitir turmas).
SELECT
  t.ano_letivo,
  t.ano AS serie,
  t.nome AS turma,
  t.turno,
  COALESCE(COUNT(p.id), 0) AS posts_publicados
FROM public.escola_turmas t
LEFT JOIN public.escola_turmas_posts p
  ON p.turma_id = t.id
 AND p.status = 'publicado'::public.publicacao_status_enum
GROUP BY t.id, t.ano_letivo, t.ano, t.nome, t.turno
ORDER BY t.ano_letivo DESC, posts_publicados DESC, t.nome;

-- 6. NOT EXISTS (Ausencia):
--    Identificar turmas que ainda nao possuem grupo de WhatsApp cadastrado.
SELECT
  t.id,
  t.ano_letivo,
  t.ano AS serie,
  t.nome AS turma,
  t.turno
FROM public.escola_turmas t
WHERE NOT EXISTS (
  SELECT 1
  FROM public.escola_whatsapp_grupos w
  WHERE w.turma_id = t.id
)
ORDER BY t.ano_letivo DESC, t.nome;

-- 7. Preservacao Historica (Virada de Ano):
--    Comparar volume de turmas e postagens entre ano_letivo = 2025 e ano_letivo = 2026.
SELECT
  t.ano_letivo,
  COUNT(DISTINCT t.id) AS qtd_turmas,
  COUNT(p.id) AS total_posts,
  COUNT(p.id) FILTER (WHERE p.status = 'publicado'::public.publicacao_status_enum) AS posts_publicados,
  COUNT(p.id) FILTER (WHERE p.status = 'rascunho'::public.publicacao_status_enum) AS posts_rascunho,
  COUNT(p.id) FILTER (WHERE p.status = 'arquivado'::public.publicacao_status_enum) AS posts_arquivados
FROM public.escola_turmas t
LEFT JOIN public.escola_turmas_posts p
  ON p.turma_id = t.id
WHERE t.ano_letivo IN (2025, 2026)
GROUP BY t.ano_letivo
ORDER BY t.ano_letivo;

-- 8. Consulta nas Views Publicas vs Tabelas Base:
--    Prova que rascunhos, arquivados, expirados e inativos ficam ocultos nas Views.
SELECT
  'escola_avisos' AS entidade,
  (SELECT COUNT(*) FROM public.escola_avisos) AS total_tabela_base,
  (SELECT COUNT(*) FROM public.escola_avisos_publicos) AS total_view_publica
UNION ALL
SELECT
  'escola_eventos' AS entidade,
  (SELECT COUNT(*) FROM public.escola_eventos) AS total_tabela_base,
  (SELECT COUNT(*) FROM public.escola_eventos_publicos) AS total_view_publica;

SELECT id, titulo, categoria, importancia, destaque_home, data_publicacao, data_expiracao
FROM public.escola_avisos_publicos
ORDER BY destaque_home DESC, data_publicacao DESC;

SELECT id, titulo, local, data_inicio, data_fim, dia_inteiro
FROM public.escola_eventos_publicos
ORDER BY data_inicio;
