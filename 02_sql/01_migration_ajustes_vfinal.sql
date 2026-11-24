-- ============================================================================
-- 01_migration_ajustes_vfinal.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: Migration incremental de endurecimento estrutural, seguranca de
--           funcoes, constraints faltantes, limpeza de indices e metadados.
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Funcoes utilitarias e de autorizacao (SET search_path = '')
-- ----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS public.escola_set_updated_at();

CREATE OR REPLACE FUNCTION public.trigger_set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = ''
AS $$
BEGIN
  NEW.updated_at := timezone('utc', now());
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.escola_is_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.escola_usuarios u
    WHERE u.id = (SELECT auth.uid())
      AND u.ativo = true
      AND u.role = 'admin'::public.usuario_role_enum
  );
$$;

CREATE OR REPLACE FUNCTION public.escola_is_editor()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.escola_usuarios u
    WHERE u.id = (SELECT auth.uid())
      AND u.ativo = true
      AND u.role IN ('admin'::public.usuario_role_enum, 'editor'::public.usuario_role_enum)
  );
$$;

REVOKE ALL ON FUNCTION public.escola_is_admin() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.escola_is_admin() TO authenticated;

REVOKE ALL ON FUNCTION public.escola_is_editor() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.escola_is_editor() TO authenticated;

-- ----------------------------------------------------------------------------
-- 2. Higienizacao preventiva de strings opcionais vazias -> NULL
-- ----------------------------------------------------------------------------
UPDATE public.escola_avisos
SET conteudo   = NULLIF(btrim(conteudo), ''),
    imagem_url = NULLIF(btrim(imagem_url), '')
WHERE (conteudo IS NOT NULL AND btrim(conteudo) = '')
   OR (imagem_url IS NOT NULL AND btrim(imagem_url) = '');

UPDATE public.escola_avisos_imagens
SET legenda = NULLIF(btrim(legenda), '')
WHERE legenda IS NOT NULL AND btrim(legenda) = '';

UPDATE public.escola_acervo
SET descricao = NULLIF(btrim(descricao), ''),
    capa_url  = NULLIF(btrim(capa_url), '')
WHERE (descricao IS NOT NULL AND btrim(descricao) = '')
   OR (capa_url IS NOT NULL AND btrim(capa_url) = '');

UPDATE public.escola_acervo_imagens
SET legenda = NULLIF(btrim(legenda), '')
WHERE legenda IS NOT NULL AND btrim(legenda) = '';

UPDATE public.escola_documentos
SET descricao = NULLIF(btrim(descricao), '')
WHERE descricao IS NOT NULL AND btrim(descricao) = '';

UPDATE public.escola_conteudo_paginas
SET resumo        = NULLIF(btrim(resumo), ''),
    conteudo_html = NULLIF(btrim(conteudo_html), ''),
    imagem_url    = NULLIF(btrim(imagem_url), '')
WHERE (resumo IS NOT NULL AND btrim(resumo) = '')
   OR (conteudo_html IS NOT NULL AND btrim(conteudo_html) = '')
   OR (imagem_url IS NOT NULL AND btrim(imagem_url) = '');

UPDATE public.escola_turmas_posts
SET resumo          = NULLIF(btrim(resumo), ''),
    conteudo        = NULLIF(btrim(conteudo), ''),
    imagem_url      = NULLIF(btrim(imagem_url), ''),
    link_referencia = NULLIF(btrim(link_referencia), '')
WHERE (resumo IS NOT NULL AND btrim(resumo) = '')
   OR (conteudo IS NOT NULL AND btrim(conteudo) = '')
   OR (imagem_url IS NOT NULL AND btrim(imagem_url) = '')
   OR (link_referencia IS NOT NULL AND btrim(link_referencia) = '');

UPDATE public.escola_eventos
SET descricao  = NULLIF(btrim(descricao), ''),
    local      = NULLIF(btrim(local), ''),
    imagem_url = NULLIF(btrim(imagem_url), '')
WHERE (descricao IS NOT NULL AND btrim(descricao) = '')
   OR (local IS NOT NULL AND btrim(local) = '')
   OR (imagem_url IS NOT NULL AND btrim(imagem_url) = '');

UPDATE public.escola_refeicoes
SET observacoes = NULLIF(btrim(observacoes), '')
WHERE observacoes IS NOT NULL AND btrim(observacoes) = '';

-- ----------------------------------------------------------------------------
-- 3. Constraints faltantes e reforcadas
-- ----------------------------------------------------------------------------

-- Em producao, descomentar o vinculo rigido com auth.users(id):
-- ALTER TABLE public.escola_usuarios
--   ADD CONSTRAINT fk_escola_usuarios_auth_users
--   FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.escola_usuarios
  DROP CONSTRAINT IF EXISTS escola_usuarios_email_check,
  DROP CONSTRAINT IF EXISTS ck_escola_usuarios_email_valido,
  ADD CONSTRAINT ck_escola_usuarios_email_valido
    CHECK (
      length(btrim(email)) > 3
      AND email = lower(btrim(email))
      AND email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
    );

ALTER TABLE public.escola_conteudo_paginas
  DROP CONSTRAINT IF EXISTS ck_escola_conteudo_paginas_slug_formato,
  ADD CONSTRAINT ck_escola_conteudo_paginas_slug_formato
    CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$');

ALTER TABLE public.escola_avisos
  DROP CONSTRAINT IF EXISTS ck_escola_avisos_conteudo_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_avisos_imagem_url_not_blank,
  ADD CONSTRAINT ck_escola_avisos_conteudo_not_blank
    CHECK (conteudo IS NULL OR length(btrim(conteudo)) > 0),
  ADD CONSTRAINT ck_escola_avisos_imagem_url_not_blank
    CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0);

ALTER TABLE public.escola_avisos_imagens
  DROP CONSTRAINT IF EXISTS ck_escola_avisos_imagens_legenda_not_blank,
  ADD CONSTRAINT ck_escola_avisos_imagens_legenda_not_blank
    CHECK (legenda IS NULL OR length(btrim(legenda)) > 0);

ALTER TABLE public.escola_acervo
  DROP CONSTRAINT IF EXISTS ck_escola_acervo_descricao_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_acervo_capa_url_not_blank,
  ADD CONSTRAINT ck_escola_acervo_descricao_not_blank
    CHECK (descricao IS NULL OR length(btrim(descricao)) > 0),
  ADD CONSTRAINT ck_escola_acervo_capa_url_not_blank
    CHECK (capa_url IS NULL OR length(btrim(capa_url)) > 0);

ALTER TABLE public.escola_acervo_imagens
  DROP CONSTRAINT IF EXISTS ck_escola_acervo_imagens_legenda_not_blank,
  ADD CONSTRAINT ck_escola_acervo_imagens_legenda_not_blank
    CHECK (legenda IS NULL OR length(btrim(legenda)) > 0);

ALTER TABLE public.escola_documentos
  DROP CONSTRAINT IF EXISTS ck_escola_documentos_descricao_not_blank,
  ADD CONSTRAINT ck_escola_documentos_descricao_not_blank
    CHECK (descricao IS NULL OR length(btrim(descricao)) > 0);

ALTER TABLE public.escola_conteudo_paginas
  DROP CONSTRAINT IF EXISTS ck_escola_conteudo_paginas_resumo_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_conteudo_paginas_html_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_conteudo_paginas_imagem_url_not_blank,
  ADD CONSTRAINT ck_escola_conteudo_paginas_resumo_not_blank
    CHECK (resumo IS NULL OR length(btrim(resumo)) > 0),
  ADD CONSTRAINT ck_escola_conteudo_paginas_html_not_blank
    CHECK (conteudo_html IS NULL OR length(btrim(conteudo_html)) > 0),
  ADD CONSTRAINT ck_escola_conteudo_paginas_imagem_url_not_blank
    CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0);

ALTER TABLE public.escola_turmas_posts
  DROP CONSTRAINT IF EXISTS ck_escola_turmas_posts_resumo_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_turmas_posts_conteudo_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_turmas_posts_imagem_url_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_turmas_posts_link_ref_not_blank,
  ADD CONSTRAINT ck_escola_turmas_posts_resumo_not_blank
    CHECK (resumo IS NULL OR length(btrim(resumo)) > 0),
  ADD CONSTRAINT ck_escola_turmas_posts_conteudo_not_blank
    CHECK (conteudo IS NULL OR length(btrim(conteudo)) > 0),
  ADD CONSTRAINT ck_escola_turmas_posts_imagem_url_not_blank
    CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0),
  ADD CONSTRAINT ck_escola_turmas_posts_link_ref_not_blank
    CHECK (link_referencia IS NULL OR length(btrim(link_referencia)) > 0);

ALTER TABLE public.escola_eventos
  DROP CONSTRAINT IF EXISTS ck_escola_eventos_descricao_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_eventos_local_not_blank,
  DROP CONSTRAINT IF EXISTS ck_escola_eventos_imagem_url_not_blank,
  ADD CONSTRAINT ck_escola_eventos_descricao_not_blank
    CHECK (descricao IS NULL OR length(btrim(descricao)) > 0),
  ADD CONSTRAINT ck_escola_eventos_local_not_blank
    CHECK (local IS NULL OR length(btrim(local)) > 0),
  ADD CONSTRAINT ck_escola_eventos_imagem_url_not_blank
    CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0);

ALTER TABLE public.escola_refeicoes
  DROP CONSTRAINT IF EXISTS ck_escola_refeicoes_observacoes_not_blank,
  ADD CONSTRAINT ck_escola_refeicoes_observacoes_not_blank
    CHECK (observacoes IS NULL OR length(btrim(observacoes)) > 0);

-- Garantir UNIQUE de ordenacao em galerias e links (1FN deterministica)
ALTER TABLE public.escola_avisos_imagens
  DROP CONSTRAINT IF EXISTS uq_escola_avisos_imagens_aviso_ordem,
  ADD CONSTRAINT uq_escola_avisos_imagens_aviso_ordem UNIQUE (aviso_id, ordem);

ALTER TABLE public.escola_acervo_imagens
  DROP CONSTRAINT IF EXISTS uq_escola_acervo_imagens_acervo_ordem,
  ADD CONSTRAINT uq_escola_acervo_imagens_acervo_ordem UNIQUE (acervo_id, ordem);

ALTER TABLE public.escola_turmas_links
  DROP CONSTRAINT IF EXISTS uq_escola_turmas_links_turma_ordem,
  ADD CONSTRAINT uq_escola_turmas_links_turma_ordem UNIQUE (turma_id, ordem);

-- Garantir CHECKs de coerencia de datas (data_expiracao > data_publicacao; data_fim >= data_inicio)
ALTER TABLE public.escola_avisos
  DROP CONSTRAINT IF EXISTS ck_avisos_datas_estrita,
  DROP CONSTRAINT IF EXISTS ck_avisos_datas,
  ADD CONSTRAINT ck_avisos_datas
    CHECK (data_expiracao IS NULL OR data_expiracao > data_publicacao);

ALTER TABLE public.escola_turmas_posts
  DROP CONSTRAINT IF EXISTS ck_turmas_posts_datas_estrita,
  DROP CONSTRAINT IF EXISTS ck_turmas_posts_datas,
  ADD CONSTRAINT ck_turmas_posts_datas
    CHECK (data_expiracao IS NULL OR data_expiracao > data_publicacao);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_constraint
    WHERE conrelid = 'public.escola_turmas'::regclass
      AND conname = 'uq_turmas_ano_letivo_serie_nome_turno'
  ) THEN
    ALTER TABLE public.escola_turmas
      ADD CONSTRAINT uq_turmas_ano_letivo_serie_nome_turno UNIQUE (ano_letivo, ano, nome, turno);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_constraint
    WHERE conrelid = 'public.escola_refeicoes'::regclass
      AND conname = 'uq_refeicoes_data_turno'
  ) THEN
    ALTER TABLE public.escola_refeicoes
      ADD CONSTRAINT uq_refeicoes_data_turno UNIQUE (data, turno);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_constraint
    WHERE conrelid = 'public.escola_eventos'::regclass
      AND conname = 'ck_eventos_datas'
  ) THEN
    ALTER TABLE public.escola_eventos
      ADD CONSTRAINT ck_eventos_datas CHECK (data_fim IS NULL OR data_fim >= data_inicio);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_constraint
    WHERE conrelid = 'public.escola_notificacoes'::regclass
      AND conname = 'ck_notificacoes_datas'
  ) THEN
    ALTER TABLE public.escola_notificacoes
      ADD CONSTRAINT ck_notificacoes_datas CHECK (data_fim IS NULL OR data_fim >= data_inicio);
  END IF;
END $$;

-- ----------------------------------------------------------------------------
-- 4. Limpeza de indices redundantes e criacao de indices compostos de consulta
-- ----------------------------------------------------------------------------
DROP INDEX IF EXISTS public.ix_escola_whatsapp_grupos_turma; -- coberto por escola_whatsapp_grupos_turma_id_key
DROP INDEX IF EXISTS public.ix_escola_refeicoes_data;          -- prefixo de uq_refeicoes_data_turno
DROP INDEX IF EXISTS public.ix_escola_turmas_posts_turma;      -- prefixo de ix_escola_turmas_posts_pub
DROP INDEX IF EXISTS public.ix_escola_turmas_ano_letivo;       -- prefixo de uq_turmas_ano_letivo_serie_nome_turno
DROP INDEX IF EXISTS public.ix_escola_avisos_imagens_aviso;    -- prefixo de uq_escola_avisos_imagens_aviso_ordem
DROP INDEX IF EXISTS public.ix_escola_acervo_imagens_acervo;   -- prefixo de uq_escola_acervo_imagens_acervo_ordem
DROP INDEX IF EXISTS public.ix_escola_turmas_links_turma;      -- prefixo de uq_escola_turmas_links_turma_ordem

CREATE INDEX IF NOT EXISTS ix_escola_eventos_status_inicio
  ON public.escola_eventos (status, data_inicio);

CREATE INDEX IF NOT EXISTS ix_escola_acervo_status_ano
  ON public.escola_acervo (status, ano DESC);

CREATE INDEX IF NOT EXISTS ix_escola_conteudo_paginas_pub_slug
  ON public.escola_conteudo_paginas (publicado, slug);

-- ----------------------------------------------------------------------------
-- 5. Metadados de Catalogo (COMMENT ON TABLE / COLUMN)
-- ----------------------------------------------------------------------------
COMMENT ON TABLE public.escola_usuarios IS 'Operadores, professores e administradores com acesso ao painel do portal escolar.';
COMMENT ON COLUMN public.escola_usuarios.role IS 'Nivel de permissao no portal (admin ou editor).';
COMMENT ON COLUMN public.escola_usuarios.email IS 'E-mail institucional unico normalizado em letras minusculas.';

COMMENT ON TABLE public.escola_avisos IS 'Comunicados, informes gerais e noticias publicadas no mural oficial da escola.';
COMMENT ON COLUMN public.escola_avisos.importancia IS 'Grau de prioridade editorial (normal, importante, urgente).';
COMMENT ON COLUMN public.escola_avisos.destaque_home IS 'Indica se o comunicado aparece no carrossel de destaque da pagina inicial.';
COMMENT ON COLUMN public.escola_avisos.data_expiracao IS 'Data/hora limite de vigencia publica (quando informada, estritamente posterior a data_publicacao).';

COMMENT ON TABLE public.escola_avisos_imagens IS 'Galeria de fotos vinculadas a um aviso (1FN; substitui antigo array JSONB).';
COMMENT ON COLUMN public.escola_avisos_imagens.ordem IS 'Posicao unica de exibicao dentro da galeria do aviso (>= 0).';

COMMENT ON TABLE public.escola_acervo IS 'Registros de projetos historicos, Revista Okaza e memorias institucionais da EEB Benonivio.';
COMMENT ON COLUMN public.escola_acervo.ano IS 'Ano ou periodo cronologico de referencia do registro historico.';

COMMENT ON TABLE public.escola_acervo_imagens IS 'Fotografias individuais dos albuns do acervo historico em 1FN.';
COMMENT ON COLUMN public.escola_acervo_imagens.ordem IS 'Sequencia unica de ordenacao da fotografia no album (>= 0).';

COMMENT ON TABLE public.escola_documentos IS 'Repositorio de arquivos oficiais disponiveis para download publico (editais, calendarios, atas).';
COMMENT ON COLUMN public.escola_documentos.tamanho_bytes IS 'Tamanho exato do arquivo em bytes (>= 0).';

COMMENT ON TABLE public.escola_conteudo_paginas IS 'Conteudo dinamico das paginas institucionais fixas do portal (Sobre, APP, Projetos).';
COMMENT ON COLUMN public.escola_conteudo_paginas.slug IS 'Identificador textual unico de rota amigavel (apenas minusculas, numeros e hifens).';

COMMENT ON TABLE public.escola_turmas IS 'Turmas regulares da escola organizadas por ano letivo, serie e turno em 3FN.';
COMMENT ON COLUMN public.escola_turmas.ano_letivo IS 'Ano letivo de vigencia da turma (ex.: 2025, 2026), preservando historico sem sobrescrita.';

COMMENT ON TABLE public.escola_turmas_links IS 'Links externos de apoio de cada turma (Drive, Classroom) em 1FN; substitui antigo campo JSONB.';
COMMENT ON COLUMN public.escola_turmas_links.ordem IS 'Ordem unica de exibicao do link na pagina da turma (>= 0).';

COMMENT ON TABLE public.escola_whatsapp_grupos IS 'Grupos oficiais de WhatsApp vinculados em relacao 1:1 com escola_turmas (turno obtido por JOIN em 3FN).';
COMMENT ON COLUMN public.escola_whatsapp_grupos.turma_id IS 'Chave estrangeira unica (1:1) para escola_turmas.';

COMMENT ON TABLE public.escola_turmas_posts IS 'Comunicados, materiais de aula e avisos de provas publicados no mural especifico de uma turma.';

COMMENT ON TABLE public.escola_eventos IS 'Programacao do calendario escolar (feiras cientificas, reunioes pedagogicas e eventos culturais).';
COMMENT ON COLUMN public.escola_eventos.status IS 'Situacao operacional do evento (ativo, inativo, expirado).';

COMMENT ON TABLE public.escola_turmas_eventos IS 'Tabela associativa N:N entre eventos e turmas participantes (2FN/3FN).';

COMMENT ON TABLE public.escola_refeicoes IS 'Cardapio diario da alimentacao escolar por data e turno (PNAE/SED-SC).';

COMMENT ON TABLE public.escola_notificacoes IS 'Alertas globais e comunicados urgentes exibidos no topo ou modal do portal escolar.';

COMMIT;
