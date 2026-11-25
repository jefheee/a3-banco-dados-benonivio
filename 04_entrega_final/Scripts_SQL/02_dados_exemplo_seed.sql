-- ============================================================================
-- 04_seed_escola_benonivio.sql
-- Projeto: problemaescola vFinal (project_ref: rbowxcvpcaqrycrvfowh)
-- Objetivo: Limpar dados anteriores de teste e popular massa de dados rica,
--           coerente e idempotente (CTEs + RETURNING sem UUIDs chutados).
-- ============================================================================

BEGIN;

TRUNCATE TABLE
  public.escola_turmas_eventos,
  public.escola_turmas_posts,
  public.escola_turmas_links,
  public.escola_whatsapp_grupos,
  public.escola_avisos_imagens,
  public.escola_acervo_imagens,
  public.escola_avisos,
  public.escola_acervo,
  public.escola_documentos,
  public.escola_conteudo_paginas,
  public.escola_eventos,
  public.escola_turmas,
  public.escola_refeicoes,
  public.escola_notificacoes,
  public.escola_usuarios
RESTART IDENTITY CASCADE;

WITH
-- 1. Usuários (4 operadores)
u_ins AS (
  INSERT INTO public.escola_usuarios (nome, email, role, ativo)
  VALUES
    ('Ana Cláudia Souza (Direção)',    'direcao@eebbenonivio.sc.gov.br',      'admin'::public.usuario_role_enum,  true),
    ('Marcos Vieira (Secretaria)',     'secretaria@eebbenonivio.sc.gov.br',   'admin'::public.usuario_role_enum,  true),
    ('Helena Martins (Coordenação)',   'coordenacao@eebbenonivio.sc.gov.br',  'editor'::public.usuario_role_enum, true),
    ('Prof. Carlos Eduardo Lima',      'carlos.lima@eebbenonivio.sc.gov.br',  'editor'::public.usuario_role_enum, true)
  RETURNING id, email
),
u_dir  AS (SELECT id FROM u_ins WHERE email = 'direcao@eebbenonivio.sc.gov.br'),
u_sec  AS (SELECT id FROM u_ins WHERE email = 'secretaria@eebbenonivio.sc.gov.br'),
u_coor AS (SELECT id FROM u_ins WHERE email = 'coordenacao@eebbenonivio.sc.gov.br'),
u_prof AS (SELECT id FROM u_ins WHERE email = 'carlos.lima@eebbenonivio.sc.gov.br'),

-- 2. Turmas (6 turmas: 2 de 2025 e 4 de 2026)
t_ins AS (
  INSERT INTO public.escola_turmas (ano_letivo, ano, nome, turno)
  VALUES
    (2025, '1º Ano Ensino Médio',        '101', 'matutino'::public.turno_enum),
    (2025, '3º Ano Ensino Médio',        '301', 'noturno'::public.turno_enum),
    (2026, '1º Ano Ensino Médio',        '101', 'matutino'::public.turno_enum),
    (2026, '2º Ano Ensino Médio',        '201', 'vespertino'::public.turno_enum),
    (2026, '3º Ano Ensino Médio',        '301', 'noturno'::public.turno_enum),
    (2026, '9º Ano Ensino Fundamental',  '901', 'matutino'::public.turno_enum)
  RETURNING id, ano_letivo, nome
),
t_25_101 AS (SELECT id FROM t_ins WHERE ano_letivo = 2025 AND nome = '101'),
t_25_301 AS (SELECT id FROM t_ins WHERE ano_letivo = 2025 AND nome = '301'),
t_26_101 AS (SELECT id FROM t_ins WHERE ano_letivo = 2026 AND nome = '101'),
t_26_201 AS (SELECT id FROM t_ins WHERE ano_letivo = 2026 AND nome = '201'),
t_26_301 AS (SELECT id FROM t_ins WHERE ano_letivo = 2026 AND nome = '301'),
t_26_901 AS (SELECT id FROM t_ins WHERE ano_letivo = 2026 AND nome = '901'),

-- 3. Grupos de WhatsApp (5 de 6 turmas; 2026-901 propositalmente sem grupo)
wpp_ins AS (
  INSERT INTO public.escola_whatsapp_grupos (turma_id, nome, link_convite, ativo)
  SELECT id, '2025 | 1º Ano 101 - Arquivo',        'https://chat.whatsapp.com/Beno2025Turma101', false FROM t_25_101
  UNION ALL
  SELECT id, '2025 | 3º Ano 301 - Formandos',      'https://chat.whatsapp.com/Beno2025Turma301', false FROM t_25_301
  UNION ALL
  SELECT id, '2026 | 1º Ano 101 - Informes',       'https://chat.whatsapp.com/Beno2026Turma101', true  FROM t_26_101
  UNION ALL
  SELECT id, '2026 | 2º Ano 201 - Vespertino',     'https://chat.whatsapp.com/Beno2026Turma201', true  FROM t_26_201
  UNION ALL
  SELECT id, '2026 | 3º Ano 301 - Noturno ENEM',   'https://chat.whatsapp.com/Beno2026Turma301', true  FROM t_26_301
  RETURNING id
),

-- 4. Links complementares das turmas (11 links; 2026-901 com 0 links)
lnk_ins AS (
  INSERT INTO public.escola_turmas_links (turma_id, titulo, url, ordem)
  SELECT id, 'Google Classroom - Turma 101 (2026)',     'https://classroom.google.com/c/beno-2026-101', 1 FROM t_26_101
  UNION ALL
  SELECT id, 'Pasta de Apostilas SED-SC (2026)',       'https://drive.google.com/drive/folders/beno-101-2026', 2 FROM t_26_101
  UNION ALL
  SELECT id, 'Cronograma de Provas Trimestrais',        'https://portal.eebbenonivio.sc.gov.br/provas/101', 3 FROM t_26_101
  UNION ALL
  SELECT id, 'Google Classroom - Turma 201 (2026)',     'https://classroom.google.com/c/beno-2026-201', 1 FROM t_26_201
  UNION ALL
  SELECT id, 'Roteiros de Laboratório de Química',      'https://drive.google.com/drive/folders/beno-lab-201', 2 FROM t_26_201
  UNION ALL
  SELECT id, 'Plataforma ENEM & Simulados 301',         'https://simulados.eebbenonivio.sc.gov.br/301', 1 FROM t_26_301
  UNION ALL
  SELECT id, 'Google Classroom - Terceirão 301',        'https://classroom.google.com/c/beno-2026-301', 2 FROM t_26_301
  UNION ALL
  SELECT id, 'Banco de Temas de Redação 2026',          'https://drive.google.com/drive/folders/redacao-301', 3 FROM t_26_301
  UNION ALL
  SELECT id, 'Repositório Histórico 101 (2025)',        'https://drive.google.com/drive/folders/arquivo-2025-101', 1 FROM t_25_101
  UNION ALL
  SELECT id, 'Boletins e Atas 101 (2025)',              'https://portal.eebbenonivio.sc.gov.br/arquivo/2025-101', 2 FROM t_25_101
  UNION ALL
  SELECT id, 'Álbum Digital Formatura 301 (2025)',      'https://drive.google.com/drive/folders/formatura-2025', 1 FROM t_25_301
  RETURNING id
),

-- 5. Posts de turmas (9 posts misturando publicado, rascunho e arquivado; 2026-901 sem posts publicados)
pst_ins AS (
  INSERT INTO public.escola_turmas_posts
    (turma_id, titulo, resumo, conteudo, imagem_url, link_referencia, status, data_publicacao, data_expiracao, autor_id)
  SELECT t.id, 'Semana de Provas do 1º Trimestre - 101', 'Calendário oficial de avaliações.',
         'Provas ocorrem de segunda a sexta no primeiro horário.', NULL, 'https://portal.eebbenonivio.sc.gov.br/provas',
         'publicado'::public.publicacao_status_enum, timezone('utc', now()) - interval '10 days', timezone('utc', now()) + interval '20 days', u.id
  FROM t_26_101 t, u_prof u
  UNION ALL
  SELECT t.id, 'Trabalho de Biologia Celular', 'Entrega de maquetes em grupo.',
         'Apresentação no laboratório de ciências.', NULL, NULL,
         'publicado'::public.publicacao_status_enum, timezone('utc', now()) - interval '5 days', NULL, u.id
  FROM t_26_101 t, u_prof u
  UNION ALL
  SELECT t.id, 'Roteiro de Física - Cinemática', 'Lista de exercícios preparatória.',
         'Resolver exercícios 1 a 15 do caderno.', NULL, NULL,
         'publicado'::public.publicacao_status_enum, timezone('utc', now()) - interval '3 days', timezone('utc', now()) + interval '30 days', u.id
  FROM t_26_201 t, u_prof u
  UNION ALL
  SELECT t.id, 'Simulado Geral ENEM - 3º Ano Noturno', 'Aplicação no auditório central.',
         'Trazer caneta esferográfica preta transparente.', NULL, 'https://simulados.eebbenonivio.sc.gov.br',
         'publicado'::public.publicacao_status_enum, timezone('utc', now()) - interval '7 days', timezone('utc', now()) + interval '15 days', u.id
  FROM t_26_301 t, u_coor u
  UNION ALL
  SELECT t.id, 'Plantão de Redação Nota 1000', 'Atendimento extra às quartas-feiras.',
         'Correção comentada de redações anteriores.', NULL, NULL,
         'publicado'::public.publicacao_status_enum, timezone('utc', now()) - interval '2 days', NULL, u.id
  FROM t_26_301 t, u_prof u
  UNION ALL
  SELECT t.id, 'Rascunho: Recuperação Paralela 901', 'Cronograma em revisão pela coordenação.',
         'Aguardando confirmação de datas dos docentes.', NULL, NULL,
         'rascunho'::public.publicacao_status_enum, timezone('utc', now()), NULL, u.id
  FROM t_26_901 t, u_coor u
  UNION ALL
  SELECT t.id, 'Encerramento do Ano Letivo 2025 - 101', 'Registro de fechamento de notas 2025.',
         'Boletins disponíveis na secretaria escolar.', NULL, NULL,
         'arquivado'::public.publicacao_status_enum, timestamp '2025-12-10 12:00:00+00', timestamp '2025-12-30 23:59:59+00', u.id
  FROM t_25_101 t, u_sec u
  UNION ALL
  SELECT t.id, 'Colação de Grau Turma 301 - 2025', 'Instruções para entrega de certificados.',
         'Cerimônia realizada no ginásio da escola.', NULL, NULL,
         'publicado'::public.publicacao_status_enum, timestamp '2025-12-01 18:00:00+00', NULL, u.id
  FROM t_25_301 t, u_dir u
  UNION ALL
  SELECT t.id, 'Revisão de Matemática Básica 2025', 'Material de apoio encerrado.',
         'Arquivado ao final do trimestre.', NULL, NULL,
         'arquivado'::public.publicacao_status_enum, timestamp '2025-06-01 12:00:00+00', timestamp '2025-07-01 12:00:00+00', u.id
  FROM t_25_101 t, u_prof u
  RETURNING id
),

-- 6. Avisos (6 avisos: 4 publicados vigentes, 1 rascunho, 1 arquivado)
avs_ins AS (
  INSERT INTO public.escola_avisos
    (titulo, resumo, conteudo, categoria, imagem_url, importancia, destaque_home, status, data_publicacao, data_expiracao, autor_id)
  SELECT 'Matrículas e Rematrículas 2026 Abertas', 'Confira prazos e documentos obrigatórios na secretaria.',
         'Atendimento presencial das 08:00 às 17:00 com comprovante de residência e CPF.', 'Matrículas',
         'https://portal.eebbenonivio.sc.gov.br/img/avisos/matriculas.jpg',
         'urgente'::public.importancia_enum, true, 'publicado'::public.publicacao_status_enum,
         timezone('utc', now()) - interval '15 days', timezone('utc', now()) + interval '45 days', u.id
  FROM u_sec u
  UNION ALL
  SELECT 'Entrega dos Kits de Material Escolar SED/SC', 'Distribuição iniciada para Ensino Fundamental e Médio.',
         'Os responsáveis devem assinar o termo de recebimento na biblioteca.', 'Geral',
         'https://portal.eebbenonivio.sc.gov.br/img/avisos/kits.jpg',
         'importante'::public.importancia_enum, true, 'publicado'::public.publicacao_status_enum,
         timezone('utc', now()) - interval '8 days', timezone('utc', now()) + interval '30 days', u.id
  FROM u_dir u
  UNION ALL
  SELECT 'Inscrições para a Fanfarra Benonívio 2026', 'Ensaios às terças e quintas no contraturno.',
         'Vagas para percussão, sopro e linha de frente. Procurar a coordenação.', 'Projetos',
         'https://portal.eebbenonivio.sc.gov.br/img/avisos/fanfarra.jpg',
         'normal'::public.importancia_enum, false, 'publicado'::public.publicacao_status_enum,
         timezone('utc', now()) - interval '4 days', NULL, u.id
  FROM u_coor u
  UNION ALL
  SELECT 'Campanha de Vacinação Escolar - Posto Local', 'Atualização da caderneta vacinal na quadra coberta.',
         'Trazer autorização assinada pelos pais ou responsáveis.', 'Saúde',
         'https://portal.eebbenonivio.sc.gov.br/img/avisos/vacina.jpg',
         'importante'::public.importancia_enum, true, 'publicado'::public.publicacao_status_enum,
         timezone('utc', now()) - interval '2 days', timezone('utc', now()) + interval '20 days', u.id
  FROM u_dir u
  UNION ALL
  SELECT 'Rascunho: Recesso Escolar de Julho', 'Comunicado interno aguardando homologação da CRE.',
         'Não publicar antes da portaria oficial.', 'Calendário',
         NULL,
         'normal'::public.importancia_enum, false, 'rascunho'::public.publicacao_status_enum,
         timezone('utc', now()), NULL, u.id
  FROM u_sec u
  UNION ALL
  SELECT 'Encerrado: Chamada Pública Merenda 2025', 'Edital encerrado do exercício anterior.',
         'Documentação arquivada para fins de auditoria.', 'Editais',
         NULL,
         'normal'::public.importancia_enum, false, 'arquivado'::public.publicacao_status_enum,
         timestamp '2025-02-10 10:00:00+00', timestamp '2025-03-30 18:00:00+00', u.id
  FROM u_sec u
  RETURNING id, titulo
),
av1 AS (SELECT id FROM avs_ins WHERE titulo LIKE 'Matrículas%'),
av2 AS (SELECT id FROM avs_ins WHERE titulo LIKE 'Entrega dos Kits%'),
av3 AS (SELECT id FROM avs_ins WHERE titulo LIKE 'Inscrições para a Fanfarra%'),
av4 AS (SELECT id FROM avs_ins WHERE titulo LIKE 'Campanha de Vacinação%'),

-- 7. Imagens dos avisos (10 fotos em 1FN)
av_img_ins AS (
  INSERT INTO public.escola_avisos_imagens (aviso_id, url, legenda, ordem)
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/mat-1.jpg', 'Atendimento na secretaria', 1 FROM av1
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/mat-2.jpg', 'Lista de documentos no mural', 2 FROM av1
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/mat-3.jpg', 'Recepção às famílias', 3 FROM av1
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/kit-1.jpg', 'Kits organizados na biblioteca', 1 FROM av2
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/kit-2.jpg', 'Entrega aos estudantes do 1º ano', 2 FROM av2
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/kit-3.jpg', 'Materiais didáticos completos', 3 FROM av2
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/fan-1.jpg', 'Ensaio da fanfarra no pátio', 1 FROM av3
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/fan-2.jpg', 'Desfile cívico de 7 de setembro', 2 FROM av3
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/vac-1.jpg', 'Equipe de saúde na escola', 1 FROM av4
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/avisos/vac-2.jpg', 'Orientação aos estudantes', 2 FROM av4
  RETURNING id
),

-- 8. Acervo histórico (4 itens)
ac_ins AS (
  INSERT INTO public.escola_acervo (ano, categoria, titulo, descricao, capa_url, status, data_publicacao, autor_id)
  SELECT '2019', 'Revista Okaza', 'Revista Okaza - Edição Especial Centenário',
         'Produção jornalística estudantil com entrevistas, crônicas e memória do bairro.',
         'https://portal.eebbenonivio.sc.gov.br/img/acervo/okaza-capa.jpg',
         'publicado'::public.publicacao_status_enum, timestamp '2025-08-15 12:00:00+00', u.id
  FROM u_coor u
  UNION ALL
  SELECT '2020', 'Projetos', 'Grupo Butterfly e Sustentabilidade Ambiental',
         'Projeto de hortas escolares, compostagem e educação ambiental liderado pelos estudantes.',
         'https://portal.eebbenonivio.sc.gov.br/img/acervo/butterfly-capa.jpg',
         'publicado'::public.publicacao_status_enum, timestamp '2025-09-01 12:00:00+00', u.id
  FROM u_dir u
  UNION ALL
  SELECT '2024', 'Feira de Ciências', 'Mostra Científica Regional EEB Benonívio',
         'Exposição de protótipos de energia solar e robótica educacional.',
         'https://portal.eebbenonivio.sc.gov.br/img/acervo/feira-2024.jpg',
         'publicado'::public.publicacao_status_enum, timestamp '2025-10-10 12:00:00+00', u.id
  FROM u_prof u
  UNION ALL
  SELECT '2025', 'Formatura', 'Galeria Histórica Formatura Terceirão 2025',
         'Registro em curadoria antes da liberação pública.',
         NULL,
         'rascunho'::public.publicacao_status_enum, timezone('utc', now()), u.id
  FROM u_dir u
  RETURNING id, categoria
),
ac_okaza AS (SELECT id FROM ac_ins WHERE categoria = 'Revista Okaza'),
ac_butt  AS (SELECT id FROM ac_ins WHERE categoria = 'Projetos'),
ac_feira AS (SELECT id FROM ac_ins WHERE categoria = 'Feira de Ciências'),
ac_form  AS (SELECT id FROM ac_ins WHERE categoria = 'Formatura'),

-- 9. Imagens do acervo (8 fotos em 1FN)
ac_img_ins AS (
  INSERT INTO public.escola_acervo_imagens (acervo_id, url, legenda, ordem)
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/okaza-1.jpg', 'Capa da edição impressa 2019', 1 FROM ac_okaza
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/okaza-2.jpg', 'Equipe de redação estudantil', 2 FROM ac_okaza
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/butterfly-1.jpg', 'Mutirão da horta pedagógica', 1 FROM ac_butt
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/butterfly-2.jpg', 'Membros fundadores do grupo', 2 FROM ac_butt
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/feira-1.jpg', 'Estande de robótica e Arduino', 1 FROM ac_feira
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/feira-2.jpg', 'Premiação dos projetos vencedores', 2 FROM ac_feira
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/form-1.jpg', 'Entrega dos diplomas no ginásio', 1 FROM ac_form
  UNION ALL
  SELECT id, 'https://portal.eebbenonivio.sc.gov.br/img/acervo/form-2.jpg', 'Foto oficial das turmas concluintes', 2 FROM ac_form
  RETURNING id
),

-- 10. Documentos oficiais (6 arquivos em categorias distintas)
doc_ins AS (
  INSERT INTO public.escola_documentos
    (titulo, descricao, categoria, url_arquivo, nome_arquivo, mime_type, tamanho_bytes, status, autor_id)
  SELECT 'Calendário Escolar 2026 Homologado SED/SC', 'Datas letivas, conselhos de classe e recessos.',
         'Calendários', 'https://storage.supabase.co/benonivio/calendario-2026.pdf', 'calendario-2026.pdf',
         'application/pdf', 1048576, 'publicado'::public.publicacao_status_enum, u.id FROM u_sec u
  UNION ALL
  SELECT 'Calendário de Provas 1º Trimestre 2026', 'Cronograma consolidado por turno.',
         'Calendários', 'https://storage.supabase.co/benonivio/provas-1tri-2026.pdf', 'provas-1tri-2026.pdf',
         'application/pdf', 524288, 'publicado'::public.publicacao_status_enum, u.id FROM u_coor u
  UNION ALL
  SELECT 'Projeto Político Pedagógico (PPP) 2026', 'Diretrizes curriculares e missão institucional.',
         'Pedagógico', 'https://storage.supabase.co/benonivio/ppp-benonivio-2026.pdf', 'ppp-benonivio-2026.pdf',
         'application/pdf', 2621440, 'publicado'::public.publicacao_status_enum, u.id FROM u_dir u
  UNION ALL
  SELECT 'Edital Eleição Conselho Deliberativo Escolar', 'Normas e prazos de inscrição de chapas.',
         'Editais', 'https://storage.supabase.co/benonivio/edital-cde-2026.pdf', 'edital-cde-2026.pdf',
         'application/pdf', 786432, 'publicado'::public.publicacao_status_enum, u.id FROM u_dir u
  UNION ALL
  SELECT 'Edital Bolsas Esportivas e Fanfarra', 'Critérios de participação no contraturno.',
         'Editais', 'https://storage.supabase.co/benonivio/edital-fanfarra-2026.pdf', 'edital-fanfarra-2026.pdf',
         'application/pdf', 614400, 'publicado'::public.publicacao_status_enum, u.id FROM u_coor u
  UNION ALL
  SELECT 'Ata de Reunião APP - Fevereiro 2026 (Minuta)', 'Aguardando assinatura da diretoria da APP.',
         'Atas', 'https://storage.supabase.co/benonivio/ata-app-fev-2026.pdf', 'ata-app-fev-2026.pdf',
         'application/pdf', 393216, 'rascunho'::public.publicacao_status_enum, u.id FROM u_sec u
  RETURNING id
),

-- 11. Páginas institucionais (4 páginas: 3 publicadas, 1 oculta)
pag_ins AS (
  INSERT INTO public.escola_conteudo_paginas (slug, titulo, resumo, conteudo_html, imagem_url, publicado, autor_id)
  SELECT 'sobre', 'Sobre a EEB Prof. Benonívio João Martins', 'História, missão e estrutura da escola.',
         '<p>Instituição pública estadual localizada em Palhoça/SC, comprometida com formação cidadã.</p>',
         'https://portal.eebbenonivio.sc.gov.br/img/paginas/fachada.jpg', true, u.id FROM u_dir u
  UNION ALL
  SELECT 'app-associacao', 'Associação de Pais e Professores (APP)', 'Transparência e participação comunitária.',
         '<p>A APP colabora diretamente com melhorias estruturais e eventos estudantis.</p>',
         'https://portal.eebbenonivio.sc.gov.br/img/paginas/app.jpg', true, u.id FROM u_dir u
  UNION ALL
  SELECT 'projetos-estudantis', 'Projetos Estudantis e Clubes', 'Fanfarra, Grupo Butterfly e Revista Okaza.',
         '<p>Iniciativas culturais, científicas e ambientais protagonizadas pelos alunos.</p>',
         'https://portal.eebbenonivio.sc.gov.br/img/paginas/projetos.jpg', true, u.id FROM u_coor u
  UNION ALL
  SELECT 'regimento-interno-revisao', 'Minuta do Regimento Interno 2027', 'Documento em revisão interna.',
         '<p>Conteúdo restrito à direção até homologação.</p>',
         NULL, false, u.id FROM u_sec u
  RETURNING id
),

-- 12. Eventos (5 eventos: 3 ativos futuros, 1 expirado, 1 inativo)
evt_ins AS (
  INSERT INTO public.escola_eventos (titulo, descricao, local, data_inicio, data_fim, dia_inteiro, imagem_url, status, autor_id)
  SELECT 'Conselho de Classe 1º Trimestre', 'Análise pedagógica de desempenho das turmas.', 'Sala dos Professores',
         timezone('utc', now()) + interval '12 days', timezone('utc', now()) + interval '12 days' + interval '4 hours',
         false, NULL, 'ativo'::public.status_enum, u.id FROM u_coor u
  UNION ALL
  SELECT 'Feira de Ciências e Tecnologia 2026', 'Mostra anual de experimentos e inovação.', 'Ginásio Poliesportivo',
         timezone('utc', now()) + interval '35 days', timezone('utc', now()) + interval '35 days' + interval '8 hours',
         true, 'https://portal.eebbenonivio.sc.gov.br/img/eventos/feira-2026.jpg', 'ativo'::public.status_enum, u.id FROM u_prof u
  UNION ALL
  SELECT 'Festa Junina da Comunidade Escolar', 'Apresentações culturais, quadrilha e barracas típicas.', 'Pátio Central',
         timezone('utc', now()) + interval '70 days', timezone('utc', now()) + interval '70 days' + interval '6 hours',
         false, 'https://portal.eebbenonivio.sc.gov.br/img/eventos/junina.jpg', 'ativo'::public.status_enum, u.id FROM u_dir u
  UNION ALL
  SELECT 'Abertura do Ano Letivo 2025', 'Acolhimento inicial das turmas 2025.', 'Auditório',
         timestamp '2025-02-12 08:00:00+00', timestamp '2025-02-12 11:30:00+00',
         false, NULL, 'expirado'::public.status_enum, u.id FROM u_dir u
  UNION ALL
  SELECT 'Planejamento Semana da Pátria (Rascunho)', 'Definição de escala da fanfarra.', 'Pátio Central',
         timezone('utc', now()) + interval '95 days', NULL,
         true, NULL, 'inativo'::public.status_enum, u.id FROM u_coor u
  RETURNING id, titulo
),
ev1 AS (SELECT id FROM evt_ins WHERE titulo LIKE 'Conselho de Classe%'),
ev2 AS (SELECT id FROM evt_ins WHERE titulo LIKE 'Feira de Ciências%'),
ev3 AS (SELECT id FROM evt_ins WHERE titulo LIKE 'Festa Junina%'),
ev4 AS (SELECT id FROM evt_ins WHERE titulo LIKE 'Abertura do Ano Letivo%'),

-- 13. Associativa N:N escola_turmas_eventos (11 vínculos)
te_ins AS (
  INSERT INTO public.escola_turmas_eventos (evento_id, turma_id)
  SELECT ev1.id, t_26_101.id FROM ev1, t_26_101
  UNION ALL SELECT ev1.id, t_26_201.id FROM ev1, t_26_201
  UNION ALL SELECT ev1.id, t_26_301.id FROM ev1, t_26_301
  UNION ALL SELECT ev2.id, t_26_101.id FROM ev2, t_26_101
  UNION ALL SELECT ev2.id, t_26_201.id FROM ev2, t_26_201
  UNION ALL SELECT ev2.id, t_26_301.id FROM ev2, t_26_301
  UNION ALL SELECT ev2.id, t_26_901.id FROM ev2, t_26_901
  UNION ALL SELECT ev3.id, t_26_101.id FROM ev3, t_26_101
  UNION ALL SELECT ev3.id, t_26_901.id FROM ev3, t_26_901
  UNION ALL SELECT ev4.id, t_25_101.id FROM ev4, t_25_101
  UNION ALL SELECT ev4.id, t_25_301.id FROM ev4, t_25_301
  RETURNING evento_id
),

-- 14. Refeições PNAE/SED-SC (10 registros: semana completa em 2 turnos)
ref_ins AS (
  INSERT INTO public.escola_refeicoes (data, turno, descricao, observacoes)
  VALUES
    (CURRENT_DATE,     'matutino'::public.turno_enum,   'Arroz, feijão preto, frango desfiado e salada de cenoura.', 'Cardápio PNAE sem adição de açúcar.'),
    (CURRENT_DATE,     'vespertino'::public.turno_enum, 'Macarrão ao sugo com carne moída e maçã.', 'Opção sem lactose disponível mediante atestado.'),
    (CURRENT_DATE + 1, 'matutino'::public.turno_enum,   'Polenta cremosa com ragu de carne e couve refogada.', NULL),
    (CURRENT_DATE + 1, 'vespertino'::public.turno_enum, 'Arroz integral, lentilha, filé de peixe assado e banana.', 'Alimento oriundo da agricultura familiar.'),
    (CURRENT_DATE + 2, 'matutino'::public.turno_enum,   'Sopa de legumes com macarrão padre nosso e pão caseiro.', NULL),
    (CURRENT_DATE + 2, 'vespertino'::public.turno_enum, 'Arroz, feijão carioca, omelete de forno e beterraba.', 'Contém ovo.'),
    (CURRENT_DATE + 3, 'matutino'::public.turno_enum,   'Risoto de frango com abóbora e salada de alface.', NULL),
    (CURRENT_DATE + 3, 'vespertino'::public.turno_enum, 'Feijão tropeiro adaptado, arroz branco e laranja.', NULL),
    (CURRENT_DATE + 4, 'matutino'::public.turno_enum,   'Bolo de milho caseiro, leite com cacau e mamão.', 'Contém glúten e lactose.'),
    (CURRENT_DATE + 4, 'vespertino'::public.turno_enum, 'Sanduíche natural de atum com cenoura ralada e suco natural.', NULL)
  RETURNING id
)

-- 15. Notificações globais (3 alertas: 2 ativos vigentes, 1 inativo)
INSERT INTO public.escola_notificacoes (titulo, mensagem, importancia, ativa, data_inicio, data_fim)
VALUES
  ('Atenção: Mudança Temporária no Acesso Lateral', 'Durante esta semana, a entrada de estudantes ocorrerá pelo portão principal da Rua José Maria.', 'urgente'::public.importancia_enum, true, timezone('utc', now()) - interval '2 days', timezone('utc', now()) + interval '7 days'),
  ('Reunião Geral de Pais e Responsáveis', 'Próximo sábado às 09:00 no auditório. Presença fundamental.', 'importante'::public.importancia_enum, true, timezone('utc', now()) - interval '1 day', timezone('utc', now()) + interval '14 days'),
  ('Alerta Arquivado: Manutenção Elétrica', 'Aviso de manutenção já concluída.', 'normal'::public.importancia_enum, false, timezone('utc', now()) - interval '30 days', timezone('utc', now()) - interval '20 days');

COMMIT;
