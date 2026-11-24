-- ============================================================================
-- 03_rls_policies.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: Refatorar politicas RLS nas 15 tabelas separando leitura publica
--           (apenas dados publicados/ativos/vigentes) de leitura completa e
--           escrita administrativa (escola_is_editor / escola_is_admin).
-- ============================================================================

BEGIN;

-- Remover todas as politicas permissivas legadas
DO $$
DECLARE
  pol record;
BEGIN
  FOR pol IN
    SELECT schemaname, tablename, policyname
    FROM pg_catalog.pg_policies
    WHERE schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I.%I;', pol.policyname, pol.schemaname, pol.tablename);
  END LOOP;
END $$;

-- Garantir RLS habilitado nas 15 tabelas
ALTER TABLE public.escola_usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_avisos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_avisos_imagens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_acervo ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_acervo_imagens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_documentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_conteudo_paginas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_turmas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_turmas_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_whatsapp_grupos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_turmas_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_turmas_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_refeicoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escola_notificacoes ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------------------------
-- 1. escola_usuarios (sem leitura anonima; gestao exclusiva de admin ativo)
-- ----------------------------------------------------------------------------
CREATE POLICY "usuarios_select_own_or_admin"
  ON public.escola_usuarios
  FOR SELECT
  TO authenticated
  USING (
    id = (SELECT auth.uid())
    OR (SELECT public.escola_is_admin())
  );

CREATE POLICY "usuarios_insert_admin"
  ON public.escola_usuarios
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_admin()));

CREATE POLICY "usuarios_update_admin"
  ON public.escola_usuarios
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_admin()))
  WITH CHECK ((SELECT public.escola_is_admin()));

CREATE POLICY "usuarios_delete_admin"
  ON public.escola_usuarios
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_admin()));

-- ----------------------------------------------------------------------------
-- 2. escola_avisos
-- ----------------------------------------------------------------------------
CREATE POLICY "avisos_select_anon_publicos"
  ON public.escola_avisos
  FOR SELECT
  TO anon
  USING (
    status = 'publicado'::public.publicacao_status_enum
    AND data_publicacao <= timezone('utc', now())
    AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))
  );

CREATE POLICY "avisos_select_authenticated"
  ON public.escola_avisos
  FOR SELECT
  TO authenticated
  USING (
    (
      status = 'publicado'::public.publicacao_status_enum
      AND data_publicacao <= timezone('utc', now())
      AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "avisos_insert_editor"
  ON public.escola_avisos
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "avisos_update_editor"
  ON public.escola_avisos
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "avisos_delete_editor"
  ON public.escola_avisos
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 3. escola_avisos_imagens (somente se o aviso pai estiver publicado/vigente)
-- ----------------------------------------------------------------------------
CREATE POLICY "avisos_imagens_select_anon_publicos"
  ON public.escola_avisos_imagens
  FOR SELECT
  TO anon
  USING (
    EXISTS (
      SELECT 1
      FROM public.escola_avisos a
      WHERE a.id = aviso_id
        AND a.status = 'publicado'::public.publicacao_status_enum
        AND a.data_publicacao <= timezone('utc', now())
        AND (a.data_expiracao IS NULL OR a.data_expiracao > timezone('utc', now()))
    )
  );

CREATE POLICY "avisos_imagens_select_authenticated"
  ON public.escola_avisos_imagens
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.escola_avisos a
      WHERE a.id = aviso_id
        AND a.status = 'publicado'::public.publicacao_status_enum
        AND a.data_publicacao <= timezone('utc', now())
        AND (a.data_expiracao IS NULL OR a.data_expiracao > timezone('utc', now()))
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "avisos_imagens_insert_editor"
  ON public.escola_avisos_imagens
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "avisos_imagens_update_editor"
  ON public.escola_avisos_imagens
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "avisos_imagens_delete_editor"
  ON public.escola_avisos_imagens
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 4. escola_acervo
-- ----------------------------------------------------------------------------
CREATE POLICY "acervo_select_anon_publicos"
  ON public.escola_acervo
  FOR SELECT
  TO anon
  USING (
    status = 'publicado'::public.publicacao_status_enum
    AND data_publicacao <= timezone('utc', now())
  );

CREATE POLICY "acervo_select_authenticated"
  ON public.escola_acervo
  FOR SELECT
  TO authenticated
  USING (
    (
      status = 'publicado'::public.publicacao_status_enum
      AND data_publicacao <= timezone('utc', now())
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "acervo_insert_editor"
  ON public.escola_acervo
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "acervo_update_editor"
  ON public.escola_acervo
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "acervo_delete_editor"
  ON public.escola_acervo
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 5. escola_acervo_imagens (somente se o acervo pai estiver publicado)
-- ----------------------------------------------------------------------------
CREATE POLICY "acervo_imagens_select_anon_publicos"
  ON public.escola_acervo_imagens
  FOR SELECT
  TO anon
  USING (
    EXISTS (
      SELECT 1
      FROM public.escola_acervo ac
      WHERE ac.id = acervo_id
        AND ac.status = 'publicado'::public.publicacao_status_enum
        AND ac.data_publicacao <= timezone('utc', now())
    )
  );

CREATE POLICY "acervo_imagens_select_authenticated"
  ON public.escola_acervo_imagens
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1
      FROM public.escola_acervo ac
      WHERE ac.id = acervo_id
        AND ac.status = 'publicado'::public.publicacao_status_enum
        AND ac.data_publicacao <= timezone('utc', now())
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "acervo_imagens_insert_editor"
  ON public.escola_acervo_imagens
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "acervo_imagens_update_editor"
  ON public.escola_acervo_imagens
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "acervo_imagens_delete_editor"
  ON public.escola_acervo_imagens
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 6. escola_documentos
-- ----------------------------------------------------------------------------
CREATE POLICY "documentos_select_anon_publicos"
  ON public.escola_documentos
  FOR SELECT
  TO anon
  USING (status = 'publicado'::public.publicacao_status_enum);

CREATE POLICY "documentos_select_authenticated"
  ON public.escola_documentos
  FOR SELECT
  TO authenticated
  USING (
    status = 'publicado'::public.publicacao_status_enum
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "documentos_insert_editor"
  ON public.escola_documentos
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "documentos_update_editor"
  ON public.escola_documentos
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "documentos_delete_editor"
  ON public.escola_documentos
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 7. escola_conteudo_paginas
-- ----------------------------------------------------------------------------
CREATE POLICY "conteudo_paginas_select_anon_publicos"
  ON public.escola_conteudo_paginas
  FOR SELECT
  TO anon
  USING (publicado = true);

CREATE POLICY "conteudo_paginas_select_authenticated"
  ON public.escola_conteudo_paginas
  FOR SELECT
  TO authenticated
  USING (
    publicado = true
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "conteudo_paginas_insert_editor"
  ON public.escola_conteudo_paginas
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "conteudo_paginas_update_editor"
  ON public.escola_conteudo_paginas
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "conteudo_paginas_delete_editor"
  ON public.escola_conteudo_paginas
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 8. escola_turmas (leitura publica; gestao editor/admin)
-- ----------------------------------------------------------------------------
CREATE POLICY "turmas_select_publico"
  ON public.escola_turmas
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "turmas_insert_editor"
  ON public.escola_turmas
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_update_editor"
  ON public.escola_turmas
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_delete_editor"
  ON public.escola_turmas
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 9. escola_turmas_links (leitura publica; gestao editor/admin)
-- ----------------------------------------------------------------------------
CREATE POLICY "turmas_links_select_publico"
  ON public.escola_turmas_links
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "turmas_links_insert_editor"
  ON public.escola_turmas_links
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_links_update_editor"
  ON public.escola_turmas_links
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_links_delete_editor"
  ON public.escola_turmas_links
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 10. escola_whatsapp_grupos (apenas ativo = true para publico)
-- ----------------------------------------------------------------------------
CREATE POLICY "whatsapp_grupos_select_anon_ativos"
  ON public.escola_whatsapp_grupos
  FOR SELECT
  TO anon
  USING (ativo = true);

CREATE POLICY "whatsapp_grupos_select_authenticated"
  ON public.escola_whatsapp_grupos
  FOR SELECT
  TO authenticated
  USING (
    ativo = true
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "whatsapp_grupos_insert_editor"
  ON public.escola_whatsapp_grupos
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "whatsapp_grupos_update_editor"
  ON public.escola_whatsapp_grupos
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "whatsapp_grupos_delete_editor"
  ON public.escola_whatsapp_grupos
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 11. escola_turmas_posts
-- ----------------------------------------------------------------------------
CREATE POLICY "turmas_posts_select_anon_publicos"
  ON public.escola_turmas_posts
  FOR SELECT
  TO anon
  USING (
    status = 'publicado'::public.publicacao_status_enum
    AND data_publicacao <= timezone('utc', now())
    AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))
  );

CREATE POLICY "turmas_posts_select_authenticated"
  ON public.escola_turmas_posts
  FOR SELECT
  TO authenticated
  USING (
    (
      status = 'publicado'::public.publicacao_status_enum
      AND data_publicacao <= timezone('utc', now())
      AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "turmas_posts_insert_editor"
  ON public.escola_turmas_posts
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_posts_update_editor"
  ON public.escola_turmas_posts
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_posts_delete_editor"
  ON public.escola_turmas_posts
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 12. escola_eventos (apenas status = 'ativo' para publico)
-- ----------------------------------------------------------------------------
CREATE POLICY "eventos_select_anon_ativos"
  ON public.escola_eventos
  FOR SELECT
  TO anon
  USING (status = 'ativo'::public.status_enum);

CREATE POLICY "eventos_select_authenticated"
  ON public.escola_eventos
  FOR SELECT
  TO authenticated
  USING (
    status = 'ativo'::public.status_enum
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "eventos_insert_editor"
  ON public.escola_eventos
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "eventos_update_editor"
  ON public.escola_eventos
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "eventos_delete_editor"
  ON public.escola_eventos
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 13. escola_turmas_eventos (leitura publica; gestao editor/admin)
-- ----------------------------------------------------------------------------
CREATE POLICY "turmas_eventos_select_publico"
  ON public.escola_turmas_eventos
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "turmas_eventos_insert_editor"
  ON public.escola_turmas_eventos
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_eventos_update_editor"
  ON public.escola_turmas_eventos
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "turmas_eventos_delete_editor"
  ON public.escola_turmas_eventos
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 14. escola_refeicoes (leitura publica; gestao editor/admin)
-- ----------------------------------------------------------------------------
CREATE POLICY "refeicoes_select_publico"
  ON public.escola_refeicoes
  FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "refeicoes_insert_editor"
  ON public.escola_refeicoes
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "refeicoes_update_editor"
  ON public.escola_refeicoes
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "refeicoes_delete_editor"
  ON public.escola_refeicoes
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

-- ----------------------------------------------------------------------------
-- 15. escola_notificacoes (apenas ativa = true e dentro da janela temporal)
-- ----------------------------------------------------------------------------
CREATE POLICY "notificacoes_select_anon_ativas"
  ON public.escola_notificacoes
  FOR SELECT
  TO anon
  USING (
    ativa = true
    AND data_inicio <= timezone('utc', now())
    AND (data_fim IS NULL OR data_fim >= timezone('utc', now()))
  );

CREATE POLICY "notificacoes_select_authenticated"
  ON public.escola_notificacoes
  FOR SELECT
  TO authenticated
  USING (
    (
      ativa = true
      AND data_inicio <= timezone('utc', now())
      AND (data_fim IS NULL OR data_fim >= timezone('utc', now()))
    )
    OR (SELECT public.escola_is_editor())
  );

CREATE POLICY "notificacoes_insert_editor"
  ON public.escola_notificacoes
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "notificacoes_update_editor"
  ON public.escola_notificacoes
  FOR UPDATE
  TO authenticated
  USING ((SELECT public.escola_is_editor()))
  WITH CHECK ((SELECT public.escola_is_editor()));

CREATE POLICY "notificacoes_delete_editor"
  ON public.escola_notificacoes
  FOR DELETE
  TO authenticated
  USING ((SELECT public.escola_is_editor()));

COMMIT;
