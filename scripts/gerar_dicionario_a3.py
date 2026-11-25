from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "01_modelagem" / "Dicionario_de_Dados_A3_FINAL.docx"
IMG_CONCEITUAL = ROOT / "01_modelagem" / "der_conceitual.png"
IMG_LOGICO_DBDIAGRAM = ROOT / "01_modelagem" / "der_logico_dbdiagram.png"

NAVY = RGBColor(0x0F, 0x25, 0x37)
BLUE = RGBColor(0x1E, 0x3A, 0x8A)
DARK = RGBColor(0x0F, 0x17, 0x2A)
MUTED = RGBColor(0x47, 0x55, 0x69)
TEAL = RGBColor(0x0F, 0x76, 0x6E)

AUTHORS = [
    ("DANIEL ALVES", "1072517730"),
    ("GABRIEL GRANDO", "10725118226"),
    ("JEFHERSON LUIZ", "10725114819"),
    ("MAICON LODETTI", "1072511629"),
]


def set_cell_shading(cell, fill_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="1E3A8A"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)


def prevent_row_split(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def repeat_header_row(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_styled_table(doc, headers, rows, col_widths_cm, font_size_pt=8.4, keep_together=None):
    n_rows = len(rows)
    if keep_together is None:
        keep_together = n_rows <= 7

    table = doc.add_table(rows=1 + n_rows, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)

    hdr_row = table.rows[0]
    repeat_header_row(hdr_row)
    prevent_row_split(hdr_row)
    for idx, text in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = Cm(col_widths_cm[idx])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(font_size_pt)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        prevent_row_split(row)
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"

        # Controle anti-quebra de linha orfa
        if keep_together:
            row_kwn = r_idx < n_rows - 1
        else:
            # Tabelas longas (8+ linhas): mantem as 3 primeiras linhas presas ao cabecalho
            # e as 2 ultimas linhas presas entre si para evitar 1 linha orfa.
            row_kwn = (r_idx < 3) or (r_idx == n_rows - 2)

        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=55, bottom=55, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.keep_with_next = row_kwn
            run = p.add_run(str(val))
            run.font.name = "Calibri"
            run.font.size = Pt(font_size_pt)
            run.font.color.rgb = DARK
            if c_idx == 0:
                run.bold = True

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(3)
    return table


def add_heading_1(doc, text, page_break_before=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0 if page_break_before else 13)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.page_break_before = page_break_before
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(14)
    run.font.color.rgb = BLUE
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="3" w:color="1E3A8A"/></w:pBdr>'))
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(11.5)
    run.font.color.rgb = TEAL
    return p


def add_body(doc, text, bold_prefix=None, space_after=5, keep_with_next=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = keep_with_next
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(10.5)
        rb.font.color.rgb = DARK
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = DARK
    return p


def add_bullet(doc, text, bold_prefix=None, keep_with_next=False):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
    p.paragraph_format.keep_with_next = keep_with_next
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(9.8)
        rb.font.color.rgb = DARK
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(9.8)
    r.font.color.rgb = DARK
    return p


def add_fitted_picture(doc, img_path: Path, max_w_in=6.3, max_h_in=7.6):
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = min(max_w_in / iw, max_h_in / ih)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(img_path), width=Inches(iw * ratio), height=Inches(ih * ratio))


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r1 = p.add_run("Avaliação A3 — Banco de Dados (UNISUL 2026)  |  Pág. ")
    r1.font.name = "Calibri"
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = MUTED
    p._p.append(parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls("w")))


def add_authors_block(doc, first_page_break=False):
    for idx, (name, ra) in enumerate(AUTHORS):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        if first_page_break and idx == 0:
            p.paragraph_format.page_break_before = True
        r_name = p.add_run(name)
        r_name.bold = True
        r_name.font.name = "Calibri"
        r_name.font.size = Pt(11.5)
        r_name.font.color.rgb = DARK
        r_ra = p.add_run(f" — RA: {ra}")
        r_ra.bold = False
        r_ra.font.name = "Calibri"
        r_ra.font.size = Pt(10.5)
        r_ra.font.color.rgb = MUTED


def build_doc():
    doc = Document()

    for sec in doc.sections:
        sec.top_margin = Cm(2.2)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.3)
        sec.right_margin = Cm(2.0)
        sec.different_first_page_header_footer = True
        add_page_number_footer(sec)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(10.5)

    # =========================================================================
    # CAPA (ABNT / UNISUL)
    # =========================================================================
    for line, sz, bld in [
        ("UNIVERSIDADE DO SUL DE SANTA CATARINA – UNISUL", 13, True),
        ("CAMPUS PEDRA BRANCA", 11, True),
        ("CURSO DE ANÁLISE E DESENVOLVIMENTO DE SISTEMAS", 11, False),
        ("UNIDADE CURRICULAR: BANCO DE DADOS", 11, False),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(line)
        r.bold = bld
        r.font.size = Pt(sz)
        r.font.color.rgb = BLUE if bld else DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(32)
    add_authors_block(doc, first_page_break=False)
    doc.add_paragraph().paragraph_format.space_after = Pt(58)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run(
        "DICIONÁRIO DE DADOS E MODELAGEM RELACIONAL:\n"
        "PORTAL ESCOLAR EEB PROF. BENONÍVIO JOÃO MARTINS"
    )
    r_title.bold = True
    r_title.font.size = Pt(15)
    r_title.font.color.rgb = BLUE

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Avaliação A3 — Banco de Dados (PostgreSQL / Supabase)")
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = MUTED

    doc.add_paragraph().paragraph_format.space_after = Pt(115)

    for loc in ["Palhoça - SC", "2026"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(loc)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK

    # =========================================================================
    # FOLHA DE ROSTO (ABNT) — page_break_before no 1o paragrafo
    # =========================================================================
    add_authors_block(doc, first_page_break=True)
    doc.add_paragraph().paragraph_format.space_after = Pt(50)

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t2 = p_t2.add_run(
        "DICIONÁRIO DE DADOS E MODELAGEM RELACIONAL:\n"
        "PORTAL ESCOLAR EEB PROF. BENONÍVIO JOÃO MARTINS"
    )
    r_t2.bold = True
    r_t2.font.size = Pt(14)
    r_t2.font.color.rgb = BLUE

    doc.add_paragraph().paragraph_format.space_after = Pt(34)

    p_note = doc.add_paragraph()
    p_note.paragraph_format.left_indent = Cm(7.5)
    p_note.paragraph_format.line_spacing = 1.15
    p_note.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_n = p_note.add_run(
        "Trabalho acadêmico apresentado à Unidade Curricular Banco de Dados (Avaliação A3), "
        "do Curso de Análise e Desenvolvimento de Sistemas da Universidade do Sul de Santa Catarina – UNISUL, "
        "Campus Pedra Branca, como atividade avaliativa.\n\n"
        "Professores: Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves"
    )
    r_n.font.size = Pt(10.5)
    r_n.font.color.rgb = DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(118)

    for loc in ["Palhoça - SC", "2026"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(loc)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK

    # =========================================================================
    # SUMÁRIO — page_break_before=True
    # =========================================================================
    add_heading_1(doc, "SUMÁRIO", page_break_before=True)
    toc_items = [
        ("1. INTRODUÇÃO", "4"),
        ("2. OBJETIVOS E EVOLUÇÃO DO MODELO", "4"),
        ("3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO (1FN, 2FN E 3FN)", "4"),
        ("4. DICIONÁRIO DE DADOS DAS 15 TABELAS", "5"),
        ("5. VIEWS PÚBLICAS", "12"),
        ("6. TIPOS ENUMERADOS (5 ENUMs)", "14"),
        ("7. RESUMO DOS RELACIONAMENTOS (13 CHAVES ESTRANGEIRAS)", "14"),
        ("8. DIAGRAMA CONCEITUAL", "15"),
        ("9. DIAGRAMA LÓGICO", "16"),
        ("10. TESTES DE INTEGRIDADE E CONSULTAS VALIDADAS", "17"),
        ("11. CONSIDERAÇÕES FINAIS E REFERÊNCIAS", "18"),
    ]
    for title_t, pg_t in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        r = p.add_run(f"{title_t}  ....................................................  {pg_t}")
        r.font.size = Pt(10.5)
        r.bold = True
        r.font.color.rgb = DARK

    # =========================================================================
    # 1. INTRODUÇÃO & 2. OBJETIVOS — page_break_before=True
    # =========================================================================
    add_heading_1(doc, "1. INTRODUÇÃO", page_break_before=True)
    add_body(
        doc,
        "Este documento apresenta a modelagem relacional e o dicionário de dados do Portal Escolar da Escola de Educação Básica "
        "Professor Benonívio João Martins (Palhoça – SC). O portal é um sistema real já publicado em produção "
        "(https://escolabenonivio.vercel.app/), com código-fonte aberto disponível no repositório "
        "https://github.com/jefheee/escola-benonivio, desenvolvido em Next.js com banco de dados PostgreSQL na plataforma Supabase."
    )
    add_body(
        doc,
        "A aplicação centraliza a comunicação da escola com alunos, pais e professores: avisos oficiais, galerias de fotos, "
        "acervo histórico, documentos para download, páginas institucionais, turmas por ano letivo, grupos de WhatsApp, "
        "postagens pedagógicas, calendário de eventos e cardápio da alimentação escolar."
    )

    add_heading_1(doc, "2. OBJETIVOS E EVOLUÇÃO DO MODELO")
    add_heading_2(doc, "2.1. Objetivo Geral")
    add_body(
        doc,
        "Reconstruir e documentar o banco de dados do portal de forma estruturada e normalizada (1FN, 2FN e 3FN), garantindo "
        "a integridade das informações, controle adequado de permissões e preservação do histórico escolar de um ano letivo para o outro."
    )
    add_heading_2(doc, "2.2. Objetivos Específicos")
    for item in [
        "Especificar todas as 15 tabelas, suas colunas, tipos de dados, obrigatoriedade, tamanhos e valores padrão.",
        "Documentar chaves primárias, chaves estrangeiras com regras de exclusão, chaves únicas, validações e índices.",
        "Apresentar as 2 Views públicas, os 5 tipos enumerados (ENUMs) e os 13 relacionamentos entre tabelas.",
        "Comprovar o funcionamento do modelo com testes de validação e consultas reais executadas no PostgreSQL.",
    ]:
        add_bullet(doc, item)

    add_heading_2(doc, "2.3. Evolução do Projeto Real (Antes vs. Depois)")
    add_body(
        doc,
        "Na primeira versão colocada no ar, o banco contava com 9 tabelas e guardava listas de fotos e links dentro de campos JSONB. "
        "Além disso, as turmas não separavam o ano letivo (o que fazia os dados serem sobrescritos na virada do ano), o turno era "
        "repetido nos grupos de WhatsApp e faltavam validações diretamente no banco."
    )
    add_body(
        doc,
        "Na reconstrução feita para a Avaliação A3, o modelo passou a ter 15 tabelas normalizadas até a 3FN, 5 tipos ENUM para "
        "padronizar valores permitidos, 2 Views públicas para filtrar automaticamente o que pode ser exibido no site e controle de "
        "acesso por perfil (visitantes visualizam apenas conteúdos publicados e ativos, enquanto editores e administradores gerenciam os cadastros)."
    )

    # =========================================================================
    # 3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO
    # =========================================================================
    add_heading_1(doc, "3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO (1FN, 2FN E 3FN)")
    regras = [
        ("1FN (Eliminação de listas em JSONB): ", "Listas de fotos e links foram separadas em tabelas próprias ligadas por chave estrangeira e ordenadas (escola_avisos_imagens, escola_acervo_imagens e escola_turmas_links)."),
        ("2FN (Resolução de muitos-para-muitos): ", "A relação N:N entre Eventos e Turmas foi resolvida com a tabela intermediária escola_turmas_eventos usando chave primária composta (evento_id, turma_id)."),
        ("3FN (Eliminação de dado repetido): ", "O campo turno foi removido de escola_whatsapp_grupos, ficando apenas em escola_turmas e sendo obtido por JOIN sempre que necessário."),
        ("Histórico por Ano Letivo: ", "A tabela escola_turmas possui o campo ano_letivo e chave única combinada (ano_letivo, ano, nome, turno), permitindo manter turmas de 2025, 2026 e próximos anos sem perda de histórico."),
        ("Um Grupo de WhatsApp por Turma (1:1): ", "A restrição UNIQUE em escola_whatsapp_grupos(turma_id) garante no máximo um grupo oficial por turma."),
        ("Cardápio Único por Dia e Turno: ", "A restrição UNIQUE (data, turno) em escola_refeicoes impede o cadastro de dois cardápios diferentes para a mesma data e período."),
        ("Preservação da Autoria: ", "As 6 chaves estrangeiras de autor_id usam ON DELETE SET NULL para que avisos, documentos e eventos continuem no portal caso o cadastro de um operador seja removido."),
        ("Controle de Acesso e Views Públicas: ", "Todas as tabelas possuem controle de acesso por perfil (visitantes só consultam registros publicados e vigentes) e as 2 Views públicas filtram rascunhos e itens expirados automaticamente."),
    ]
    for bp, txt in regras:
        add_bullet(doc, txt, bold_prefix=bp)

    # =========================================================================
    # 4. DICIONÁRIO DE DADOS DAS 15 TABELAS
    # =========================================================================
    add_heading_1(doc, "4. DICIONÁRIO DE DADOS DAS 15 TABELAS")
    add_body(
        doc,
        "Legenda da coluna Observação: PK = Chave Primária; FK = Chave Estrangeira; NN = Obrigatório (NOT NULL); Null = Opcional; "
        "UQ = Único (UNIQUE); UQ Comp. = Único Composto; UTC = Data/hora padrão preenchida automaticamente em UTC."
    )

    col_w = [2.8, 2.3, 2.5, 1.3, 5.2, 2.4]
    hdr_cols = ["Nome", "Tipo", "Classe", "Tam.", "Descrição", "Observação"]

    tables_spec = [
        (
            "4.1. Tabela escola_usuarios",
            "Operadores, professores e administradores com acesso ao painel administrativo do portal.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do usuário (gerado automaticamente)", "PK / NN"],
                ["nome", "Texto", "Simples", "Var.", "Nome completo do usuário/operador", "NN"],
                ["email", "Texto", "Determinante", "Var.", "E-mail institucional único em letras minúsculas", "NN / UQ"],
                ["role", "Enum", "Simples", "4 B", "Perfil de permissão (usuario_role_enum; padrão 'editor')", "NN"],
                ["ativo", "Boolean", "Simples", "1 B", "Indica se o cadastro está ativo (padrão true)", "NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização cadastral", "NN / UTC"],
            ],
            [
                "PK: escola_usuarios_pkey (id). Na base de homologação o identificador é gerado automaticamente para testes independentes; em produção integra-se ao cadastro de autenticação do portal.",
                "UNIQUE: escola_usuarios_email_key (email).",
                "CHECK: nome não vazio; e-mail em formato válido e letras minúsculas (ck_escola_usuarios_email_valido).",
                "Trigger: atualização automática de updated_at em alterações (trg_escola_usuarios_updated_at).",
            ],
        ),
        (
            "4.2. Tabela escola_avisos",
            "Comunicados, informes gerais e notícias publicadas no mural oficial da escola.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do aviso", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título principal do aviso", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Síntese exibida nos cartões de listagem", "NN"],
                ["conteudo", "Texto", "Simples", "Var.", "Texto completo do comunicado", "Null"],
                ["categoria", "Texto", "Simples", "Var.", "Classificação temática (ex.: Matrículas, Geral)", "NN"],
                ["imagem_url", "Texto", "Simples", "Var.", "Endereço da imagem principal de capa", "Null"],
                ["importancia", "Enum", "Simples", "4 B", "Prioridade (importancia_enum; padrão 'normal')", "NN"],
                ["destaque_home", "Boolean", "Simples", "1 B", "Exibe no destaque da página inicial (padrão false)", "NN"],
                ["status", "Enum", "Simples", "4 B", "Situação editorial (publicacao_status_enum; padrão 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Início da exibição pública", "NN / UTC"],
                ["data_expiracao", "Data/Hora", "Simples", "8 B", "Data limite de exibição no mural", "Null"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última modificação", "NN / UTC"],
            ],
            [
                "PK: escola_avisos_pkey (id).",
                "FK: escola_avisos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: textos não vazios; ck_avisos_datas garante data_expiracao posterior à data_publicacao.",
                "Índices: autor_id e consulta pública por (status, data_publicacao DESC). Trigger: updated_at.",
            ],
        ),
        (
            "4.3. Tabela escola_avisos_imagens",
            "Fotografias individuais da galeria de cada aviso (separadas em tabela própria pela 1FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da imagem", "PK / NN"],
                ["aviso_id", "UUID", "Determinante", "16 B", "Referência ao aviso pai em escola_avisos", "FK / NN / UQ Comp."],
                ["url", "Texto", "Simples", "Var.", "Endereço público da imagem", "NN"],
                ["legenda", "Texto", "Simples", "Var.", "Descrição ou crédito da fotografia", "Null"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Posição na galeria (padrão 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de envio em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_avisos_imagens_pkey (id).",
                "FK: escola_avisos_imagens_aviso_id_fkey (aviso_id) → escola_avisos(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_avisos_imagens_aviso_ordem (aviso_id, ordem).",
                "CHECK: url não vazia; legenda não vazia quando informada; ordem >= 0.",
            ],
        ),
        (
            "4.4. Tabela escola_acervo",
            "Projetos históricos, edições da Revista Okaza, Grupo Butterfly e memórias escolares.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do item", "PK / NN"],
                ["ano", "Texto", "Simples", "Var.", "Ano cronológico de referência", "NN"],
                ["categoria", "Texto", "Simples", "Var.", "Categoria do acervo (ex.: Revista Okaza, Projetos)", "NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título descritivo do registro", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Relato histórico detalhado", "Null"],
                ["capa_url", "Texto", "Simples", "Var.", "Endereço da foto de capa do álbum", "Null"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; padrão 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Data/hora de publicação no portal", "NN / UTC"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_acervo_pkey (id).",
                "FK: escola_acervo_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: ano, categoria e titulo não vazios; descricao e capa_url não vazios quando informados.",
                "Índices: autor_id e listagem por (status, ano DESC). Trigger: updated_at.",
            ],
        ),
        (
            "4.5. Tabela escola_acervo_imagens",
            "Fotografias individuais dos álbuns do acervo histórico (1FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da foto", "PK / NN"],
                ["acervo_id", "UUID", "Determinante", "16 B", "Referência ao álbum em escola_acervo", "FK / NN / UQ Comp."],
                ["url", "Texto", "Simples", "Var.", "Endereço público da imagem", "NN"],
                ["legenda", "Texto", "Simples", "Var.", "Legenda histórica da fotografia", "Null"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Sequência no álbum (padrão 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de inclusão em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_acervo_imagens_pkey (id).",
                "FK: escola_acervo_imagens_acervo_id_fkey (acervo_id) → escola_acervo(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_acervo_imagens_acervo_ordem (acervo_id, ordem).",
                "CHECK: url não vazia; legenda não vazia quando informada; ordem >= 0.",
            ],
        ),
        (
            "4.6. Tabela escola_documentos",
            "Repositório de arquivos oficiais para download público (calendários, PPP, editais e atas).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do documento", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título público para listagem", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Explicação complementar sobre o arquivo", "Null"],
                ["categoria", "Texto", "Simples", "Var.", "Classificação documental (Calendários, Editais, Atas)", "NN"],
                ["url_arquivo", "Texto", "Simples", "Var.", "Link direto para download do arquivo", "NN"],
                ["nome_arquivo", "Texto", "Simples", "Var.", "Nome original do arquivo físico", "NN"],
                ["mime_type", "Texto", "Simples", "Var.", "Tipo do arquivo (ex.: application/pdf)", "NN"],
                ["tamanho_bytes", "Número (Int8)", "Simples", "8 B", "Tamanho do arquivo em bytes (>= 0)", "NN"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; padrão 'publicado')", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de upload em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização", "NN / UTC"],
            ],
            [
                "PK: escola_documentos_pkey (id).",
                "FK: escola_documentos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: campos de texto não vazios e tamanho_bytes >= 0.",
                "Índices: autor_id e listagem por (categoria, status). Trigger: updated_at.",
            ],
        ),
        (
            "4.7. Tabela escola_conteudo_paginas",
            "Conteúdo editável das páginas institucionais fixas do portal (Sobre, APP, Projetos).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da página", "PK / NN"],
                ["slug", "Texto", "Determinante", "Var.", "Identificador único de endereço (letras minúsculas e hífen)", "NN / UQ"],
                ["titulo", "Texto", "Simples", "Var.", "Título exibido no topo da página", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Descrição curta da página", "Null"],
                ["conteudo_html", "Texto", "Simples", "Var.", "Corpo estruturado em HTML/Texto", "Null"],
                ["imagem_url", "Texto", "Simples", "Var.", "Endereço do banner principal da página", "Null"],
                ["publicado", "Boolean", "Simples", "1 B", "Define visibilidade pública (padrão true)", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador editor em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última edição", "NN / UTC"],
            ],
            [
                "PK: escola_conteudo_paginas_pkey (id).",
                "FK: escola_conteudo_paginas_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "UNIQUE: escola_conteudo_paginas_slug_key (slug).",
                "CHECK: formato válido de slug (apenas letras minúsculas, números e hífen) e textos não vazios.",
                "Índices: autor_id e busca pública por (publicado, slug). Trigger: updated_at.",
            ],
        ),
        (
            "4.8. Tabela escola_turmas",
            "Turmas regulares da escola organizadas por ano letivo, série e turno (3FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da turma", "PK / NN"],
                ["ano_letivo", "Número (Int4)", "Determinante", "4 B", "Ano letivo de vigência (padrão 2026; >= 2000)", "NN / UQ Comp."],
                ["ano", "Texto", "Determinante", "Var.", "Série ou etapa de ensino (ex.: 1º Ano Ensino Médio)", "NN / UQ Comp."],
                ["nome", "Texto", "Determinante", "Var.", "Código identificador da turma (ex.: 101, 201, 901)", "NN / UQ Comp."],
                ["turno", "Enum", "Determinante", "4 B", "Período das aulas (turno_enum)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de abertura em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última modificação", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_pkey (id).",
                "UNIQUE: uq_turmas_ano_letivo_serie_nome_turno (ano_letivo, ano, nome, turno).",
                "CHECK: ano_letivo >= 2000; ano e nome não vazios.",
                "Trigger: atualização automática de updated_at.",
            ],
        ),
        (
            "4.9. Tabela escola_turmas_links",
            "Links externos de apoio de cada turma (Classroom, Drive e materiais extras) em 1FN.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do link", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "FK / NN / UQ Comp."],
                ["titulo", "Texto", "Simples", "Var.", "Rótulo do link complementar", "NN"],
                ["url", "Texto", "Simples", "Var.", "Endereço web completo", "NN"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Ordem de exibição (padrão 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de cadastro em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_links_pkey (id).",
                "FK: escola_turmas_links_turma_id_fkey (turma_id) → escola_turmas(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_turmas_links_turma_ordem (turma_id, ordem).",
                "CHECK: titulo e url não vazios; ordem >= 0.",
            ],
        ),
        (
            "4.10. Tabela escola_whatsapp_grupos",
            "Links de convite dos grupos oficiais de WhatsApp por turma (relação 1:1 em 3FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do grupo", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência única (1:1) para escola_turmas", "FK / NN / UQ"],
                ["nome", "Texto", "Simples", "Var.", "Nome de exibição do grupo oficial", "NN"],
                ["link_convite", "Texto", "Simples", "Var.", "Endereço de convite do grupo no WhatsApp", "NN"],
                ["ativo", "Boolean", "Simples", "1 B", "Indica se o convite está ativo (padrão true)", "NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização", "NN / UTC"],
            ],
            [
                "PK: escola_whatsapp_grupos_pkey (id).",
                "FK: escola_whatsapp_grupos_turma_id_fkey (turma_id) → escola_turmas(id) ON DELETE CASCADE.",
                "UNIQUE: escola_whatsapp_grupos_turma_id_key (turma_id) — garante no máximo 1 grupo por turma.",
                "CHECK: nome e link_convite não vazios. Trigger: updated_at.",
            ],
        ),
        (
            "4.11. Tabela escola_turmas_posts",
            "Comunicados, materiais de aula e avisos de provas no mural de cada turma.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da postagem", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "FK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Assunto ou título da atividade", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Breve descrição apresentada na listagem", "Null"],
                ["conteudo", "Texto", "Simples", "Var.", "Orientações completas da atividade", "Null"],
                ["imagem_url", "Texto", "Simples", "Var.", "Endereço de imagem ilustrativa", "Null"],
                ["link_referencia", "Texto", "Simples", "Var.", "Link externo complementar", "Null"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; padrão 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Liberação pública do post", "NN / UTC"],
                ["data_expiracao", "Data/Hora", "Simples", "8 B", "Data limite de exibição", "Null"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador autor em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última edição", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_posts_pkey (id).",
                "FKs: turma_id → escola_turmas(id) ON DELETE CASCADE; autor_id → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: campos textuais não vazios; data_expiracao posterior à data_publicacao.",
                "Índices: autor_id e listagem por (turma_id, status, data_publicacao DESC). Trigger: updated_at.",
            ],
        ),
        (
            "4.12. Tabela escola_eventos",
            "Programação do calendário escolar (feiras científicas, reuniões e eventos culturais).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do evento", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Nome oficial do evento", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Detalhamento do cronograma e objetivos", "Null"],
                ["local", "Texto", "Simples", "Var.", "Espaço físico de realização", "Null"],
                ["data_inicio", "Data/Hora", "Simples", "8 B", "Data e horário de início", "NN"],
                ["data_fim", "Data/Hora", "Simples", "8 B", "Data e horário de término (>= data_inicio)", "Null"],
                ["dia_inteiro", "Boolean", "Simples", "1 B", "Evento de dia inteiro (padrão false)", "NN"],
                ["imagem_url", "Texto", "Simples", "Var.", "Endereço do cartaz de divulgação", "Null"],
                ["status", "Enum", "Simples", "4 B", "Situação operacional (status_enum; padrão 'ativo')", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador organizador em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_eventos_pkey (id).",
                "FK: escola_eventos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: campos de texto não vazios; ck_eventos_datas garante data_fim >= data_inicio.",
                "Índices: autor_id, datas e consulta por (status, data_inicio). Trigger: updated_at.",
            ],
        ),
        (
            "4.13. Tabela escola_turmas_eventos",
            "Tabela intermediária que resolve o relacionamento muitos-para-muitos (N:N) entre Eventos e Turmas.",
            [
                ["evento_id", "UUID", "Determinante", "16 B", "Referência ao evento em escola_eventos", "PK Comp. / FK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "PK Comp. / FK / NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora do vínculo em UTC", "NN / UTC"],
            ],
            [
                "PK Composta: escola_turmas_eventos_pkey (evento_id, turma_id).",
                "FKs: evento_id → escola_eventos(id) ON DELETE CASCADE; turma_id → escola_turmas(id) ON DELETE CASCADE.",
                "Índice auxiliar em turma_id para acelerar consultas a partir da turma.",
            ],
        ),
        (
            "4.14. Tabela escola_refeicoes",
            "Cardápio diário da alimentação escolar por data e turno.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do registro", "PK / NN"],
                ["data", "Data", "Determinante", "4 B", "Data em que a refeição será servida", "NN / UQ Comp."],
                ["turno", "Enum", "Determinante", "4 B", "Turno da merenda (turno_enum)", "NN / UQ Comp."],
                ["descricao", "Texto", "Simples", "Var.", "Alimentos que compõem o prato do dia", "NN"],
                ["observacoes", "Texto", "Simples", "Var.", "Avisos sobre alérgenos ou restrições", "Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de lançamento em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização", "NN / UTC"],
            ],
            [
                "PK: escola_refeicoes_pkey (id).",
                "UNIQUE Composta: uq_refeicoes_data_turno (data, turno).",
                "CHECK: descricao não vazia; observacoes não vazia quando informada. Trigger: updated_at.",
            ],
        ),
        (
            "4.15. Tabela escola_notificacoes",
            "Alertas globais e comunicados urgentes exibidos no topo do portal.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do alerta", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título curto de chamada", "NN"],
                ["mensagem", "Texto", "Simples", "Var.", "Texto explicativo do alerta", "NN"],
                ["importancia", "Enum", "Simples", "4 B", "Criticidade (importancia_enum; padrão 'normal')", "NN"],
                ["ativa", "Boolean", "Simples", "1 B", "Define se o alerta está habilitado (padrão true)", "NN"],
                ["data_inicio", "Data/Hora", "Simples", "8 B", "Início da exibição automática", "NN / UTC"],
                ["data_fim", "Data/Hora", "Simples", "8 B", "Fim da exibição (>= data_inicio)", "Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_notificacoes_pkey (id).",
                "CHECK: titulo e mensagem não vazios; data_fim >= data_inicio.",
                "Índice para alertas ativos por vigência. Trigger: updated_at.",
            ],
        ),
    ]

    for title, desc, rows, notes in tables_spec:
        add_heading_2(doc, title)
        add_body(doc, desc, bold_prefix="Finalidade: ", space_after=4, keep_with_next=True)
        add_styled_table(doc, hdr_cols, rows, col_w, font_size_pt=8.3)
        p_rl = doc.add_paragraph()
        p_rl.paragraph_format.space_before = Pt(0)
        p_rl.paragraph_format.space_after = Pt(2)
        p_rl.paragraph_format.keep_with_next = True
        r_rl = p_rl.add_run("Restrições e Relacionamentos:")
        r_rl.bold = True
        r_rl.font.size = Pt(9.8)
        r_rl.font.color.rgb = BLUE
        for idx_n, n in enumerate(notes):
            add_bullet(doc, n, keep_with_next=(idx_n == 0 and len(notes) > 1))

    # =========================================================================
    # 5. VIEWS PÚBLICAS
    # =========================================================================
    add_heading_1(doc, "5. VIEWS PÚBLICAS")
    add_body(
        doc,
        "As duas Views públicas facilitam as consultas feitas pelo site, aplicando diretamente no banco o filtro que oculta "
        "rascunhos, itens arquivados, inativos ou com prazo de exibição expirado, respeitando as permissões do usuário logado ou visitante."
    )

    add_heading_2(doc, "5.1. View escola_avisos_publicos")
    add_body(
        doc,
        "Retorna apenas avisos com status 'publicado', cuja data de publicação já iniciou e que ainda não expiraram.",
        bold_prefix="Regra de filtro: ",
        space_after=4,
        keep_with_next=True,
    )
    add_styled_table(
        doc,
        ["Coluna", "Tipo", "Descrição"],
        [
            ["id", "uuid", "Identificador único do aviso"],
            ["titulo", "text", "Título principal do aviso"],
            ["resumo", "text", "Síntese exibida nos cartões"],
            ["conteudo", "text", "Texto completo do comunicado"],
            ["categoria", "text", "Classificação temática"],
            ["imagem_url", "text", "Endereço da imagem principal"],
            ["importancia", "importancia_enum", "Prioridade editorial (normal, importante, urgente)"],
            ["destaque_home", "boolean", "Sinaliza exibição no destaque da home"],
            ["data_publicacao", "timestamptz", "Início da exibição pública"],
            ["data_expiracao", "timestamptz", "Limite de vigência"],
        ],
        [4.0, 4.0, 8.5],
        font_size_pt=8.8,
        keep_together=False,
    )

    add_heading_2(doc, "5.2. View escola_eventos_publicos")
    add_body(
        doc,
        "Retorna apenas os eventos do calendário escolar com status 'ativo'.",
        bold_prefix="Regra de filtro: ",
        space_after=4,
        keep_with_next=True,
    )
    add_styled_table(
        doc,
        ["Coluna", "Tipo", "Descrição"],
        [
            ["id", "uuid", "Identificador único do evento"],
            ["titulo", "text", "Nome oficial do evento"],
            ["descricao", "text", "Detalhamento do cronograma"],
            ["local", "text", "Espaço físico de realização"],
            ["data_inicio", "timestamptz", "Data e hora de início"],
            ["data_fim", "timestamptz", "Data e hora de encerramento"],
            ["dia_inteiro", "boolean", "Indica duração de dia inteiro"],
            ["imagem_url", "text", "Endereço do cartaz de divulgação"],
        ],
        [4.0, 4.0, 8.5],
        font_size_pt=8.8,
        keep_together=True,
    )

    # =========================================================================
    # 6. TIPOS ENUMERADOS (5 ENUMs)
    # =========================================================================
    add_heading_1(doc, "6. TIPOS ENUMERADOS (5 ENUMs)")
    add_body(
        doc,
        "Os tipos ENUM garantem que campos de domínio fechado aceitem somente valores padronizados, evitando erros de digitação:",
        keep_with_next=True,
    )
    add_styled_table(
        doc,
        ["Tipo ENUM (public)", "Valores Permitidos", "Tabelas que Utilizam"],
        [
            ["importancia_enum", "normal, importante, urgente", "escola_avisos, escola_notificacoes"],
            ["publicacao_status_enum", "rascunho, publicado, arquivado", "escola_avisos, escola_acervo, escola_documentos, escola_turmas_posts"],
            ["status_enum", "ativo, inativo, expirado", "escola_eventos"],
            ["turno_enum", "matutino, vespertino, noturno, integral", "escola_turmas, escola_refeicoes"],
            ["usuario_role_enum", "admin, editor", "escola_usuarios"],
        ],
        [4.8, 5.5, 6.2],
        font_size_pt=8.8,
        keep_together=True,
    )

    # =========================================================================
    # 7. RESUMO DOS RELACIONAMENTOS (13 FKs)
    # =========================================================================
    add_heading_1(doc, "7. RESUMO DOS RELACIONAMENTOS (13 CHAVES ESTRANGEIRAS)")
    add_body(
        doc,
        "A tabela abaixo resume todas as ligações entre tabelas, indicando a tabela de origem da chave estrangeira, a tabela de destino, a cardinalidade e o comportamento em caso de exclusão:",
        keep_with_next=True,
    )
    add_styled_table(
        doc,
        ["Tabela Origem", "Tabela Destino", "Coluna (FK)", "Cardinalidade", "Política ON DELETE"],
        [
            ["escola_avisos", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_acervo", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_documentos", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_conteudo_paginas", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_turmas_posts", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_eventos", "escola_usuarios", "autor_id → id", "N:0..1 (Opcional)", "SET NULL"],
            ["escola_avisos_imagens", "escola_avisos", "aviso_id → id", "N:1 (Composição)", "CASCADE"],
            ["escola_acervo_imagens", "escola_acervo", "acervo_id → id", "N:1 (Composição)", "CASCADE"],
            ["escola_turmas_links", "escola_turmas", "turma_id → id", "N:1 (Composição)", "CASCADE"],
            ["escola_turmas_posts", "escola_turmas", "turma_id → id", "N:1 (Composição)", "CASCADE"],
            ["escola_whatsapp_grupos", "escola_turmas", "turma_id → id", "1:1 (UNIQUE)", "CASCADE"],
            ["escola_turmas_eventos", "escola_eventos", "evento_id → id", "N:1 (Associativa N:N)", "CASCADE"],
            ["escola_turmas_eventos", "escola_turmas", "turma_id → id", "N:1 (Associativa N:N)", "CASCADE"],
        ],
        [4.2, 3.6, 3.0, 3.3, 2.4],
        font_size_pt=8.6,
        keep_together=True,
    )

    # =========================================================================
    # 8. DIAGRAMA CONCEITUAL — page_break_before=True
    # =========================================================================
    add_heading_1(doc, "8. DIAGRAMA CONCEITUAL", page_break_before=True)
    add_body(
        doc,
        "Visão conceitual das entidades do domínio escolar, seus atributos principais de negócio e as cardinalidades entre elas (1:1, 1:N, 0..1:N e N:N).",
        keep_with_next=True,
    )
    if IMG_CONCEITUAL.exists():
        add_fitted_picture(doc, IMG_CONCEITUAL, max_w_in=6.3, max_h_in=7.6)
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc1 = p_cap1.add_run("Figura 1 — Diagrama Entidade-Relacionamento Conceitual.")
        rc1.italic = True
        rc1.font.size = Pt(9.2)
        rc1.font.color.rgb = MUTED

    # =========================================================================
    # 9. DIAGRAMA LÓGICO — page_break_before=True
    # =========================================================================
    add_heading_1(doc, "9. DIAGRAMA LÓGICO", page_break_before=True)
    add_body(
        doc,
        "Representação lógica completa das 15 tabelas relacionais, exibindo chaves primárias, chaves estrangeiras, chaves únicas, tipos de dados, ENUMs e cardinalidades.",
        keep_with_next=True,
    )
    if IMG_LOGICO_DBDIAGRAM.exists():
        add_fitted_picture(doc, IMG_LOGICO_DBDIAGRAM, max_w_in=6.4, max_h_in=7.8)
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc2 = p_cap2.add_run("Figura 2 — Diagrama Entidade-Relacionamento Lógico.")
        rc2.italic = True
        rc2.font.size = Pt(9.2)
        rc2.font.color.rgb = MUTED

    # =========================================================================
    # 10. TESTES DE INTEGRIDADE E CONSULTAS VALIDADAS — page_break_before=True
    # =========================================================================
    add_heading_1(doc, "10. TESTES DE INTEGRIDADE E CONSULTAS VALIDADAS", page_break_before=True)
    add_body(
        doc,
        "O banco foi criado do zero no PostgreSQL (Supabase), populado com 102 registros realistas distribuídos entre os anos "
        "letivos de 2025 e 2026 e submetido a testes de integridade e consultas de demonstração."
    )

    add_heading_2(doc, "10.1. Resumo da Massa de Dados Populada (102 Registros)")
    add_styled_table(
        doc,
        ["Tabela", "Qtd", "Tabela", "Qtd", "Tabela", "Qtd"],
        [
            ["escola_usuarios", "4", "escola_avisos", "6", "escola_conteudo_paginas", "4"],
            ["escola_turmas", "6", "escola_avisos_imagens", "10", "escola_eventos", "5"],
            ["escola_whatsapp_grupos", "5", "escola_acervo", "4", "escola_turmas_eventos", "11"],
            ["escola_turmas_links", "11", "escola_acervo_imagens", "8", "escola_refeicoes", "10"],
            ["escola_turmas_posts", "9", "escola_documentos", "6", "escola_notificacoes", "3"],
        ],
        [4.2, 1.3, 4.2, 1.3, 4.2, 1.3],
        font_size_pt=8.7,
        keep_together=True,
    )

    add_heading_2(doc, "10.2. Testes de Validação de Integridade no PostgreSQL")
    add_body(
        doc,
        "Foram simulados erros propositais para comprovar que o próprio banco de dados impede dados inconsistentes:",
        keep_with_next=True,
    )
    add_styled_table(
        doc,
        ["Teste", "Cenário Inválido Simulado", "Resultado no Banco"],
        [
            ["T1", "Cadastrar turma duplicada no mesmo ano letivo, série e turno", "Bloqueado por chave única (uq_turmas_ano_letivo_serie_nome_turno)"],
            ["T2", "Cadastrar dois cardápios para a mesma data e turno", "Bloqueado por chave única (uq_refeicoes_data_turno)"],
            ["T3", "Vincular um segundo grupo de WhatsApp à mesma turma", "Bloqueado por chave única 1:1 (escola_whatsapp_grupos_turma_id_key)"],
            ["T4", "Cadastrar evento com data de término anterior ao início", "Bloqueado por regra CHECK de datas (ck_eventos_datas)"],
            ["T5", "Inserir e-mail inválido, nome em branco ou slug fora do padrão", "Bloqueado por regras CHECK de validação de texto e formato"],
            ["T6", "Publicar post vinculado a uma turma inexistente", "Bloqueado por integridade referencial (chave estrangeira turma_id)"],
        ],
        [1.4, 7.6, 7.5],
        font_size_pt=8.5,
        keep_together=True,
    )

    add_heading_2(doc, "10.3. Consultas SQL Validadas")
    for q in [
        "Consulta 1 (JOIN em 3FN): Listou as turmas de 2026 com grupo de WhatsApp ativo e contagem de links complementares (101: 3; 201: 2; 301: 3).",
        "Consulta 2 (COUNT, SUM e AVG): Agrupou os 6 documentos por categoria, exibindo total em MB e média de tamanho por categoria.",
        "Consulta 3 (MIN, MAX e relação N:N): Exibiu o período dos eventos ativos e quantas turmas participam de cada evento via tabela associativa.",
        "Consulta 4 (GROUP BY com HAVING): Filtrou apenas as 4 turmas que possuem 2 ou mais links complementares.",
        "Consulta 5 (LEFT JOIN com COALESCE): Listou todas as 6 turmas com a quantidade de posts publicados, mantendo zeros sem ocultar turmas.",
        "Consulta 6 (NOT EXISTS): Identificou automaticamente a turma 901 de 2026 que ainda não possui grupo de WhatsApp cadastrado.",
        "Consulta 7 (Histórico 2025 vs. 2026): Comparou a evolução entre os dois anos letivos (2 turmas e 3 posts em 2025; 4 turmas e 6 posts em 2026).",
        "Consulta 8 (Views Públicas): Confirmou que escola_avisos_publicos retornou 4 de 6 avisos e escola_eventos_publicos retornou 3 de 5 eventos, filtrando rascunhos e itens vencidos.",
    ]:
        add_bullet(doc, q)

    # =========================================================================
    # 11. CONSIDERAÇÕES FINAIS E REFERÊNCIAS
    # =========================================================================
    add_heading_1(doc, "11. CONSIDERAÇÕES FINAIS")
    add_body(
        doc,
        "A reconstrução do banco de dados do Portal Escolar da EEB Professor Benonívio João Martins permitiu transformar "
        "uma base inicial com listas em JSON em um modelo relacional completo, normalizado até a 3FN e preparado para acompanhar "
        "a escola ao longo de vários anos letivos. As regras de integridade, os tipos enumerados, o controle de acesso por perfil "
        "e as Views públicas trazem mais segurança, organização e facilidade de manutenção para o projeto real."
    )

    add_heading_1(doc, "REFERÊNCIAS")
    refs = [
        "DATE, Christopher J. Introdução a sistemas de bancos de dados. 8. ed. Rio de Janeiro: Elsevier, 2004.",
        "ELMASRI, Ramez; NAVATHE, Shamkant B. Sistemas de banco de dados. 7. ed. São Paulo: Pearson, 2019.",
        "PORTAL ESCOLAR EEB PROF. BENONÍVIO JOÃO MARTINS. Aplicação em produção. Disponível em: https://escolabenonivio.vercel.app/. Acesso em: 24 nov. 2026.",
        "POSTGRESQL GLOBAL DEVELOPMENT GROUP. PostgreSQL 17 Documentation. Disponível em: https://www.postgresql.org/docs/17/. Acesso em: 24 nov. 2026.",
        "SILBERSCHATZ, Abraham; KORTH, Henry F.; SUDARSHAN, S. Sistema de banco de dados. 7. ed. Rio de Janeiro: GEN LTC, 2020.",
        "SUPABASE. Supabase Documentation: Row Level Security and Database Functions. Disponível em: https://supabase.com/docs. Acesso em: 24 nov. 2026.",
    ]
    for rf in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(rf)
        r.font.size = Pt(10)
        r.font.color.rgb = DARK

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_PATH))
    print("DOCX_SAVED:", OUT_PATH)


if __name__ == "__main__":
    build_doc()
