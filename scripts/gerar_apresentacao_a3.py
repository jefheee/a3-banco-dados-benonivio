from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "03_apresentacao" / "Apresentacao_A3_Portal_Escolar.pptx"
IMG_DBDIAGRAM = ROOT / "01_modelagem" / "der_logico_dbdiagram.png"
IMG_MERMAID = ROOT / "01_modelagem" / "der_logico.png"

C_NAVY_DARK = RGBColor(0x0F, 0x17, 0x2A)
C_NAVY = RGBColor(0x1E, 0x3A, 0x8A)
C_BLUE = RGBColor(0x25, 0x63, 0xEB)
C_TEAL = RGBColor(0x0F, 0x76, 0x6E)
C_AMBER = RGBColor(0xD9, 0x77, 0x06)
C_ROSE = RGBColor(0xBE, 0x12, 0x3C)
C_BG_LIGHT = RGBColor(0xF8, 0xFA, 0xFC)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
C_TEXT = RGBColor(0x0F, 0x17, 0x2A)
C_MUTED = RGBColor(0x47, 0x55, 0x69)

FONT = "Segoe UI"


def put_run(p, text, size=14, color=C_TEXT, bold=False):
    r = p.add_run()
    r.text = str(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return r


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title, subtitle, slide_num):
    set_bg(slide, C_BG_LIGHT)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_NAVY_DARK
    bar.line.fill.background()

    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.08), Inches(13.333), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_BLUE
    accent.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.14), Inches(10.8), Inches(0.84))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    put_run(p1, title, size=24, color=C_WHITE, bold=True)

    p2 = tf.add_paragraph()
    put_run(p2, subtitle, size=13, color=RGBColor(0x94, 0xA3, 0xB8))

    nb = slide.shapes.add_textbox(Inches(11.65), Inches(0.34), Inches(1.15), Inches(0.4))
    np = nb.text_frame.paragraphs[0]
    np.alignment = PP_ALIGN.RIGHT
    put_run(np, f"{slide_num:02d} / 10", size=13, color=RGBColor(0x93, 0xC5, 0xFD), bold=True)


def add_card(slide, left, top, width, height, title=None, bullets=None, accent_color=C_BLUE, bg_color=C_WHITE, title_size=16, body_size=14.5):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.04
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1)

    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.1))
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.22), Inches(width - 0.5), Inches(height - 0.34))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    if title:
        p = tf.paragraphs[0]
        p.space_after = Pt(10)
        put_run(p, title, size=title_size, color=accent_color, bold=True)
        first = False
    if bullets:
        for b in bullets:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(9)
            if isinstance(b, tuple):
                bp, txt = b
                put_run(p, bp, size=body_size, color=C_TEXT, bold=True)
                put_run(p, txt, size=body_size, color=C_MUTED)
            else:
                put_run(p, f"• {b}", size=body_size, color=C_TEXT)
    return card


def add_table(slide, left, top, width, height, headers, rows, col_widths, font_size=13):
    tbl_shape = slide.shapes.add_table(1 + len(rows), len(headers), Inches(left), Inches(top), Inches(width), Inches(height))
    table = tbl_shape.table
    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        put_run(p, h, size=font_size, color=C_WHITE, bold=True)

    for r_i, row_data in enumerate(rows):
        bg = C_WHITE if r_i % 2 == 0 else RGBColor(0xF1, 0xF5, 0xF9)
        for c_i, val in enumerate(row_data):
            cell = table.cell(r_i + 1, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            put_run(p, val, size=font_size, color=C_TEXT, bold=(c_i == 0))
    return tbl_shape


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # SLIDE 1 — CAPA
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, C_NAVY_DARK)

    band = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.28), Inches(7.5))
    band.fill.solid()
    band.fill.fore_color.rgb = C_BLUE
    band.line.fill.background()

    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(1.0), Inches(7.8), Inches(0.46))
    badge.adjustments[0] = 0.5
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_NAVY
    badge.line.color.rgb = C_BLUE
    bp = badge.text_frame.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    put_run(bp, "AVALIAÇÃO A3  •  BANCO DE DADOS  •  UNISUL — CAMPUS PEDRA BRANCA · 2026", size=11, color=RGBColor(0x93, 0xC5, 0xFD), bold=True)

    tb1 = s1.shapes.add_textbox(Inches(0.95), Inches(1.8), Inches(11.4), Inches(2.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p_t = tf1.paragraphs[0]
    p_t.space_after = Pt(14)
    put_run(p_t, "Modelagem e Refatoração Relacional\nPortal Escolar EEB Prof. Benonívio João Martins", size=36, color=C_WHITE, bold=True)

    p_s = tf1.add_paragraph()
    put_run(p_s, "De 9 tabelas com JSONB para 15 tabelas em 3FN no PostgreSQL 17 / Supabase", size=18, color=RGBColor(0x94, 0xA3, 0xB8))

    card_meta = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(4.85), Inches(11.4), Inches(1.75))
    card_meta.adjustments[0] = 0.06
    card_meta.fill.solid()
    card_meta.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    card_meta.line.color.rgb = RGBColor(0x33, 0x41, 0x55)

    tm = s1.shapes.add_textbox(Inches(1.25), Inches(5.1), Inches(10.8), Inches(1.35))
    tfm = tm.text_frame
    tfm.word_wrap = True
    pm1 = tfm.paragraphs[0]
    pm1.space_after = Pt(10)
    put_run(pm1, "Equipe: ", size=14, color=RGBColor(0x93, 0xC5, 0xFD), bold=True)
    put_run(pm1, "Daniel Alves  •  Gabriel Grando  •  Jefherson Luiz  •  Maicon Lodetti", size=14, color=C_WHITE)

    pm2 = tfm.add_paragraph()
    put_run(pm2, "Professores: ", size=14, color=RGBColor(0x93, 0xC5, 0xFD), bold=True)
    put_run(pm2, "Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves", size=14, color=RGBColor(0xCB, 0xD5, 0xE1))

    # SLIDE 2 — O PROBLEMA REAL
    s2 = prs.slides.add_slide(blank)
    add_header(s2, "O Problema Real", "Por que refatorar o banco de dados do Portal Escolar (escolabenonivio.vercel.app)", 2)

    add_card(
        s2, 0.6, 1.5, 5.95, 5.3,
        title="Dores do Banco Legado",
        bullets=[
            ("JSONB Multivalorado: ", "Fotos e links sem chave estrangeira."),
            ("Sem Histórico Letivo: ", "Virada de ano sobrescrevia turmas."),
            ("Turno Redundante: ", "Grupos de WhatsApp repetiam dados da turma."),
            ("Sem Travas no SGBD: ", "RLS permissivo e ausência de CHECKs."),
        ],
        accent_color=C_ROSE,
        title_size=18,
        body_size=15,
    )
    add_card(
        s2, 6.8, 1.5, 5.95, 5.3,
        title="Objetivos da Refatoração",
        bullets=[
            ("Preservar Histórico: ", "Anos letivos de 2025, 2026+ coexistindo."),
            ("Integridade Nativa: ", "UNIQUE, CHECK e FK travando lixo no banco."),
            ("Segurança por Papel: ", "Visitante vê só publicados; equipe gerencia."),
            ("Documentação Fiel: ", "DDL, Dicionário e DER 100% sincronizados."),
        ],
        accent_color=C_TEAL,
        title_size=18,
        body_size=15,
    )

    # SLIDE 3 — ANTES VS. DEPOIS
    s3 = prs.slides.add_slide(blank)
    add_header(s3, "Antes vs. Depois", "Comparativo estrutural entre o legado em produção e a entrega final", 3)

    add_table(
        s3, 0.6, 1.45, 12.13, 4.45,
        ["Dimensão", "Cenário Legado", "Modelo Final A3 (vFinal)"],
        [
            ["Estrutura", "9 tabelas com arrays JSONB", "15 tabelas normalizadas (1FN–3FN)"],
            ["Domínios", "Textos livres sem validação", "5 ENUMs explícitos no PostgreSQL"],
            ["Relacionamentos", "Sem política ON DELETE padrão", "13 FKs (CASCADE vs. SET NULL)"],
            ["Integridade", "Concentrada apenas no frontend", "CHECKs de data, slug, e-mail e texto"],
            ["Exposição Pública", "Leitura direta sem filtro central", "2 Views (WITH security_invoker = true)"],
            ["Segurança (RLS)", "Políticas heterogêneas sem controle por papel (role)", "70 políticas granulares por operação"],
        ],
        [2.6, 4.4, 5.13],
        font_size=13.5,
    )

    add_card(
        s3, 0.6, 6.15, 12.13, 0.88,
        bullets=[("Advisors do Supabase: ", "0 alertas de políticas duplicadas e 0 alertas de search_path mutável.")],
        accent_color=C_NAVY,
        body_size=14,
    )

    # SLIDE 4 — NORMALIZAÇÃO NA PRÁTICA
    s4 = prs.slides.add_slide(blank)
    add_header(s4, "Normalização na Prática", "Aplicação objetiva de 1FN, 2FN e 3FN no domínio escolar", 4)

    add_card(
        s4, 0.6, 1.5, 3.85, 5.3,
        title="1FN — Atomicidade",
        bullets=[
            "Fim dos arrays JSONB.",
            "3 tabelas filhas: avisos_imagens, acervo_imagens e turmas_links.",
            "Coluna ordem >= 0 com UNIQUE (pai_id, ordem).",
        ],
        accent_color=C_BLUE,
        title_size=17,
        body_size=14.5,
    )
    add_card(
        s4, 4.74, 1.5, 3.85, 5.3,
        title="2FN — Sem Parcialidade",
        bullets=[
            "Relação N:N entre eventos e turmas.",
            "Tabela associativa escola_turmas_eventos.",
            "PK composta (evento_id, turma_id) sem atributos extras.",
        ],
        accent_color=C_TEAL,
        title_size=17,
        body_size=14.5,
    )
    add_card(
        s4, 8.88, 1.5, 3.85, 5.3,
        title="3FN — Sem Transitividade",
        bullets=[
            "Removido turno de escola_whatsapp_grupos.",
            "Turno obtido por JOIN com escola_turmas.",
            "ano_letivo preserva 2025 e 2026 sem sobrescrita.",
        ],
        accent_color=C_AMBER,
        title_size=17,
        body_size=14.5,
    )

    # SLIDE 5 — VISÃO GERAL DO DER
    s5 = prs.slides.add_slide(blank)
    add_header(s5, "Visão Geral do DER", "15 tabelas organizadas em 5 subsistemas funcionais (dbdiagram.io)", 5)

    add_card(
        s5, 0.6, 1.4, 5.85, 5.65,
        title="5 Subsistemas do Modelo",
        bullets=[
            ("Identidade: ", "escola_usuarios (admin e editor)."),
            ("Turmas: ", "turmas (ano_letivo), links, posts e WhatsApp (1:1)."),
            ("Mural: ", "avisos, imagens, páginas fixas e alertas."),
            ("Memória: ", "acervo histórico, imagens e documentos."),
            ("Calendário: ", "eventos, turmas_eventos (N:N) e refeições."),
        ],
        accent_color=C_NAVY,
        title_size=18,
        body_size=15,
    )

    frame_left, frame_top, frame_w, frame_h = 6.7, 1.4, 6.03, 5.65
    frame = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(frame_left), Inches(frame_top), Inches(frame_w), Inches(frame_h))
    frame.adjustments[0] = 0.02
    frame.fill.solid()
    frame.fill.fore_color.rgb = C_WHITE
    frame.line.color.rgb = C_BORDER

    img_der = IMG_DBDIAGRAM if IMG_DBDIAGRAM.exists() else IMG_MERMAID
    if img_der.exists():
        with Image.open(img_der) as im:
            iw, ih = im.size
        pad = 0.12
        max_w = frame_w - 2 * pad
        max_h = frame_h - 2 * pad
        ratio = min(max_w / iw, max_h / ih)
        disp_w = iw * ratio
        disp_h = ih * ratio
        pic_left = frame_left + (frame_w - disp_w) / 2
        pic_top = frame_top + (frame_h - disp_h) / 2
        s5.shapes.add_picture(str(img_der), Inches(pic_left), Inches(pic_top), width=Inches(disp_w), height=Inches(disp_h))

    # SLIDE 6 — INTEGRIDADE E SEGURANÇA NO SGBD
    s6 = prs.slides.add_slide(blank)
    add_header(s6, "Integridade e Segurança no SGBD", "Regras declarativas no PostgreSQL 17 que protegem os dados", 6)

    add_card(
        s6, 0.6, 1.45, 5.95, 2.6,
        title="Constraints (CHECK & UNIQUE)",
        bullets=[
            "length(btrim(col)) > 0 contra textos vazios.",
            "Datas coerentes e regex em slug e e-mail.",
            "Chaves naturais em turma e refeição.",
        ],
        accent_color=C_BLUE,
        title_size=16.5,
        body_size=14,
    )
    add_card(
        s6, 6.8, 1.45, 5.95, 2.6,
        title="Integridade Referencial & Triggers",
        bullets=[
            "ON DELETE CASCADE em itens dependentes.",
            "ON DELETE SET NULL nas 6 FKs de autoria.",
            "Trigger única de updated_at com search_path = ''.",
        ],
        accent_color=C_TEAL,
        title_size=16.5,
        body_size=14,
    )
    add_card(
        s6, 0.6, 4.3, 12.15, 2.6,
        title="RLS Granular + Views Públicas (security_invoker = true)",
        bullets=[
            ("anon: ", "lê apenas publicados, ativos e dentro da vigência."),
            ("authenticated: ", "escola_is_editor() e escola_is_admin() controlam escrita e papéis."),
            ("Views: ", "escola_avisos_publicos e escola_eventos_publicos respeitam RLS do invocador."),
        ],
        accent_color=C_NAVY,
        title_size=16.5,
        body_size=14,
    )

    # SLIDE 7 — PROVA 1: CRASH TESTS AO VIVO
    s7 = prs.slides.add_slide(blank)
    add_header(s7, "Prova 1 — Crash Tests ao Vivo", "6 testes de falha intencional (05_crash_test_integridade.sql)", 7)

    add_table(
        s7, 0.6, 1.45, 12.13, 4.65,
        ["Teste", "Tentativa Inválida", "SQLSTATE", "Constraint Que Bloqueou"],
        [
            ["T1", "Turma duplicada (2026 / 1º Ano / 101 / matutino)", "23505", "uq_turmas_ano_letivo_serie_nome_turno"],
            ["T2", "2º cardápio no mesmo dia e turno", "23505", "uq_refeicoes_data_turno"],
            ["T3", "2º grupo de WhatsApp para a mesma turma", "23505", "escola_whatsapp_grupos_turma_id_key"],
            ["T4", "Evento com data_fim < data_inicio", "23514", "ck_eventos_datas"],
            ["T5", "E-mail inválido / nome vazio / slug com espaço", "23514", "ck_..._email_valido / nome_check / slug_formato"],
            ["T6", "Post para turma_id UUID inexistente", "23503", "escola_turmas_posts_turma_id_fkey"],
        ],
        [1.1, 5.2, 1.35, 4.48],
        font_size=12.5,
    )

    add_card(
        s7, 0.6, 6.28, 12.13, 0.78,
        bullets=[("Execução Segura: ", "Todos rodam em BEGIN; ... ROLLBACK; — bloqueiam o erro sem sujar o banco.")],
        accent_color=C_ROSE,
        body_size=13.5,
    )

    # SLIDE 8 — PROVA 2: CONSULTAS SQL AO VIVO
    s8 = prs.slides.add_slide(blank)
    add_header(s8, "Prova 2 — Consultas SQL ao Vivo (DQL)", "Consultas analíticas executadas em 06_consultas_apresentacao.sql", 8)

    add_card(
        s8, 0.6, 1.45, 5.95, 2.55,
        title="Q1 & Q4 — JOIN 3FN e HAVING",
        bullets=[
            ("Q1: ", "Turmas 2026 + WhatsApp ativo + total de links."),
            ("Q4: ", "GROUP BY + HAVING >= 2 links (4 turmas)."),
        ],
        accent_color=C_BLUE,
        title_size=16.5,
        body_size=14,
    )
    add_card(
        s8, 6.8, 1.45, 5.95, 2.55,
        title="Q2 & Q3 — Agregações e N:N",
        bullets=[
            ("Q2: ", "COUNT, SUM (MB) e AVG (KB) de documentos."),
            ("Q3: ", "MIN/MAX de eventos ativos + contagem N:N."),
        ],
        accent_color=C_TEAL,
        title_size=16.5,
        body_size=14,
    )
    add_card(
        s8, 0.6, 4.28, 5.95, 2.55,
        title="Q5 & Q6 — LEFT JOIN e NOT EXISTS",
        bullets=[
            ("Q5: ", "Todas as 6 turmas com COALESCE(posts, 0)."),
            ("Q6: ", "Detecta turma 2026-901 sem WhatsApp."),
        ],
        accent_color=C_AMBER,
        title_size=16.5,
        body_size=14,
    )
    add_card(
        s8, 6.8, 4.28, 5.95, 2.55,
        title="Q7 & Q8 — Histórico e Views",
        bullets=[
            ("Q7: ", "Comparativo 2025 (3 posts) vs. 2026 (6 posts)."),
            ("Q8: ", "Views filtram avisos (4/6) e eventos (3/5)."),
        ],
        accent_color=C_NAVY,
        title_size=16.5,
        body_size=14,
    )

    # SLIDE 9 — EVIDÊNCIA DO BANCO POPULADO
    s9 = prs.slides.add_slide(blank)
    add_header(s9, "Evidência do Banco Populado", "102 registros realistas distribuídos nas 15 tabelas e Advisors limpos", 9)

    add_table(
        s9, 0.6, 1.45, 7.5, 5.45,
        ["Tabela", "Qtd", "Tabela", "Qtd"],
        [
            ["escola_usuarios", "4", "escola_acervo_imagens", "8"],
            ["escola_turmas (2025/2026)", "6", "escola_documentos", "6"],
            ["escola_whatsapp_grupos", "5", "escola_conteudo_paginas", "4"],
            ["escola_turmas_links", "11", "escola_eventos", "5"],
            ["escola_turmas_posts", "9", "escola_turmas_eventos", "11"],
            ["escola_avisos", "6", "escola_refeicoes", "10"],
            ["escola_avisos_imagens", "10", "escola_notificacoes", "3"],
            ["escola_acervo", "4", "TOTAL GERAL", "102"],
        ],
        [2.85, 0.9, 2.85, 0.9],
        font_size=12,
    )

    add_card(
        s9, 8.35, 1.45, 4.38, 5.45,
        title="Validação Supabase",
        bullets=[
            "0 políticas RLS duplicadas.",
            "0 funções com search_path mutável.",
            "Views ocultam rascunhos e arquivados.",
            "Seed idempotente via CTEs + RETURNING.",
        ],
        accent_color=C_TEAL,
        title_size=17,
        body_size=14.5,
    )

    # SLIDE 10 — PRÓXIMOS PASSOS E ENCERRAMENTO
    s10 = prs.slides.add_slide(blank)
    set_bg(s10, C_NAVY_DARK)

    band10 = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.28), Inches(7.5))
    band10.fill.solid()
    band10.fill.fore_color.rgb = C_TEAL
    band10.line.fill.background()

    tb10 = s10.shapes.add_textbox(Inches(0.95), Inches(0.85), Inches(11.4), Inches(1.2))
    tf10 = tb10.text_frame
    p10 = tf10.paragraphs[0]
    put_run(p10, "Próximos Passos & Encerramento", size=32, color=C_WHITE, bold=True)

    p10s = tf10.add_paragraph()
    put_run(p10s, "Da homologação na A3 para a evolução segura em produção", size=15, color=RGBColor(0x94, 0xA3, 0xB8))

    add_card(
        s10, 0.95, 2.35, 5.5, 3.15,
        title="Roteiro Pós-A3 (Produção)",
        bullets=[
            "Migrar JSONBs legados via ETL controlado.",
            "Ativar FK de escola_usuarios para auth.users.",
            "Atualizar queries do Next.js (lib/data/).",
        ],
        accent_color=C_BLUE,
        title_size=17,
        body_size=14.5,
    )
    add_card(
        s10, 6.85, 2.35, 5.5, 3.15,
        title="Entregáveis em 04_entrega_final/",
        bullets=[
            "Dicionário de Dados (DOCX e PDF).",
            "Apresentação (PPTX e PDF) + Roteiro.",
            "DDL, Seed, Crash Tests, DQL e DERs.",
        ],
        accent_color=C_TEAL,
        title_size=17,
        body_size=14.5,
    )

    tbf = s10.shapes.add_textbox(Inches(0.95), Inches(5.95), Inches(11.4), Inches(0.9))
    tbf.text_frame.word_wrap = True
    pff = tbf.text_frame.paragraphs[0]
    pff.alignment = PP_ALIGN.CENTER
    pff.space_after = Pt(4)
    put_run(pff, "Obrigado! | Daniel Alves, Gabriel Grando, Jefherson Luiz e Maicon Lodetti", size=15, color=RGBColor(0x93, 0xC5, 0xFD), bold=True)
    pff2 = tbf.text_frame.add_paragraph()
    pff2.alignment = PP_ALIGN.CENTER
    put_run(pff2, "Professores: Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves  •  UNISUL 2026", size=13, color=RGBColor(0xCB, 0xD5, 0xE1))

    prs.save(str(OUT_PATH))
    print("PPTX_SAVED:", OUT_PATH)


if __name__ == "__main__":
    build_deck()
