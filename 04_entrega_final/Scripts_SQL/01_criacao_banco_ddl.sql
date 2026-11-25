-- ============================================================================
-- 00_ddl_completo_do_zero.sql
-- Projeto: Portal Escolar EEB Prof. Benonivio Joao Martins (A3 Banco de Dados)
-- Objetivo: Script DDL completo e transacional para criacao do zero do schema
--           normalizado (1FN, 2FN, 3FN), espelhando o estado final consolidado.
-- ATENCAO: Nao executar sobre banco ja migrado sem limpeza previa.
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Tipos Enumerados (ENUM)
-- ----------------------------------------------------------------------------
CREATE TYPE public.importancia_enum AS ENUM ('normal', 'importante', 'urgente');
CREATE TYPE public.publicacao_status_enum AS ENUM ('rascunho', 'publicado', 'arquivado');
CREATE TYPE public.status_enum AS ENUM ('ativo', 'inativo', 'expirado');
CREATE TYPE public.turno_enum AS ENUM ('matutino', 'vespertino', 'noturno', 'integral');
CREATE TYPE public.usuario_role_enum AS ENUM ('admin', 'editor');

-- ----------------------------------------------------------------------------
-- 2. Funcao Compartilhada de Timestamp (updated_at)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 3. Tabelas (15 entidades em 1FN, 2FN e 3FN)
-- ----------------------------------------------------------------------------

-- 3.1. escola_usuarios
CREATE TABLE public.escola_usuarios (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nome text NOT NULL,
  email text NOT NULL,
  role public.usuario_role_enum NOT NULL DEFAULT 'editor'::public.usuario_role_enum,
  ativo boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_usuarios_email_key UNIQUE (email),
  CONSTRAINT escola_usuarios_nome_check CHECK (length(btrim(nome)) > 0),
  CONSTRAINT ck_escola_usuarios_email_valido CHECK (
    length(btrim(email)) > 3
    AND email = lower(btrim(email))
    AND email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  )
);
-- Em producao, vincular diretamente a auth.users(id):
-- ALTER TABLE public.escola_usuarios
--   ADD CONSTRAINT fk_escola_usuarios_auth_users
--   FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

COMMENT ON TABLE public.escola_usuarios IS 'Operadores, professores e administradores com acesso ao painel do portal escolar.';
COMMENT ON COLUMN public.escola_usuarios.role IS 'Nivel de permissao no portal (admin ou editor).';
COMMENT ON COLUMN public.escola_usuarios.email IS 'E-mail institucional unico normalizado em letras minusculas.';

-- 3.2. escola_avisos
CREATE TABLE public.escola_avisos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  resumo text NOT NULL,
  conteudo text,
  categoria text NOT NULL,
  imagem_url text,
  importancia public.importancia_enum NOT NULL DEFAULT 'normal'::public.importancia_enum,
  destaque_home boolean NOT NULL DEFAULT false,
  status public.publicacao_status_enum NOT NULL DEFAULT 'publicado'::public.publicacao_status_enum,
  data_publicacao timestamptz NOT NULL DEFAULT timezone('utc', now()),
  data_expiracao timestamptz,
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_avisos_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT escola_avisos_resumo_check CHECK (length(btrim(resumo)) > 0),
  CONSTRAINT escola_avisos_categoria_check CHECK (length(btrim(categoria)) > 0),
  CONSTRAINT ck_escola_avisos_conteudo_not_blank CHECK (conteudo IS NULL OR length(btrim(conteudo)) > 0),
  CONSTRAINT ck_escola_avisos_imagem_url_not_blank CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0),
  CONSTRAINT ck_avisos_datas CHECK (data_expiracao IS NULL OR data_expiracao > data_publicacao)
);

COMMENT ON TABLE public.escola_avisos IS 'Comunicados, informes gerais e noticias publicadas no mural oficial da escola.';
COMMENT ON COLUMN public.escola_avisos.importancia IS 'Grau de prioridade editorial (normal, importante, urgente).';
COMMENT ON COLUMN public.escola_avisos.destaque_home IS 'Indica se o comunicado aparece no carrossel de destaque da pagina inicial.';
COMMENT ON COLUMN public.escola_avisos.data_expiracao IS 'Data/hora limite de vigencia publica (quando informada, estritamente posterior a data_publicacao).';

-- 3.3. escola_avisos_imagens (1FN)
CREATE TABLE public.escola_avisos_imagens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  aviso_id uuid NOT NULL REFERENCES public.escola_avisos(id) ON DELETE CASCADE,
  url text NOT NULL,
  legenda text,
  ordem integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_avisos_imagens_url_check CHECK (length(btrim(url)) > 0),
  CONSTRAINT ck_escola_avisos_imagens_legenda_not_blank CHECK (legenda IS NULL OR length(btrim(legenda)) > 0),
  CONSTRAINT escola_avisos_imagens_ordem_check CHECK (ordem >= 0),
  CONSTRAINT uq_escola_avisos_imagens_aviso_ordem UNIQUE (aviso_id, ordem)
);

COMMENT ON TABLE public.escola_avisos_imagens IS 'Galeria de fotos vinculadas a um aviso (1FN; substitui antigo array JSONB).';
COMMENT ON COLUMN public.escola_avisos_imagens.ordem IS 'Posicao unica de exibicao dentro da galeria do aviso (>= 0).';

-- 3.4. escola_acervo
CREATE TABLE public.escola_acervo (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ano text NOT NULL,
  categoria text NOT NULL,
  titulo text NOT NULL,
  descricao text,
  capa_url text,
  status public.publicacao_status_enum NOT NULL DEFAULT 'publicado'::public.publicacao_status_enum,
  data_publicacao timestamptz NOT NULL DEFAULT timezone('utc', now()),
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_acervo_ano_check CHECK (length(btrim(ano)) > 0),
  CONSTRAINT escola_acervo_categoria_check CHECK (length(btrim(categoria)) > 0),
  CONSTRAINT escola_acervo_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT ck_escola_acervo_descricao_not_blank CHECK (descricao IS NULL OR length(btrim(descricao)) > 0),
  CONSTRAINT ck_escola_acervo_capa_url_not_blank CHECK (capa_url IS NULL OR length(btrim(capa_url)) > 0)
);

COMMENT ON TABLE public.escola_acervo IS 'Registros de projetos historicos, Revista Okaza e memorias institucionais da EEB Benonivio.';
COMMENT ON COLUMN public.escola_acervo.ano IS 'Ano ou periodo cronologico de referencia do registro historico.';

-- 3.5. escola_acervo_imagens (1FN)
CREATE TABLE public.escola_acervo_imagens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  acervo_id uuid NOT NULL REFERENCES public.escola_acervo(id) ON DELETE CASCADE,
  url text NOT NULL,
  legenda text,
  ordem integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_acervo_imagens_url_check CHECK (length(btrim(url)) > 0),
  CONSTRAINT ck_escola_acervo_imagens_legenda_not_blank CHECK (legenda IS NULL OR length(btrim(legenda)) > 0),
  CONSTRAINT escola_acervo_imagens_ordem_check CHECK (ordem >= 0),
  CONSTRAINT uq_escola_acervo_imagens_acervo_ordem UNIQUE (acervo_id, ordem)
);

COMMENT ON TABLE public.escola_acervo_imagens IS 'Fotografias individuais dos albuns do acervo historico em 1FN.';
COMMENT ON COLUMN public.escola_acervo_imagens.ordem IS 'Sequencia unica de ordenacao da fotografia no album (>= 0).';

-- 3.6. escola_documentos
CREATE TABLE public.escola_documentos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  descricao text,
  categoria text NOT NULL,
  url_arquivo text NOT NULL,
  nome_arquivo text NOT NULL,
  mime_type text NOT NULL,
  tamanho_bytes bigint NOT NULL,
  status public.publicacao_status_enum NOT NULL DEFAULT 'publicado'::public.publicacao_status_enum,
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_documentos_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT ck_escola_documentos_descricao_not_blank CHECK (descricao IS NULL OR length(btrim(descricao)) > 0),
  CONSTRAINT escola_documentos_categoria_check CHECK (length(btrim(categoria)) > 0),
  CONSTRAINT escola_documentos_url_arquivo_check CHECK (length(btrim(url_arquivo)) > 0),
  CONSTRAINT escola_documentos_nome_arquivo_check CHECK (length(btrim(nome_arquivo)) > 0),
  CONSTRAINT escola_documentos_mime_type_check CHECK (length(btrim(mime_type)) > 0),
  CONSTRAINT escola_documentos_tamanho_bytes_check CHECK (tamanho_bytes >= 0)
);

COMMENT ON TABLE public.escola_documentos IS 'Repositorio de arquivos oficiais disponiveis para download publico (editais, calendarios, atas).';
COMMENT ON COLUMN public.escola_documentos.tamanho_bytes IS 'Tamanho exato do arquivo em bytes (>= 0).';

-- 3.7. escola_conteudo_paginas
CREATE TABLE public.escola_conteudo_paginas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text NOT NULL,
  titulo text NOT NULL,
  resumo text,
  conteudo_html text,
  imagem_url text,
  publicado boolean NOT NULL DEFAULT true,
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_conteudo_paginas_slug_key UNIQUE (slug),
  CONSTRAINT escola_conteudo_paginas_slug_check CHECK (length(btrim(slug)) > 0),
  CONSTRAINT ck_escola_conteudo_paginas_slug_formato CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  CONSTRAINT escola_conteudo_paginas_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT ck_escola_conteudo_paginas_resumo_not_blank CHECK (resumo IS NULL OR length(btrim(resumo)) > 0),
  CONSTRAINT ck_escola_conteudo_paginas_html_not_blank CHECK (conteudo_html IS NULL OR length(btrim(conteudo_html)) > 0),
  CONSTRAINT ck_escola_conteudo_paginas_imagem_url_not_blank CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0)
);

COMMENT ON TABLE public.escola_conteudo_paginas IS 'Conteudo dinamico das paginas institucionais fixas do portal (Sobre, APP, Projetos).';
COMMENT ON COLUMN public.escola_conteudo_paginas.slug IS 'Identificador textual unico de rota amigavel (apenas minusculas, numeros e hifens).';

-- 3.8. escola_turmas (3FN com ano_letivo)
CREATE TABLE public.escola_turmas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ano_letivo integer NOT NULL DEFAULT 2026,
  ano text NOT NULL,
  nome text NOT NULL,
  turno public.turno_enum NOT NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_turmas_ano_letivo_check CHECK (ano_letivo >= 2000),
  CONSTRAINT escola_turmas_ano_check CHECK (length(btrim(ano)) > 0),
  CONSTRAINT escola_turmas_nome_check CHECK (length(btrim(nome)) > 0),
  CONSTRAINT uq_turmas_ano_letivo_serie_nome_turno UNIQUE (ano_letivo, ano, nome, turno)
);

COMMENT ON TABLE public.escola_turmas IS 'Turmas regulares da escola organizadas por ano letivo, serie e turno em 3FN.';
COMMENT ON COLUMN public.escola_turmas.ano_letivo IS 'Ano letivo de vigencia da turma (ex.: 2025, 2026), preservando historico sem sobrescrita.';

-- 3.9. escola_turmas_links (1FN)
CREATE TABLE public.escola_turmas_links (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  turma_id uuid NOT NULL REFERENCES public.escola_turmas(id) ON DELETE CASCADE,
  titulo text NOT NULL,
  url text NOT NULL,
  ordem integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_turmas_links_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT escola_turmas_links_url_check CHECK (length(btrim(url)) > 0),
  CONSTRAINT escola_turmas_links_ordem_check CHECK (ordem >= 0),
  CONSTRAINT uq_escola_turmas_links_turma_ordem UNIQUE (turma_id, ordem)
);

COMMENT ON TABLE public.escola_turmas_links IS 'Links externos de apoio de cada turma (Drive, Classroom) em 1FN; substitui antigo campo JSONB.';
COMMENT ON COLUMN public.escola_turmas_links.ordem IS 'Ordem unica de exibicao do link na pagina da turma (>= 0).';

-- 3.10. escola_whatsapp_grupos (1:1 com escola_turmas, 3FN)
CREATE TABLE public.escola_whatsapp_grupos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  turma_id uuid NOT NULL REFERENCES public.escola_turmas(id) ON DELETE CASCADE,
  nome text NOT NULL,
  link_convite text NOT NULL,
  ativo boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_whatsapp_grupos_turma_id_key UNIQUE (turma_id),
  CONSTRAINT escola_whatsapp_grupos_nome_check CHECK (length(btrim(nome)) > 0),
  CONSTRAINT escola_whatsapp_grupos_link_convite_check CHECK (length(btrim(link_convite)) > 0)
);

COMMENT ON TABLE public.escola_whatsapp_grupos IS 'Grupos oficiais de WhatsApp vinculados em relacao 1:1 com escola_turmas (turno obtido por JOIN em 3FN).';
COMMENT ON COLUMN public.escola_whatsapp_grupos.turma_id IS 'Chave estrangeira unica (1:1) para escola_turmas.';

-- 3.11. escola_turmas_posts
CREATE TABLE public.escola_turmas_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  turma_id uuid NOT NULL REFERENCES public.escola_turmas(id) ON DELETE CASCADE,
  titulo text NOT NULL,
  resumo text,
  conteudo text,
  imagem_url text,
  link_referencia text,
  status public.publicacao_status_enum NOT NULL DEFAULT 'publicado'::public.publicacao_status_enum,
  data_publicacao timestamptz NOT NULL DEFAULT timezone('utc', now()),
  data_expiracao timestamptz,
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_turmas_posts_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT ck_escola_turmas_posts_resumo_not_blank CHECK (resumo IS NULL OR length(btrim(resumo)) > 0),
  CONSTRAINT ck_escola_turmas_posts_conteudo_not_blank CHECK (conteudo IS NULL OR length(btrim(conteudo)) > 0),
  CONSTRAINT ck_escola_turmas_posts_imagem_url_not_blank CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0),
  CONSTRAINT ck_escola_turmas_posts_link_ref_not_blank CHECK (link_referencia IS NULL OR length(btrim(link_referencia)) > 0),
  CONSTRAINT ck_turmas_posts_datas CHECK (data_expiracao IS NULL OR data_expiracao > data_publicacao)
);

COMMENT ON TABLE public.escola_turmas_posts IS 'Comunicados, materiais de aula e avisos de provas publicados no mural especifico de uma turma.';

-- 3.12. escola_eventos
CREATE TABLE public.escola_eventos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  descricao text,
  local text,
  data_inicio timestamptz NOT NULL,
  data_fim timestamptz,
  dia_inteiro boolean NOT NULL DEFAULT false,
  imagem_url text,
  status public.status_enum NOT NULL DEFAULT 'ativo'::public.status_enum,
  autor_id uuid REFERENCES public.escola_usuarios(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_eventos_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT ck_escola_eventos_descricao_not_blank CHECK (descricao IS NULL OR length(btrim(descricao)) > 0),
  CONSTRAINT ck_escola_eventos_local_not_blank CHECK (local IS NULL OR length(btrim(local)) > 0),
  CONSTRAINT ck_escola_eventos_imagem_url_not_blank CHECK (imagem_url IS NULL OR length(btrim(imagem_url)) > 0),
  CONSTRAINT ck_eventos_datas CHECK (data_fim IS NULL OR data_fim >= data_inicio)
);

COMMENT ON TABLE public.escola_eventos IS 'Programacao do calendario escolar (feiras cientificas, reunioes pedagogicas e eventos culturais).';
COMMENT ON COLUMN public.escola_eventos.status IS 'Situacao operacional do evento (ativo, inativo, expirado).';

-- 3.13. escola_turmas_eventos (Associativa N:N)
CREATE TABLE public.escola_turmas_eventos (
  evento_id uuid NOT NULL REFERENCES public.escola_eventos(id) ON DELETE CASCADE,
  turma_id uuid NOT NULL REFERENCES public.escola_turmas(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_turmas_eventos_pkey PRIMARY KEY (evento_id, turma_id)
);

COMMENT ON TABLE public.escola_turmas_eventos IS 'Tabela associativa N:N entre eventos e turmas participantes (2FN/3FN).';

-- 3.14. escola_refeicoes
CREATE TABLE public.escola_refeicoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  data date NOT NULL,
  turno public.turno_enum NOT NULL,
  descricao text NOT NULL,
  observacoes text,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_refeicoes_descricao_check CHECK (length(btrim(descricao)) > 0),
  CONSTRAINT ck_escola_refeicoes_observacoes_not_blank CHECK (observacoes IS NULL OR length(btrim(observacoes)) > 0),
  CONSTRAINT uq_refeicoes_data_turno UNIQUE (data, turno)
);

COMMENT ON TABLE public.escola_refeicoes IS 'Cardapio diario da alimentacao escolar por data e turno (PNAE/SED-SC).';

-- 3.15. escola_notificacoes
CREATE TABLE public.escola_notificacoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL,
  mensagem text NOT NULL,
  importancia public.importancia_enum NOT NULL DEFAULT 'normal'::public.importancia_enum,
  ativa boolean NOT NULL DEFAULT true,
  data_inicio timestamptz NOT NULL DEFAULT timezone('utc', now()),
  data_fim timestamptz,
  created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at timestamptz NOT NULL DEFAULT timezone('utc', now()),

  CONSTRAINT escola_notificacoes_titulo_check CHECK (length(btrim(titulo)) > 0),
  CONSTRAINT escola_notificacoes_mensagem_check CHECK (length(btrim(mensagem)) > 0),
  CONSTRAINT ck_notificacoes_datas CHECK (data_fim IS NULL OR data_fim >= data_inicio)
);

COMMENT ON TABLE public.escola_notificacoes IS 'Alertas globais e comunicados urgentes exibidos no topo ou modal do portal escolar.';

-- ----------------------------------------------------------------------------
-- 4. Indices Fisicos (FKs nao cobertas por PK/UNIQUE + consultas compostas)
-- ----------------------------------------------------------------------------
CREATE INDEX ix_escola_avisos_autor ON public.escola_avisos (autor_id);
CREATE INDEX ix_escola_avisos_pub ON public.escola_avisos (status, data_publicacao DESC);

CREATE INDEX ix_escola_acervo_autor ON public.escola_acervo (autor_id);
CREATE INDEX ix_escola_acervo_status_ano ON public.escola_acervo (status, ano DESC);

CREATE INDEX ix_escola_documentos_autor ON public.escola_documentos (autor_id);
CREATE INDEX ix_escola_documentos_cat ON public.escola_documentos (categoria, status);

CREATE INDEX ix_escola_conteudo_paginas_autor ON public.escola_conteudo_paginas (autor_id);
CREATE INDEX ix_escola_conteudo_paginas_pub_slug ON public.escola_conteudo_paginas (publicado, slug);

CREATE INDEX ix_escola_turmas_posts_autor ON public.escola_turmas_posts (autor_id);
CREATE INDEX ix_escola_turmas_posts_pub ON public.escola_turmas_posts (turma_id, status, data_publicacao DESC);

CREATE INDEX ix_escola_eventos_autor ON public.escola_eventos (autor_id);
CREATE INDEX ix_escola_eventos_datas ON public.escola_eventos (data_inicio, data_fim);
CREATE INDEX ix_escola_eventos_status_inicio ON public.escola_eventos (status, data_inicio);

CREATE INDEX ix_escola_turmas_eventos_turma ON public.escola_turmas_eventos (turma_id);

CREATE INDEX ix_escola_notificacoes_ativa ON public.escola_notificacoes (ativa, data_inicio, data_fim);

-- ----------------------------------------------------------------------------
-- 5. Triggers de updated_at (11 tabelas mutaveis)
-- ----------------------------------------------------------------------------
CREATE TRIGGER trg_escola_usuarios_updated_at
  BEFORE UPDATE ON public.escola_usuarios FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_avisos_updated_at
  BEFORE UPDATE ON public.escola_avisos FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_acervo_updated_at
  BEFORE UPDATE ON public.escola_acervo FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_documentos_updated_at
  BEFORE UPDATE ON public.escola_documentos FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_conteudo_paginas_updated_at
  BEFORE UPDATE ON public.escola_conteudo_paginas FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_turmas_updated_at
  BEFORE UPDATE ON public.escola_turmas FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_whatsapp_grupos_updated_at
  BEFORE UPDATE ON public.escola_whatsapp_grupos FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_turmas_posts_updated_at
  BEFORE UPDATE ON public.escola_turmas_posts FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_eventos_updated_at
  BEFORE UPDATE ON public.escola_eventos FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_refeicoes_updated_at
  BEFORE UPDATE ON public.escola_refeicoes FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();
CREATE TRIGGER trg_escola_notificacoes_updated_at
  BEFORE UPDATE ON public.escola_notificacoes FOR EACH ROW EXECUTE FUNCTION public.trigger_set_updated_at();

-- ----------------------------------------------------------------------------
-- 6. Views Publicas (security_invoker = true)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 7. Funcoes Auxiliares e Politicas RLS (Row-Level Security)
-- ----------------------------------------------------------------------------
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

-- escola_usuarios
CREATE POLICY "usuarios_select_own_or_admin" ON public.escola_usuarios FOR SELECT TO authenticated
  USING (id = (SELECT auth.uid()) OR (SELECT public.escola_is_admin()));
CREATE POLICY "usuarios_insert_admin" ON public.escola_usuarios FOR INSERT TO authenticated
  WITH CHECK ((SELECT public.escola_is_admin()));
CREATE POLICY "usuarios_update_admin" ON public.escola_usuarios FOR UPDATE TO authenticated
  USING ((SELECT public.escola_is_admin())) WITH CHECK ((SELECT public.escola_is_admin()));
CREATE POLICY "usuarios_delete_admin" ON public.escola_usuarios FOR DELETE TO authenticated
  USING ((SELECT public.escola_is_admin()));

-- escola_avisos
CREATE POLICY "avisos_select_anon_publicos" ON public.escola_avisos FOR SELECT TO anon
  USING (status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now()) AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now())));
CREATE POLICY "avisos_select_authenticated" ON public.escola_avisos FOR SELECT TO authenticated
  USING ((status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now()) AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))) OR (SELECT public.escola_is_editor()));
CREATE POLICY "avisos_insert_editor" ON public.escola_avisos FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "avisos_update_editor" ON public.escola_avisos FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "avisos_delete_editor" ON public.escola_avisos FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_avisos_imagens
CREATE POLICY "avisos_imagens_select_anon_publicos" ON public.escola_avisos_imagens FOR SELECT TO anon
  USING (EXISTS (SELECT 1 FROM public.escola_avisos a WHERE a.id = aviso_id AND a.status = 'publicado'::public.publicacao_status_enum AND a.data_publicacao <= timezone('utc', now()) AND (a.data_expiracao IS NULL OR a.data_expiracao > timezone('utc', now()))));
CREATE POLICY "avisos_imagens_select_authenticated" ON public.escola_avisos_imagens FOR SELECT TO authenticated
  USING (EXISTS (SELECT 1 FROM public.escola_avisos a WHERE a.id = aviso_id AND a.status = 'publicado'::public.publicacao_status_enum AND a.data_publicacao <= timezone('utc', now()) AND (a.data_expiracao IS NULL OR a.data_expiracao > timezone('utc', now()))) OR (SELECT public.escola_is_editor()));
CREATE POLICY "avisos_imagens_insert_editor" ON public.escola_avisos_imagens FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "avisos_imagens_update_editor" ON public.escola_avisos_imagens FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "avisos_imagens_delete_editor" ON public.escola_avisos_imagens FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_acervo
CREATE POLICY "acervo_select_anon_publicos" ON public.escola_acervo FOR SELECT TO anon
  USING (status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now()));
CREATE POLICY "acervo_select_authenticated" ON public.escola_acervo FOR SELECT TO authenticated
  USING ((status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now())) OR (SELECT public.escola_is_editor()));
CREATE POLICY "acervo_insert_editor" ON public.escola_acervo FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "acervo_update_editor" ON public.escola_acervo FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "acervo_delete_editor" ON public.escola_acervo FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_acervo_imagens
CREATE POLICY "acervo_imagens_select_anon_publicos" ON public.escola_acervo_imagens FOR SELECT TO anon
  USING (EXISTS (SELECT 1 FROM public.escola_acervo ac WHERE ac.id = acervo_id AND ac.status = 'publicado'::public.publicacao_status_enum AND ac.data_publicacao <= timezone('utc', now())));
CREATE POLICY "acervo_imagens_select_authenticated" ON public.escola_acervo_imagens FOR SELECT TO authenticated
  USING (EXISTS (SELECT 1 FROM public.escola_acervo ac WHERE ac.id = acervo_id AND ac.status = 'publicado'::public.publicacao_status_enum AND ac.data_publicacao <= timezone('utc', now())) OR (SELECT public.escola_is_editor()));
CREATE POLICY "acervo_imagens_insert_editor" ON public.escola_acervo_imagens FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "acervo_imagens_update_editor" ON public.escola_acervo_imagens FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "acervo_imagens_delete_editor" ON public.escola_acervo_imagens FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_documentos
CREATE POLICY "documentos_select_anon_publicos" ON public.escola_documentos FOR SELECT TO anon
  USING (status = 'publicado'::public.publicacao_status_enum);
CREATE POLICY "documentos_select_authenticated" ON public.escola_documentos FOR SELECT TO authenticated
  USING (status = 'publicado'::public.publicacao_status_enum OR (SELECT public.escola_is_editor()));
CREATE POLICY "documentos_insert_editor" ON public.escola_documentos FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "documentos_update_editor" ON public.escola_documentos FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "documentos_delete_editor" ON public.escola_documentos FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_conteudo_paginas
CREATE POLICY "conteudo_paginas_select_anon_publicos" ON public.escola_conteudo_paginas FOR SELECT TO anon
  USING (publicado = true);
CREATE POLICY "conteudo_paginas_select_authenticated" ON public.escola_conteudo_paginas FOR SELECT TO authenticated
  USING (publicado = true OR (SELECT public.escola_is_editor()));
CREATE POLICY "conteudo_paginas_insert_editor" ON public.escola_conteudo_paginas FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "conteudo_paginas_update_editor" ON public.escola_conteudo_paginas FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "conteudo_paginas_delete_editor" ON public.escola_conteudo_paginas FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_turmas
CREATE POLICY "turmas_select_publico" ON public.escola_turmas FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "turmas_insert_editor" ON public.escola_turmas FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_update_editor" ON public.escola_turmas FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_delete_editor" ON public.escola_turmas FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_turmas_links
CREATE POLICY "turmas_links_select_publico" ON public.escola_turmas_links FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "turmas_links_insert_editor" ON public.escola_turmas_links FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_links_update_editor" ON public.escola_turmas_links FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_links_delete_editor" ON public.escola_turmas_links FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_whatsapp_grupos
CREATE POLICY "whatsapp_grupos_select_anon_ativos" ON public.escola_whatsapp_grupos FOR SELECT TO anon USING (ativo = true);
CREATE POLICY "whatsapp_grupos_select_authenticated" ON public.escola_whatsapp_grupos FOR SELECT TO authenticated USING (ativo = true OR (SELECT public.escola_is_editor()));
CREATE POLICY "whatsapp_grupos_insert_editor" ON public.escola_whatsapp_grupos FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "whatsapp_grupos_update_editor" ON public.escola_whatsapp_grupos FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "whatsapp_grupos_delete_editor" ON public.escola_whatsapp_grupos FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_turmas_posts
CREATE POLICY "turmas_posts_select_anon_publicos" ON public.escola_turmas_posts FOR SELECT TO anon
  USING (status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now()) AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now())));
CREATE POLICY "turmas_posts_select_authenticated" ON public.escola_turmas_posts FOR SELECT TO authenticated
  USING ((status = 'publicado'::public.publicacao_status_enum AND data_publicacao <= timezone('utc', now()) AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now()))) OR (SELECT public.escola_is_editor()));
CREATE POLICY "turmas_posts_insert_editor" ON public.escola_turmas_posts FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_posts_update_editor" ON public.escola_turmas_posts FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_posts_delete_editor" ON public.escola_turmas_posts FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_eventos
CREATE POLICY "eventos_select_anon_ativos" ON public.escola_eventos FOR SELECT TO anon USING (status = 'ativo'::public.status_enum);
CREATE POLICY "eventos_select_authenticated" ON public.escola_eventos FOR SELECT TO authenticated USING (status = 'ativo'::public.status_enum OR (SELECT public.escola_is_editor()));
CREATE POLICY "eventos_insert_editor" ON public.escola_eventos FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "eventos_update_editor" ON public.escola_eventos FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "eventos_delete_editor" ON public.escola_eventos FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_turmas_eventos
CREATE POLICY "turmas_eventos_select_publico" ON public.escola_turmas_eventos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "turmas_eventos_insert_editor" ON public.escola_turmas_eventos FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_eventos_update_editor" ON public.escola_turmas_eventos FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "turmas_eventos_delete_editor" ON public.escola_turmas_eventos FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_refeicoes
CREATE POLICY "refeicoes_select_publico" ON public.escola_refeicoes FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "refeicoes_insert_editor" ON public.escola_refeicoes FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "refeicoes_update_editor" ON public.escola_refeicoes FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "refeicoes_delete_editor" ON public.escola_refeicoes FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

-- escola_notificacoes
CREATE POLICY "notificacoes_select_anon_ativas" ON public.escola_notificacoes FOR SELECT TO anon
  USING (ativa = true AND data_inicio <= timezone('utc', now()) AND (data_fim IS NULL OR data_fim >= timezone('utc', now())));
CREATE POLICY "notificacoes_select_authenticated" ON public.escola_notificacoes FOR SELECT TO authenticated
  USING ((ativa = true AND data_inicio <= timezone('utc', now()) AND (data_fim IS NULL OR data_fim >= timezone('utc', now()))) OR (SELECT public.escola_is_editor()));
CREATE POLICY "notificacoes_insert_editor" ON public.escola_notificacoes FOR INSERT TO authenticated WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "notificacoes_update_editor" ON public.escola_notificacoes FOR UPDATE TO authenticated USING ((SELECT public.escola_is_editor())) WITH CHECK ((SELECT public.escola_is_editor()));
CREATE POLICY "notificacoes_delete_editor" ON public.escola_notificacoes FOR DELETE TO authenticated USING ((SELECT public.escola_is_editor()));

COMMIT;
