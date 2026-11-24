-- ============================================================================
-- 02_views_publicas.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: Criar as views publicas documentadas com security_invoker = true
--           para respeitar as politicas RLS das tabelas base.
-- ============================================================================

BEGIN;

CREATE OR REPLACE VIEW public.escola_avisos_publicos
WITH (security_invoker = true) AS
SELECT
  a.id,
  a.titulo,
  a.resumo,
  a.conteudo,
  a.categoria,
  a.imagem_url,
  a.importancia,
  a.destaque_home,
  a.data_publicacao,
  a.data_expiracao
FROM public.escola_avisos a
WHERE a.status = 'publicado'::public.publicacao_status_enum
  AND a.data_publicacao <= timezone('utc', now())
  AND (a.data_expiracao IS NULL OR a.data_expiracao > timezone('utc', now()));

COMMENT ON VIEW public.escola_avisos_publicos IS
  'Avisos publicos vigentes (status publicado, dentro da janela de exibicao) com security_invoker = true.';

CREATE OR REPLACE VIEW public.escola_eventos_publicos
WITH (security_invoker = true) AS
SELECT
  e.id,
  e.titulo,
  e.descricao,
  e.local,
  e.data_inicio,
  e.data_fim,
  e.dia_inteiro,
  e.imagem_url
FROM public.escola_eventos e
WHERE e.status = 'ativo'::public.status_enum;

COMMENT ON VIEW public.escola_eventos_publicos IS
  'Eventos escolares ativos destinados a exibicao publica no calendario com security_invoker = true.';

GRANT SELECT ON public.escola_avisos_publicos, public.escola_eventos_publicos TO anon, authenticated;

COMMIT;
