from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
OUT_PPTX = ROOT / "03_apresentacao" / "Apresentacao_A3_Portal_Escolar.pptx"
IMG_CONCEITUAL = ROOT / "01_modelagem" / "der_conceitual.png"
IMG_LOGICO = ROOT / "01_modelagem" / "der_logico_dbdiagram.png"

# Paleta minimalista (3 tons principais + neutros)
C_NAVY = RGBColor(0x0F, 0x25, 0x37)
C_BLUE = RGBColor(0x1E, 0x40, 0xAF)
C_ACCENT = RGBColor(0x38, 0xBD, 0xF8)
C_DARK = RGBColor(0x1E, 0x29, 0x3B)
C_MUTED = RGBColor(0x64, 0x74, 0x8B)
C_SOFT_ON_DARK = RGBColor(0x94, 0xA3, 0xB8)
C_LIGHT_MUTED = RGBColor(0xCB, 0xD5, 0xE1)
C_BORDER = RGBColor(0xE2, 0xE8, 0xF0)
C_BG_SOFT = RGBColor(0xF8, 0xFA, 0xFC)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_TEAL = RGBColor(0x0F, 0x76, 0x6E)

FONT = "Segoe UI"
AUTHORS_RA = [
    "Daniel Alves — RA: 1072517730",
    "Gabriel Grando — RA: 10725118226",
    "Jefherson Luiz — RA: 10725114819",
    "Maicon Lodetti — RA: 1072511629",
]
PROFESSORES = "Professores: Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves"


def set_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, fill_color, border_color=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    if border_color:
        shp.line.color.rgb = border_color
        shp.line.width = Pt(0.75)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(slide, x, y, w, h, text, size=18, bold=False, color=C_DARK, align=PP_ALIGN.LEFT, line_spacing=1.2):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tb


def add_bullets(slide, x, y, w, h, items, size=16.5, color=C_DARK, space_after=12, line_spacing=1.22):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0.02)
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        if isinstance(item, tuple):
            r1 = p.add_run()
            r1.text = "•  " + item[0]
            r1.font.name = FONT
            r1.font.size = Pt(size)
            r1.font.bold = True
            r1.font.color.rgb = C_NAVY
            r2 = p.add_run()
            r2.text = item[1]
            r2.font.name = FONT
            r2.font.size = Pt(size)
            r2.font.color.rgb = color
        else:
            r = p.add_run()
            r.text = "•  " + item
            r.font.name = FONT
            r.font.size = Pt(size)
            r.font.color.rgb = color
    return tb


def add_content_chrome(slide, title, slide_num, total=10):
    set_bg(slide, C_WHITE)
    # Fina barra superior minimalista
    add_rect(slide, 0, 0, 13.333, 0.06, C_BLUE)
    # Eyebrow discreto
    add_text(slide, 0.75, 0.28, 8.5, 0.28, "BANCO DE DADOS · AVALIAÇÃO A3", size=9.5, bold=True, color=C_MUTED)
    # Titulo principal
    add_text(slide, 0.75, 0.56, 11.8, 0.58, title, size=26, bold=True, color=C_NAVY)
    # Linha fina separadora
    add_rect(slide, 0.75, 1.22, 11.83, 0.015, C_BORDER)
    # Rodape discreto
    add_rect(slide, 0.75, 6.96, 11.83, 0.012, C_BORDER)
    add_text(slide, 0.75, 7.04, 9.0, 0.28, "Portal Escolar EEB Prof. Benonívio João Martins  ·  UNISUL 2026", size=9.5, color=C_MUTED)
    add_text(slide, 11.2, 7.04, 1.38, 0.28, f"{slide_num:02d} / {total:02d}", size=9.5, bold=True, color=C_MUTED, align=PP_ALIGN.RIGHT)


def add_fitted_image(slide, img_path, x, y, max_w, max_h):
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    fw, fh = iw * ratio, ih * ratio
    px = x + (max_w - fw) / 2
    py = y + (max_h - fh) / 2
    slide.shapes.add_picture(str(img_path), Inches(px), Inches(py), width=Inches(fw), height=Inches(fh))


def style_table_cell(cell, text, size=14.5, bold=False, color=C_DARK, bg=None, align=PP_ALIGN.LEFT):
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.16)
    cell.margin_right = Inches(0.16)
    cell.margin_top = Inches(0.10)
    cell.margin_bottom = Inches(0.10)
    if bg:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.15
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1 — CAPA (Fundo azul-marinho profundo)
    # =========================================================================
    s1 = prs.slides.add_slide(blank)
    set_bg(s1, C_NAVY)
    add_rect(s1, 0, 0, 13.333, 0.08, C_ACCENT)

    add_text(
        s1, 0.9, 0.72, 11.5, 0.35,
        "UNISUL — CAMPUS PEDRA BRANCA  ·  ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
        size=11, bold=True, color=C_ACCENT
    )
    add_text(
        s1, 0.9, 1.35, 11.5, 1.45,
        "Portal Escolar EEB Prof. Benonívio João Martins",
        size=38, bold=True, color=C_WHITE, line_spacing=1.12
    )
    add_text(
        s1, 0.9, 2.72, 10.8, 0.65,
        "Modelagem e Reconstrução Relacional do Banco de Dados  —  Avaliação A3",
        size=19, color=C_LIGHT_MUTED
    )

    add_rect(s1, 0.9, 3.60, 2.2, 0.04, C_ACCENT)

    # 4 Integrantes com RA em 2 colunas limpas
    add_text(s1, 0.9, 3.92, 6.0, 0.32, "INTEGRANTES", size=10.5, bold=True, color=C_ACCENT)
    for idx, author in enumerate(AUTHORS_RA):
        col = idx % 2
        row = idx // 2
        ax = 0.9 + col * 5.6
        ay = 4.32 + row * 0.48
        add_text(s1, ax, ay, 5.4, 0.40, author, size=16.5, bold=False, color=C_WHITE)

    add_rect(s1, 0.9, 5.88, 11.5, 0.015, RGBColor(0x28, 0x42, 0x58))
    add_text(s1, 0.9, 6.08, 11.5, 0.36, PROFESSORES, size=14, color=C_LIGHT_MUTED)
    add_text(s1, 0.9, 6.46, 11.5, 0.32, "Unidade Curricular: Banco de Dados  ·  Palhoça - SC, 2026", size=12.5, color=C_SOFT_ON_DARK)

    # =========================================================================
    # SLIDE 2 — O PROJETO REAL
    # =========================================================================
    s2 = prs.slides.add_slide(blank)
    add_content_chrome(s2, "O Projeto Real", 2)

    add_text(
        s2, 0.75, 1.55, 7.6, 0.85,
        "O Portal Escolar da EEB Prof. Benonívio João Martins já está no ar atendendo alunos, famílias e equipe pedagógica em Palhoça (SC).",
        size=18.5, bold=True, color=C_NAVY, line_spacing=1.25
    )

    add_bullets(
        s2, 0.75, 2.86, 7.6, 3.85,
        [
            ("O que o sistema gerencia: ", "avisos com galerias, turmas, grupos de WhatsApp, links de aula, eventos, documentos oficiais, acervo histórico e cardápio."),
            ("Motivação da A3: ", "reconstruir o banco de dados de forma estruturada e normalizada (1FN, 2FN e 3FN) para garantir integridade e manter o histórico escolar ano após ano."),
            ("Portal em produção: ", "escolabenonivio.vercel.app (Next.js + PostgreSQL / Supabase)."),
            ("Código original: ", "github.com/jefheee/escola-benonivio."),
        ],
        size=16, space_after=15, line_spacing=1.25
    )

    # Coluna direita minimalista com 3 indicadores limpos (sem caixas pesadas)
    add_rect(s2, 8.85, 1.55, 0.015, 4.95, C_BORDER)
    metrics = [
        ("15", "Tabelas normalizadas", "Organizadas em 1FN, 2FN e 3FN"),
        ("5", "Tipos enumerados", "Valores padronizados no PostgreSQL"),
        ("2", "Views públicas", "Filtram rascunhos e avisos vencidos"),
    ]
    for idx, (num, lbl, sub) in enumerate(metrics):
        my = 1.65 + idx * 1.68
        add_text(s2, 9.25, my, 3.3, 0.65, num, size=38, bold=True, color=C_BLUE)
        add_text(s2, 9.25, my + 0.66, 3.3, 0.34, lbl, size=15.5, bold=True, color=C_NAVY)
        add_text(s2, 9.25, my + 0.98, 3.3, 0.36, sub, size=13, color=C_MUTED)

    # =========================================================================
    # SLIDE 3 — O QUE MUDOU (ANTES VS. DEPOIS)
    # =========================================================================
    s3 = prs.slides.add_slide(blank)
    add_content_chrome(s3, "O Que Mudou (Antes vs. Depois)", 3)

    add_text(
        s3, 0.75, 1.48, 11.8, 0.42,
        "Comparação direta entre a primeira versão do banco em produção e a nova arquitetura da A3.",
        size=15.5, color=C_MUTED
    )

    rows_s3 = [
        ("Estrutura", "9 tabelas com listas em JSON", "15 tabelas organizadas (1FN, 2FN e 3FN)"),
        ("Histórico escolar", "Turmas sobrescritas na virada do ano", "Separação por ano letivo (2025, 2026+)"),
        ("Dados repetidos", "Turno duplicado em grupos de WhatsApp", "Turno único em escola_turmas (3FN)"),
        ("Validações", "Regras concentradas apenas no site", "Chaves únicas, datas e textos validados no banco"),
        ("Controle de acesso", "Leitura pública sem separação por perfil", "Visitante vê publicados; equipe gerencia"),
    ]
    tbl_shp = s3.shapes.add_table(len(rows_s3) + 1, 3, Inches(0.75), Inches(2.08), Inches(11.83), Inches(4.45))
    tbl = tbl_shp.table
    tbl.columns[0].width = Inches(2.55)
    tbl.columns[1].width = Inches(4.55)
    tbl.columns[2].width = Inches(4.73)

    for c_i, h_txt in enumerate(["Aspecto", "Versão Inicial (Produção)", "Nova Estrutura (A3)"]):
        style_table_cell(tbl.cell(0, c_i), h_txt, size=15, bold=True, color=C_WHITE, bg=C_NAVY)

    for r_i, (asp, ant, dep) in enumerate(rows_s3, start=1):
        bg = C_BG_SOFT if r_i % 2 == 0 else C_WHITE
        style_table_cell(tbl.cell(r_i, 0), asp, size=15, bold=True, color=C_NAVY, bg=bg)
        style_table_cell(tbl.cell(r_i, 1), ant, size=15, color=C_MUTED, bg=bg)
        style_table_cell(tbl.cell(r_i, 2), dep, size=15, bold=True, color=C_DARK, bg=bg)

    # =========================================================================
    # SLIDE 4 — NORMALIZAÇÃO (1FN, 2FN E 3FN) NA PRÁTICA
    # =========================================================================
    s4 = prs.slides.add_slide(blank)
    add_content_chrome(s4, "Normalização (1FN, 2FN e 3FN) na Prática", 4)

    cols_fn = [
        (
            "1FN",
            "Sem listas dentro de colunas",
            C_BLUE,
            "Antes, fotos e links ficavam agrupados em listas JSON dentro da mesma coluna.",
            "Agora cada foto e cada link tem seu próprio registro ordenado em tabelas ligadas: escola_avisos_imagens, escola_acervo_imagens e escola_turmas_links."
        ),
        (
            "2FN",
            "Relação muitos-para-muitos",
            C_TEAL,
            "Um evento pode envolver várias turmas e uma turma pode participar de vários eventos.",
            "Criamos a tabela intermediária escola_turmas_eventos com chave composta (evento_id, turma_id), eliminando repetições."
        ),
        (
            "3FN",
            "Sem dado dependente repetido",
            C_NAVY,
            "Antes, o campo turno era cadastrado na turma e repetido no grupo de WhatsApp.",
            "Removemos turno de escola_whatsapp_grupos: ele pertence apenas a escola_turmas e é consultado via JOIN."
        ),
    ]

    col_w = 3.62
    gap = 0.48
    for idx, (tag, sub, accent, antes_txt, depois_txt) in enumerate(cols_fn):
        cx = 0.75 + idx * (col_w + gap)
        add_rect(s4, cx, 1.65, col_w, 0.06, accent)
        add_text(s4, cx, 1.86, col_w, 0.62, tag, size=32, bold=True, color=accent)
        add_text(s4, cx, 2.50, col_w, 0.42, sub, size=16.5, bold=True, color=C_NAVY)
        add_text(s4, cx, 3.08, col_w, 1.25, antes_txt, size=15.5, color=C_MUTED, line_spacing=1.25)
        add_rect(s4, cx, 4.42, 0.9, 0.02, C_BORDER)
        add_text(s4, cx, 4.62, col_w, 1.95, depois_txt, size=15.5, bold=False, color=C_DARK, line_spacing=1.25)

    # =========================================================================
    # SLIDE 5 — DIAGRAMA CONCEITUAL
    # =========================================================================
    s5 = prs.slides.add_slide(blank)
    add_content_chrome(s5, "Diagrama Conceitual", 5)

    if IMG_CONCEITUAL.exists():
        add_fitted_image(s5, IMG_CONCEITUAL, x=0.65, y=1.36, max_w=8.15, max_h=5.45)

    add_rect(s5, 8.95, 1.50, 0.015, 5.20, C_BORDER)
    add_text(s5, 9.25, 1.55, 3.35, 0.42, "Ligações principais", size=17.5, bold=True, color=C_NAVY)
    add_bullets(
        s5, 9.25, 2.10, 3.35, 4.55,
        [
            ("1:1 (Turma – WhatsApp): ", "cada turma tem no máximo um grupo oficial."),
            ("1:N (Composição): ", "avisos e acervo possuem várias imagens; turmas possuem posts e links."),
            ("N:N (Eventos – Turmas): ", "eventos envolvem várias turmas e vice-versa."),
            ("0..1:N (Autoria): ", "conteúdos registram o usuário autor de forma opcional."),
        ],
        size=14.5, space_after=14, line_spacing=1.22
    )

    # =========================================================================
    # SLIDE 6 — DIAGRAMA LÓGICO (NOVO COMPACT)
    # =========================================================================
    s6 = prs.slides.add_slide(blank)
    add_content_chrome(s6, "Diagrama Lógico (15 Tabelas e 13 Chaves Estrangeiras)", 6)

    if IMG_LOGICO.exists():
        add_fitted_image(s6, IMG_LOGICO, x=0.45, y=1.28, max_w=8.65, max_h=5.62)

    add_rect(s6, 9.22, 1.48, 0.015, 5.25, C_BORDER)
    add_text(s6, 9.50, 1.52, 3.15, 0.40, "5 grupos de tabelas", size=17.5, bold=True, color=C_NAVY)
    add_bullets(
        s6, 9.50, 2.05, 3.15, 4.65,
        [
            ("Acesso: ", "escola_usuarios."),
            ("Turmas: ", "turmas, whatsapp_grupos, links e posts."),
            ("Mural: ", "avisos e avisos_imagens."),
            ("Memória e Arquivos: ", "acervo, acervo_imagens, documentos e paginas."),
            ("Agenda e Rotina: ", "eventos, turmas_eventos, refeicoes e notificacoes."),
        ],
        size=14, space_after=13, line_spacing=1.22
    )

    # =========================================================================
    # SLIDE 7 — REGRAS DE INTEGRIDADE E SEGURANÇA
    # =========================================================================
    s7 = prs.slides.add_slide(blank)
    add_content_chrome(s7, "Regras de Integridade e Segurança", 7)

    quads = [
        (
            0.75, 1.65, C_BLUE,
            "Chaves únicas no banco",
            "Não permite duplicar turma no mesmo ano letivo, série e turno, nem cadastrar dois cardápios para a mesma data e turno."
        ),
        (
            6.95, 1.65, C_TEAL,
            "Validações automáticas",
            "Bloqueia textos em branco, e-mails mal formatados, endereços de página inválidos e eventos com data final antes da inicial."
        ),
        (
            0.75, 4.30, C_NAVY,
            "Regras de exclusão (CASCADE e SET NULL)",
            "CASCADE remove imagens e links se o item pai for apagado; SET NULL mantém avisos e documentos mesmo se um operador sair."
        ),
        (
            6.95, 4.30, C_BLUE,
            "Views e controle de acesso",
            "Visitantes enxergam apenas conteúdos publicados e dentro do prazo; administradores e editores gerenciam os cadastros."
        ),
    ]
    for qx, qy, qcol, qtitle, qdesc in quads:
        add_rect(s7, qx, qy, 0.07, 2.05, qcol)
        add_text(s7, qx + 0.28, qy + 0.05, 5.35, 0.45, qtitle, size=18.5, bold=True, color=C_NAVY)
        add_text(s7, qx + 0.28, qy + 0.60, 5.35, 1.45, qdesc, size=15.5, color=C_DARK, line_spacing=1.28)

    # =========================================================================
    # SLIDE 8 — TESTES DE VALIDAÇÃO NO BANCO
    # =========================================================================
    s8 = prs.slides.add_slide(blank)
    add_content_chrome(s8, "Testes de Validação no Banco", 8)

    add_text(
        s8, 0.75, 1.48, 11.8, 0.42,
        "Simulamos erros propositais no PostgreSQL para comprovar que as regras funcionam na prática:",
        size=15.5, color=C_MUTED
    )

    tests_s8 = [
        ("1. Duplicar turma", "Inserir a mesma turma no mesmo ano letivo, série e turno", "Bloqueado por chave única"),
        ("2. Duplicar cardápio", "Cadastrar dois cardápios na mesma data e mesmo turno", "Bloqueado por chave única"),
        ("3. Segundo WhatsApp", "Vincular um 2º grupo de WhatsApp à mesma turma", "Bloqueado pela relação 1:1"),
        ("4. Data invertida", "Cadastrar evento com data de término anterior ao início", "Bloqueado por regra CHECK"),
    ]
    t8_shp = s8.shapes.add_table(len(tests_s8) + 1, 3, Inches(0.75), Inches(2.08), Inches(11.83), Inches(3.85))
    t8 = t8_shp.table
    t8.columns[0].width = Inches(2.75)
    t8.columns[1].width = Inches(5.78)
    t8.columns[2].width = Inches(3.30)

    for c_i, h_txt in enumerate(["Teste", "Situação Inválida Simulada", "Resposta do Banco"]):
        style_table_cell(t8.cell(0, c_i), h_txt, size=15, bold=True, color=C_WHITE, bg=C_NAVY)

    for r_i, (tname, scen, res) in enumerate(tests_s8, start=1):
        bg = C_BG_SOFT if r_i % 2 == 0 else C_WHITE
        style_table_cell(t8.cell(r_i, 0), tname, size=15, bold=True, color=C_NAVY, bg=bg)
        style_table_cell(t8.cell(r_i, 1), scen, size=15, color=C_DARK, bg=bg)
        style_table_cell(t8.cell(r_i, 2), res, size=15, bold=True, color=C_TEAL, bg=bg)

    add_text(
        s8, 0.75, 6.18, 11.8, 0.55,
        "Também testamos e-mail inválido, nome em branco e post para turma inexistente — todos bloqueados automaticamente pelo PostgreSQL.",
        size=14.5, color=C_MUTED
    )

    # =========================================================================
    # SLIDE 9 — DEMONSTRAÇÃO DAS CONSULTAS SQL
    # =========================================================================
    s9 = prs.slides.add_slide(blank)
    add_content_chrome(s9, "Demonstração das Consultas SQL", 9)

    add_text(
        s9, 0.75, 1.48, 11.8, 0.42,
        "Quatro perguntas reais da escola respondidas ao vivo no Supabase com 102 registros de exemplo:",
        size=15.5, color=C_MUTED
    )

    queries = [
        (
            0.75, 2.15, "01",
            "Turmas de 2026 com WhatsApp e Links",
            "Une turmas, grupos de WhatsApp e links usando JOIN — mostrando na prática que não precisamos repetir o turno."
        ),
        (
            6.95, 2.15, "02",
            "Documentos por categoria",
            "Usa COUNT, SUM e AVG para resumir quantos arquivos existem e quanto espaço ocupam em cada categoria."
        ),
        (
            0.75, 4.45, "03",
            "Turmas sem grupo de WhatsApp",
            "Usa LEFT JOIN e NOT EXISTS para encontrar rapidamente a turma 901 que ainda está sem grupo cadastrado."
        ),
        (
            6.95, 4.45, "04",
            "Histórico 2025 vs. 2026 e Views",
            "Compara posts entre os dois anos letivos e mostra as Views filtrando automaticamente rascunhos e avisos expirados."
        ),
    ]
    for qx, qy, qnum, qtitle, qdesc in queries:
        add_text(s9, qx, qy, 0.72, 0.52, qnum, size=24, bold=True, color=C_BLUE)
        add_text(s9, qx + 0.75, qy + 0.04, 5.10, 0.44, qtitle, size=17.5, bold=True, color=C_NAVY)
        add_text(s9, qx + 0.75, qy + 0.62, 5.05, 1.30, qdesc, size=15, color=C_DARK, line_spacing=1.25)

    # =========================================================================
    # SLIDE 10 — ENCERRAMENTO (Fundo azul-marinho profundo igual à capa)
    # =========================================================================
    s10 = prs.slides.add_slide(blank)
    set_bg(s10, C_NAVY)
    add_rect(s10, 0, 0, 13.333, 0.08, C_ACCENT)

    add_text(s10, 0.9, 1.25, 11.5, 0.95, "Obrigado!", size=44, bold=True, color=C_WHITE)
    add_text(
        s10, 0.9, 2.28, 11.5, 0.50,
        "Portal Escolar EEB Prof. Benonívio João Martins  ·  escolabenonivio.vercel.app",
        size=18.5, color=C_ACCENT
    )

    add_rect(s10, 0.9, 3.05, 2.2, 0.04, C_ACCENT)

    add_text(s10, 0.9, 3.45, 6.0, 0.32, "EQUIPE", size=10.5, bold=True, color=C_ACCENT)
    for idx, author in enumerate(AUTHORS_RA):
        col = idx % 2
        row = idx // 2
        ax = 0.9 + col * 5.6
        ay = 3.88 + row * 0.50
        add_text(s10, ax, ay, 5.4, 0.40, author, size=16.5, color=C_WHITE)

    add_rect(s10, 0.9, 5.68, 11.5, 0.015, RGBColor(0x28, 0x42, 0x58))
    add_text(s10, 0.9, 5.92, 11.5, 0.38, PROFESSORES, size=14.5, color=C_LIGHT_MUTED)
    add_text(
        s10, 0.9, 6.32, 11.5, 0.34,
        "UNISUL — Campus Pedra Branca  ·  Análise e Desenvolvimento de Sistemas  ·  Palhoça - SC, 2026",
        size=12.5, color=C_SOFT_ON_DARK
    )

    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT_PPTX))
    print("PPTX_SAVED:", OUT_PPTX)


if __name__ == "__main__":
    build_deck()
