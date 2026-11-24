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
IMG_LOGICO_MERMAID = ROOT / "01_modelagem" / "der_logico.png"

NAVY = RGBColor(0x1E, 0x3A, 0x8A)
DARK = RGBColor(0x0F, 0x17, 0x2A)
MUTED = RGBColor(0x47, 0x55, 0x69)
TEAL = RGBColor(0x0F, 0x76, 0x6E)


def set_cell_shading(cell, fill_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=65, bottom=65, left=85, right=85):
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


def add_styled_table(doc, headers, rows, col_widths_cm, font_size_pt=8.4):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
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
        set_cell_margins(cell, top=85, bottom=85, left=85, right=85)
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
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=85, right=85)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
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


def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(14)
    run.font.color.rgb = NAVY
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="3" w:color="1E3A8A"/></w:pBdr>'))
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(11.8)
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


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
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


def add_fitted_picture(doc, img_path: Path, max_w_in=6.2, max_h_in=7.3):
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = min(max_w_in / iw, max_h_in / ih)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
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
        r.font.color.rgb = NAVY if bld else DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(36)

    for author in ["DANIEL ALVES", "GABRIEL GRANDO", "JEFHERSON LUIZ", "MAICON LODETTI"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(author)
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(64)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run(
        "DICIONÁRIO DE DADOS E MODELAGEM RELACIONAL:\n"
        "SISTEMA DE PORTAL ESCOLAR EEB PROF. BENONÍVIO JOÃO MARTINS"
    )
    r_title.bold = True
    r_title.font.size = Pt(15)
    r_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Avaliação A3 — Banco de Dados (PostgreSQL 17 / Supabase)")
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = MUTED

    doc.add_paragraph().paragraph_format.space_after = Pt(120)

    for loc in ["Palhoça – SC", "2026"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(loc)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK

    doc.add_page_break()

    # =========================================================================
    # FOLHA DE ROSTO (ABNT)
    # =========================================================================
    for author in ["DANIEL ALVES", "GABRIEL GRANDO", "JEFHERSON LUIZ", "MAICON LODETTI"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(author)
        r.bold = True
        r.font.size = Pt(12)

    doc.add_paragraph().paragraph_format.space_after = Pt(54)

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t2 = p_t2.add_run(
        "DICIONÁRIO DE DADOS E MODELAGEM RELACIONAL:\n"
        "SISTEMA DE PORTAL ESCOLAR EEB PROF. BENONÍVIO JOÃO MARTINS"
    )
    r_t2.bold = True
    r_t2.font.size = Pt(14)
    r_t2.font.color.rgb = NAVY

    doc.add_paragraph().paragraph_format.space_after = Pt(36)

    p_note = doc.add_paragraph()
    p_note.paragraph_format.left_indent = Cm(7.5)
    p_note.paragraph_format.line_spacing = 1.15
    p_note.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_n = p_note.add_run(
        "Trabalho acadêmico apresentado à Unidade Curricular Banco de Dados (Avaliação A3), "
        "do Curso de Análise e Desenvolvimento de Sistemas da Universidade do Sul de Santa Catarina – UNISUL, "
        "Campus Pedra Branca, como atividade avaliativa.\n\n"
        "Professores: Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves"
    )
    r_n.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(125)

    for loc in ["Palhoça – SC", "2026"]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(loc)
        r.bold = True
        r.font.size = Pt(11)

    doc.add_page_break()

    # =========================================================================
    # SUMÁRIO
    # =========================================================================
    add_heading_1(doc, "SUMÁRIO")
    toc_items = [
        ("1. INTRODUÇÃO", "4"),
        ("2. OBJETIVOS E EVOLUÇÃO DO MODELO", "4"),
        ("3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO (1FN, 2FN E 3FN)", "4"),
        ("4. DICIONÁRIO DE DADOS DAS 15 TABELAS", "5"),
        ("5. VIEWS PÚBLICAS", "13"),
        ("6. TIPOS ENUMERADOS (5 ENUMs)", "14"),
        ("7. RESUMO DOS RELACIONAMENTOS (13 CHAVES ESTRANGEIRAS)", "14"),
        ("8. DIAGRAMA CONCEITUAL", "16"),
        ("9. DIAGRAMA LÓGICO / FÍSICO", "17"),
        ("10. EVIDÊNCIAS DE VALIDAÇÃO EM BANCO", "18"),
        ("11. CONSIDERAÇÕES FINAIS E REFERÊNCIAS", "19"),
    ]
    for title_t, pg_t in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{title_t}  ..........................................................  {pg_t}")
        r.font.size = Pt(10.5)
        r.bold = True

    doc.add_page_break()

    # =========================================================================
    # 1. INTRODUÇÃO & 2. OBJETIVOS
    # =========================================================================
    add_heading_1(doc, "1. INTRODUÇÃO")
    add_body(
        doc,
        "Este documento descreve a modelagem relacional e o dicionário de dados do Portal Escolar da EEB Professor Benonívio João Martins "
        "(Palhoça – SC), desenvolvido em Next.js com PostgreSQL 17 na plataforma Supabase. O banco centraliza avisos, galerias de fotos, "
        "acervo histórico, documentos oficiais, páginas institucionais, turmas por ano letivo, grupos de WhatsApp, postagens pedagógicas, "
        "eventos e cardápio da alimentação escolar (PNAE/SED-SC)."
    )

    add_heading_1(doc, "2. OBJETIVOS E EVOLUÇÃO DO MODELO")
    add_heading_2(doc, "2.1. Objetivo Geral")
    add_body(
        doc,
        "Documentar a estrutura física e lógica do banco de dados em total conformidade com o script DDL definitivo "
        "(02_sql/00_ddl_completo_do_zero.sql), garantindo integridade referencial, segurança por RLS e manutenção previsível."
    )
    add_heading_2(doc, "2.2. Objetivos Específicos")
    for item in [
        "Especificar as 15 tabelas, suas colunas, tipos, nulabilidades, tamanhos e valores padrão.",
        "Registrar todas as chaves primárias, estrangeiras (com ON DELETE), restrições UNIQUE, CHECKs e índices.",
        "Documentar as 2 Views públicas (security_invoker = true), os 5 tipos ENUM e os 13 relacionamentos.",
        "Apresentar as evidências dos testes de falha intencional (Crash Tests) e consultas DQL executadas no Supabase.",
    ]:
        add_bullet(doc, item)

    add_heading_2(doc, "2.3. Evolução do Portal Real (Antes vs. Depois)")
    add_body(
        doc,
        "A versão inicial em produção utilizava 9 tabelas com listas armazenadas em JSONB, sem histórico de ano letivo em turmas, "
        "com redundância de turno nos grupos de WhatsApp e leitura pública irrestrita. Na refatoração da Avaliação A3, o modelo passou "
        "a 15 tabelas normalizadas até a 3FN, 5 ENUMs, 2 Views públicas e 70 políticas RLS granulares."
    )

    # =========================================================================
    # 3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO
    # =========================================================================
    add_heading_1(doc, "3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO (1FN, 2FN E 3FN)")
    regras = [
        ("1FN (Eliminação de JSONB): ", "Listas de fotos e links foram movidas para tabelas filhas 1:N ordenadas (ordem >= 0 e UNIQUE composta): escola_avisos_imagens, escola_acervo_imagens e escola_turmas_links."),
        ("2FN (Resolução de N:N): ", "Eventos e turmas ligam-se pela tabela associativa escola_turmas_eventos com chave primária composta (evento_id, turma_id)."),
        ("3FN (Sem Dependência Transitiva): ", "escola_whatsapp_grupos não repete o campo turno; essa informação pertence a escola_turmas e é consultada via JOIN."),
        ("Histórico por Ano Letivo: ", "escola_turmas possui ano_letivo e chave única (ano_letivo, ano, nome, turno), preservando anos anteriores (ex.: 2025 e 2026) sem sobrescrita."),
        ("Vínculo 1:1 Turma e WhatsApp: ", "UNIQUE em escola_whatsapp_grupos(turma_id) impede mais de um grupo oficial por turma."),
        ("Cardápio Único: ", "UNIQUE (data, turno) em escola_refeicoes evita dois cardápios para o mesmo dia e período."),
        ("Preservação de Autoria: ", "As 6 FKs de autor_id usam ON DELETE SET NULL para manter o histórico público mesmo se um operador for removido."),
        ("Segurança em Camadas: ", "Todas as 15 tabelas usam RLS; visitantes anônimos leem apenas registros publicados/ativos, e as 2 Views usam WITH (security_invoker = true)."),
    ]
    for bp, txt in regras:
        add_bullet(doc, txt, bold_prefix=bp)

    # =========================================================================
    # 4. DICIONÁRIO DE DADOS DAS 15 TABELAS
    # =========================================================================
    add_heading_1(doc, "4. DICIONÁRIO DE DADOS DAS 15 TABELAS")
    add_body(
        doc,
        "Convenções na coluna Observação: PK = Chave Primária; FK = Chave Estrangeira; NN = NOT NULL; Null = Permite Nulo; "
        "UQ = UNIQUE; UQ Comp. = UNIQUE Composta; UTC = DEFAULT timezone('utc', now())."
    )

    col_w = [2.8, 2.3, 2.5, 1.3, 5.2, 2.4]
    hdr_cols = ["Nome", "Tipo", "Classe", "Tam.", "Descrição", "Observação"]

    tables_spec = [
        (
            "4.1. Tabela escola_usuarios",
            "Operadores, professores e administradores com acesso ao painel do portal.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do operador (DEFAULT gen_random_uuid())", "PK / NN"],
                ["nome", "Texto", "Simples", "Var.", "Nome completo do usuário/operador", "NN"],
                ["email", "Texto", "Determinante", "Var.", "E-mail institucional único em letras minúsculas", "NN / UQ"],
                ["role", "Enum", "Simples", "4 B", "Papel de permissão (usuario_role_enum; DEFAULT 'editor')", "NN"],
                ["ativo", "Boolean", "Simples", "1 B", "Indica se o cadastro está ativo (DEFAULT true)", "NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização cadastral", "NN / UTC"],
            ],
            [
                "PK: escola_usuarios_pkey (id). Nota de ambiente: na base acadêmica/seed o id usa gen_random_uuid() para massa de testes independente; em produção vincula-se a auth.users(id) ON DELETE CASCADE (ALTER TABLE comentado no DDL).",
                "UNIQUE: escola_usuarios_email_key (email).",
                "CHECK: escola_usuarios_nome_check; ck_escola_usuarios_email_valido (formato de e-mail válido em minúsculas).",
                "Trigger: trg_escola_usuarios_updated_at (trigger_set_updated_at).",
            ],
        ),
        (
            "4.2. Tabela escola_avisos",
            "Comunicados, informes gerais e notícias publicadas no mural oficial.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do aviso (DEFAULT gen_random_uuid())", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título principal do aviso", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Síntese exibida nos cartões de listagem", "NN"],
                ["conteudo", "Texto", "Simples", "Var.", "Texto completo do comunicado", "Null"],
                ["categoria", "Texto", "Simples", "Var.", "Classificação temática (ex.: Matrículas, Geral)", "NN"],
                ["imagem_url", "Texto", "Simples", "Var.", "URL da imagem principal de capa", "Null"],
                ["importancia", "Enum", "Simples", "4 B", "Prioridade (importancia_enum; DEFAULT 'normal')", "NN"],
                ["destaque_home", "Boolean", "Simples", "1 B", "Exibe no carrossel da página inicial (DEFAULT false)", "NN"],
                ["status", "Enum", "Simples", "4 B", "Situação editorial (publicacao_status_enum; DEFAULT 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Início da exibição pública (DEFAULT UTC)", "NN / UTC"],
                ["data_expiracao", "Data/Hora", "Simples", "8 B", "Data limite de vigência pública", "Null"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última modificação", "NN / UTC"],
            ],
            [
                "PK: escola_avisos_pkey (id).",
                "FK: escola_avisos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: titulo, resumo, categoria, conteudo e imagem_url não vazios; ck_avisos_datas (data_expiracao IS NULL OR data_expiracao > data_publicacao).",
                "Índices: ix_escola_avisos_autor; ix_escola_avisos_pub (status, data_publicacao DESC). Trigger: trg_escola_avisos_updated_at.",
            ],
        ),
        (
            "4.3. Tabela escola_avisos_imagens",
            "Fotografias individuais da galeria de cada aviso (1FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da imagem (DEFAULT gen_random_uuid())", "PK / NN"],
                ["aviso_id", "UUID", "Determinante", "16 B", "Referência ao aviso pai em escola_avisos", "FK / NN / UQ Comp."],
                ["url", "Texto", "Simples", "Var.", "URL pública da imagem no Storage", "NN"],
                ["legenda", "Texto", "Simples", "Var.", "Descrição ou crédito da fotografia", "Null"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Posição na galeria (DEFAULT 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de envio em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_avisos_imagens_pkey (id).",
                "FK: escola_avisos_imagens_aviso_id_fkey (aviso_id) → escola_avisos(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_avisos_imagens_aviso_ordem (aviso_id, ordem).",
                "CHECK: url não vazia; legenda não vazia quando informada; escola_avisos_imagens_ordem_check (ordem >= 0).",
            ],
        ),
        (
            "4.4. Tabela escola_acervo",
            "Projetos históricos, edições da Revista Okaza, Grupo Butterfly e memórias escolares.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do item (DEFAULT gen_random_uuid())", "PK / NN"],
                ["ano", "Texto", "Simples", "Var.", "Ano cronológico de referência", "NN"],
                ["categoria", "Texto", "Simples", "Var.", "Categoria do acervo (ex.: Revista Okaza, Projetos)", "NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título descritivo do registro", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Relato histórico detalhado", "Null"],
                ["capa_url", "Texto", "Simples", "Var.", "URL da foto de capa do álbum", "Null"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; DEFAULT 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Data/hora de publicação no portal (DEFAULT UTC)", "NN / UTC"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_acervo_pkey (id).",
                "FK: escola_acervo_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: ano, categoria e titulo não vazios; descricao e capa_url não vazios quando informados.",
                "Índices: ix_escola_acervo_autor; ix_escola_acervo_status_ano (status, ano DESC). Trigger: trg_escola_acervo_updated_at.",
            ],
        ),
        (
            "4.5. Tabela escola_acervo_imagens",
            "Fotografias individuais dos álbuns do acervo histórico (1FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da foto (DEFAULT gen_random_uuid())", "PK / NN"],
                ["acervo_id", "UUID", "Determinante", "16 B", "Referência ao álbum em escola_acervo", "FK / NN / UQ Comp."],
                ["url", "Texto", "Simples", "Var.", "URL pública da imagem no bucket", "NN"],
                ["legenda", "Texto", "Simples", "Var.", "Legenda histórica da fotografia", "Null"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Sequência no álbum (DEFAULT 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de inclusão em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_acervo_imagens_pkey (id).",
                "FK: escola_acervo_imagens_acervo_id_fkey (acervo_id) → escola_acervo(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_acervo_imagens_acervo_ordem (acervo_id, ordem).",
                "CHECK: url não vazia; legenda não vazia quando informada; escola_acervo_imagens_ordem_check (ordem >= 0).",
            ],
        ),
        (
            "4.6. Tabela escola_documentos",
            "Repositório de arquivos oficiais para download público (calendários, PPP, editais e atas).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do documento (DEFAULT gen_random_uuid())", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título público para listagem", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Explicação complementar sobre o arquivo", "Null"],
                ["categoria", "Texto", "Simples", "Var.", "Classificação documental (Calendários, Editais, Atas)", "NN"],
                ["url_arquivo", "Texto", "Simples", "Var.", "Link direto para download no Storage", "NN"],
                ["nome_arquivo", "Texto", "Simples", "Var.", "Nome original do arquivo físico", "NN"],
                ["mime_type", "Texto", "Simples", "Var.", "Formato MIME (ex.: application/pdf)", "NN"],
                ["tamanho_bytes", "Número (Int8)", "Simples", "8 B", "Tamanho do arquivo em bytes (>= 0)", "NN"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; DEFAULT 'publicado')", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador responsável em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de upload em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização", "NN / UTC"],
            ],
            [
                "PK: escola_documentos_pkey (id).",
                "FK: escola_documentos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: titulo, categoria, url_arquivo, nome_arquivo, mime_type e descricao não vazios; tamanho_bytes >= 0.",
                "Índices: ix_escola_documentos_autor; ix_escola_documentos_cat (categoria, status). Trigger: trg_escola_documentos_updated_at.",
            ],
        ),
        (
            "4.7. Tabela escola_conteudo_paginas",
            "Conteúdo dinâmico das páginas institucionais fixas do portal (Sobre, APP, Projetos).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da página (DEFAULT gen_random_uuid())", "PK / NN"],
                ["slug", "Texto", "Determinante", "Var.", "Identificador único de rota amigável (kebab-case)", "NN / UQ"],
                ["titulo", "Texto", "Simples", "Var.", "Título exibido no topo da página", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Descrição curta para indexação", "Null"],
                ["conteudo_html", "Texto", "Simples", "Var.", "Corpo estruturado em HTML/Texto", "Null"],
                ["imagem_url", "Texto", "Simples", "Var.", "URL do banner principal da página", "Null"],
                ["publicado", "Boolean", "Simples", "1 B", "Define visibilidade pública (DEFAULT true)", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador editor em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última edição", "NN / UTC"],
            ],
            [
                "PK: escola_conteudo_paginas_pkey (id).",
                "FK: escola_conteudo_paginas_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "UNIQUE: escola_conteudo_paginas_slug_key (slug).",
                "CHECK: ck_escola_conteudo_paginas_slug_formato (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'); campos textuais não vazios.",
                "Índices: ix_escola_conteudo_paginas_autor; ix_escola_conteudo_paginas_pub_slug (publicado, slug). Trigger: trg_escola_conteudo_paginas_updated_at.",
            ],
        ),
        (
            "4.8. Tabela escola_turmas",
            "Turmas regulares da escola organizadas por ano letivo, série e turno (3FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da turma (DEFAULT gen_random_uuid())", "PK / NN"],
                ["ano_letivo", "Número (Int4)", "Determinante", "4 B", "Ano letivo de vigência (DEFAULT 2026; >= 2000)", "NN / UQ Comp."],
                ["ano", "Texto", "Determinante", "Var.", "Série ou etapa de ensino (ex.: 1º Ano Ensino Médio)", "NN / UQ Comp."],
                ["nome", "Texto", "Determinante", "Var.", "Código identificador da turma (ex.: 101, 201, 901)", "NN / UQ Comp."],
                ["turno", "Enum", "Determinante", "4 B", "Período das aulas (turno_enum)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de abertura em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última modificação", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_pkey (id).",
                "UNIQUE: uq_turmas_ano_letivo_serie_nome_turno (ano_letivo, ano, nome, turno).",
                "CHECK: escola_turmas_ano_letivo_check (ano_letivo >= 2000); ano e nome não vazios.",
                "Trigger: trg_escola_turmas_updated_at.",
            ],
        ),
        (
            "4.9. Tabela escola_turmas_links",
            "Links externos de apoio de cada turma (Classroom, Drive) em 1FN.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do link (DEFAULT gen_random_uuid())", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "FK / NN / UQ Comp."],
                ["titulo", "Texto", "Simples", "Var.", "Rótulo do link complementar", "NN"],
                ["url", "Texto", "Simples", "Var.", "Endereço web completo", "NN"],
                ["ordem", "Número (Int4)", "Simples", "4 B", "Ordem de exibição (DEFAULT 0; >= 0)", "NN / UQ Comp."],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de cadastro em UTC", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_links_pkey (id).",
                "FK: escola_turmas_links_turma_id_fkey (turma_id) → escola_turmas(id) ON DELETE CASCADE.",
                "UNIQUE: uq_escola_turmas_links_turma_ordem (turma_id, ordem).",
                "CHECK: titulo e url não vazios; escola_turmas_links_ordem_check (ordem >= 0).",
            ],
        ),
        (
            "4.10. Tabela escola_whatsapp_grupos",
            "Links de convite dos grupos oficiais de WhatsApp por turma (relação 1:1 em 3FN).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do grupo (DEFAULT gen_random_uuid())", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência única (1:1) para escola_turmas", "FK / NN / UQ"],
                ["nome", "Texto", "Simples", "Var.", "Nome de exibição do grupo oficial", "NN"],
                ["link_convite", "Texto", "Simples", "Var.", "URL de entrada no grupo do WhatsApp", "NN"],
                ["ativo", "Boolean", "Simples", "1 B", "Indica se o convite está ativo (DEFAULT true)", "NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última atualização", "NN / UTC"],
            ],
            [
                "PK: escola_whatsapp_grupos_pkey (id).",
                "FK: escola_whatsapp_grupos_turma_id_fkey (turma_id) → escola_turmas(id) ON DELETE CASCADE.",
                "UNIQUE: escola_whatsapp_grupos_turma_id_key (turma_id) — garante cardinalidade 1:1.",
                "CHECK: nome e link_convite não vazios. Trigger: trg_escola_whatsapp_grupos_updated_at.",
            ],
        ),
        (
            "4.11. Tabela escola_turmas_posts",
            "Comunicados, materiais de aula e avisos de provas no mural de cada turma.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único da postagem (DEFAULT gen_random_uuid())", "PK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "FK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Assunto ou título da atividade", "NN"],
                ["resumo", "Texto", "Simples", "Var.", "Breve descrição apresentada na listagem", "Null"],
                ["conteudo", "Texto", "Simples", "Var.", "Orientações completas da atividade", "Null"],
                ["imagem_url", "Texto", "Simples", "Var.", "URL de imagem ilustrativa", "Null"],
                ["link_referencia", "Texto", "Simples", "Var.", "Link externo complementar", "Null"],
                ["status", "Enum", "Simples", "4 B", "Estado editorial (publicacao_status_enum; DEFAULT 'publicado')", "NN"],
                ["data_publicacao", "Data/Hora", "Simples", "8 B", "Liberação pública do post (DEFAULT UTC)", "NN / UTC"],
                ["data_expiracao", "Data/Hora", "Simples", "8 B", "Data limite de exibição", "Null"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador autor em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última edição", "NN / UTC"],
            ],
            [
                "PK: escola_turmas_posts_pkey (id).",
                "FKs: turma_id → escola_turmas(id) ON DELETE CASCADE; autor_id → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: campos textuais não vazios; ck_turmas_posts_datas (data_expiracao IS NULL OR data_expiracao > data_publicacao).",
                "Índices: ix_escola_turmas_posts_autor; ix_escola_turmas_posts_pub (turma_id, status, data_publicacao DESC). Trigger: trg_escola_turmas_posts_updated_at.",
            ],
        ),
        (
            "4.12. Tabela escola_eventos",
            "Programação do calendário escolar (feiras científicas, reuniões e eventos culturais).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do evento (DEFAULT gen_random_uuid())", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Nome oficial do evento", "NN"],
                ["descricao", "Texto", "Simples", "Var.", "Detalhamento do cronograma e objetivos", "Null"],
                ["local", "Texto", "Simples", "Var.", "Espaço físico de realização", "Null"],
                ["data_inicio", "Data/Hora", "Simples", "8 B", "Data e horário de início", "NN"],
                ["data_fim", "Data/Hora", "Simples", "8 B", "Data e horário de término (>= data_inicio)", "Null"],
                ["dia_inteiro", "Boolean", "Simples", "1 B", "Evento de dia inteiro (DEFAULT false)", "NN"],
                ["imagem_url", "Texto", "Simples", "Var.", "URL do cartaz de divulgação", "Null"],
                ["status", "Enum", "Simples", "4 B", "Situação operacional (status_enum; DEFAULT 'ativo')", "NN"],
                ["autor_id", "UUID", "Determinante", "16 B", "Operador organizador em escola_usuarios", "FK / Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_eventos_pkey (id).",
                "FK: escola_eventos_autor_id_fkey (autor_id) → escola_usuarios(id) ON DELETE SET NULL.",
                "CHECK: titulo, descricao, local e imagem_url não vazios; ck_eventos_datas (data_fim IS NULL OR data_fim >= data_inicio).",
                "Índices: ix_escola_eventos_autor; ix_escola_eventos_datas; ix_escola_eventos_status_inicio. Trigger: trg_escola_eventos_updated_at.",
            ],
        ),
        (
            "4.13. Tabela escola_turmas_eventos",
            "Entidade associativa que resolve o relacionamento N:N entre Eventos e Turmas (2FN/3FN).",
            [
                ["evento_id", "UUID", "Determinante", "16 B", "Referência ao evento em escola_eventos", "PK Comp. / FK / NN"],
                ["turma_id", "UUID", "Determinante", "16 B", "Referência à turma em escola_turmas", "PK Comp. / FK / NN"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora do vínculo em UTC", "NN / UTC"],
            ],
            [
                "PK Composta: escola_turmas_eventos_pkey (evento_id, turma_id).",
                "FKs: evento_id → escola_eventos(id) ON DELETE CASCADE; turma_id → escola_turmas(id) ON DELETE CASCADE.",
                "Índice: ix_escola_turmas_eventos_turma (turma_id).",
            ],
        ),
        (
            "4.14. Tabela escola_refeicoes",
            "Cardápio diário da alimentação escolar por data e turno (PNAE/SED-SC).",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do registro (DEFAULT gen_random_uuid())", "PK / NN"],
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
                "CHECK: descricao não vazia; observacoes não vazia quando informada. Trigger: trg_escola_refeicoes_updated_at.",
            ],
        ),
        (
            "4.15. Tabela escola_notificacoes",
            "Alertas globais e comunicados urgentes exibidos no topo ou modal do portal.",
            [
                ["id", "UUID", "Determinante", "16 B", "Identificador único do alerta (DEFAULT gen_random_uuid())", "PK / NN"],
                ["titulo", "Texto", "Simples", "Var.", "Título curto de chamada", "NN"],
                ["mensagem", "Texto", "Simples", "Var.", "Texto explicativo do alerta", "NN"],
                ["importancia", "Enum", "Simples", "4 B", "Criticidade (importancia_enum; DEFAULT 'normal')", "NN"],
                ["ativa", "Boolean", "Simples", "1 B", "Define se o alerta está habilitado (DEFAULT true)", "NN"],
                ["data_inicio", "Data/Hora", "Simples", "8 B", "Início da exibição automática (DEFAULT UTC)", "NN / UTC"],
                ["data_fim", "Data/Hora", "Simples", "8 B", "Fim da exibição (>= data_inicio)", "Null"],
                ["created_at", "Data/Hora", "Simples", "8 B", "Data/hora de criação em UTC", "NN / UTC"],
                ["updated_at", "Data/Hora", "Simples", "8 B", "Data/hora da última alteração", "NN / UTC"],
            ],
            [
                "PK: escola_notificacoes_pkey (id).",
                "CHECK: titulo e mensagem não vazios; ck_notificacoes_datas (data_fim IS NULL OR data_fim >= data_inicio).",
                "Índice: ix_escola_notificacoes_ativa (ativa, data_inicio, data_fim). Trigger: trg_escola_notificacoes_updated_at.",
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
        r_rl.font.color.rgb = NAVY
        for n in notes:
            add_bullet(doc, n)

    # =========================================================================
    # 5. VIEWS PÚBLICAS
    # =========================================================================
    add_heading_1(doc, "5. VIEWS PÚBLICAS")
    add_body(
        doc,
        "Ambas as Views foram criadas com WITH (security_invoker = true) no PostgreSQL 17, executando sob as políticas RLS do usuário "
        "invocador e expondo apenas conteúdos publicados e vigentes:"
    )

    add_heading_2(doc, "5.1. View public.escola_avisos_publicos")
    add_body(
        doc,
        "status = 'publicado' AND data_publicacao <= timezone('utc', now()) AND (data_expiracao IS NULL OR data_expiracao > timezone('utc', now())).",
        bold_prefix="Filtro: ",
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
            ["imagem_url", "text", "URL da imagem principal"],
            ["importancia", "importancia_enum", "Prioridade editorial (normal, importante, urgente)"],
            ["destaque_home", "boolean", "Sinaliza exibição no carrossel da home"],
            ["data_publicacao", "timestamptz", "Início da exibição pública"],
            ["data_expiracao", "timestamptz", "Limite de vigência"],
        ],
        [4.0, 4.0, 8.5],
        font_size_pt=8.8,
    )

    add_heading_2(doc, "5.2. View public.escola_eventos_publicos")
    add_body(doc, "status = 'ativo'::public.status_enum.", bold_prefix="Filtro: ", space_after=4, keep_with_next=True)
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
            ["imagem_url", "text", "URL do cartaz de divulgação"],
        ],
        [4.0, 4.0, 8.5],
        font_size_pt=8.8,
    )

    # =========================================================================
    # 6. TIPOS ENUMERADOS (5 ENUMs)
    # =========================================================================
    add_heading_1(doc, "6. TIPOS ENUMERADOS (5 ENUMs)")
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
    )

    # =========================================================================
    # 7. RESUMO DOS RELACIONAMENTOS (13 FKs)
    # =========================================================================
    add_heading_1(doc, "7. RESUMO DOS RELACIONAMENTOS (13 CHAVES ESTRANGEIRAS)")
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
    )

    # =========================================================================
    # 8. DIAGRAMA CONCEITUAL & 9. DIAGRAMA LÓGICO
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "8. DIAGRAMA CONCEITUAL")
    add_body(
        doc,
        "Representação conceitual das entidades do domínio escolar, seus atributos principais de negócio e cardinalidades (1:1, 1:N e N:N).",
        keep_with_next=True,
    )
    if IMG_CONCEITUAL.exists():
        add_fitted_picture(doc, IMG_CONCEITUAL, max_w_in=6.2, max_h_in=7.3)
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc1 = p_cap1.add_run("Figura 1 — Modelo Conceitual do Portal Escolar (01_modelagem/der_conceitual.mmd).")
        rc1.italic = True
        rc1.font.size = Pt(9)
        rc1.font.color.rgb = MUTED

    doc.add_page_break()
    add_heading_1(doc, "9. DIAGRAMA LÓGICO / FÍSICO")
    add_body(
        doc,
        "Representação lógica das 15 tabelas relacionais, chaves primárias, estrangeiras, únicas, tipos SQL e cardinalidades (dbdiagram.io).",
        keep_with_next=True,
    )
    img_logico = IMG_LOGICO_DBDIAGRAM if IMG_LOGICO_DBDIAGRAM.exists() else IMG_LOGICO_MERMAID
    if img_logico.exists():
        add_fitted_picture(doc, img_logico, max_w_in=6.3, max_h_in=7.4)
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc2 = p_cap2.add_run(f"Figura 2 — Modelo Lógico com 15 tabelas e 13 FKs ({img_logico.name}).")
        rc2.italic = True
        rc2.font.size = Pt(9)
        rc2.font.color.rgb = MUTED

    # =========================================================================
    # 10. EVIDÊNCIAS DE VALIDAÇÃO
    # =========================================================================
    doc.add_page_break()
    add_heading_1(doc, "10. EVIDÊNCIAS DE VALIDAÇÃO EM BANCO")
    add_body(
        doc,
        "Validação executada no projeto problemaescola vFinal (rbowxcvpcaqrycrvfowh, PostgreSQL 17.11.0.003), com 0 alertas de "
        "políticas RLS duplicadas, 0 alertas de search_path mutável e 102 registros populados."
    )

    add_heading_2(doc, "10.1. Resumo da Massa de Dados (102 Registros)")
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
    )

    add_heading_2(doc, "10.2. Crash Tests Executados (05_crash_test_integridade.sql)")
    add_styled_table(
        doc,
        ["Teste", "Cenário Inválido Testado", "SQLSTATE", "Constraint Que Bloqueou"],
        [
            ["T1", "Turma duplicada no mesmo ano letivo/série/turno", "23505", "uq_turmas_ano_letivo_serie_nome_turno"],
            ["T2", "Dois cardápios para a mesma data e turno", "23505", "uq_refeicoes_data_turno"],
            ["T3", "Segundo grupo de WhatsApp para a mesma turma", "23505", "escola_whatsapp_grupos_turma_id_key"],
            ["T4", "Evento com data_fim anterior a data_inicio", "23514", "ck_eventos_datas"],
            ["T5a/b/c", "E-mail inválido / nome em branco / slug fora de kebab-case", "23514", "ck_..._email_valido / nome_check / slug_formato"],
            ["T6", "Post vinculado a turma_id UUID inexistente", "23503", "escola_turmas_posts_turma_id_fkey"],
        ],
        [1.5, 6.2, 1.8, 7.0],
        font_size_pt=8.5,
    )

    add_heading_2(doc, "10.3. Consultas DQL Validadas ao Vivo (06_consultas_apresentacao.sql)")
    for q in [
        "Q1 (JOIN 3FN): Turmas de 2026 com WhatsApp ativo e total de links (101: 3; 201: 2; 301: 3).",
        "Q2 (COUNT/SUM/AVG): Documentos por categoria (Pedagógico 2.50 MB; Calendários 1.50 MB; Editais 1.34 MB; Atas 0.38 MB).",
        "Q3 (MIN/MAX + N:N): 3 eventos ativos (06/12/2026 a 02/02/2027) e contagem de turmas participantes.",
        "Q4 (GROUP BY + HAVING): 4 turmas com 2 ou mais links complementares.",
        "Q5 (LEFT JOIN + COALESCE): Todas as 6 turmas com contagem exata de posts publicados, mantendo zeros.",
        "Q6 (NOT EXISTS): Identificação da turma 2026-901 (matutino) sem grupo de WhatsApp.",
        "Q7 (Histórico 2025 vs. 2026): 2 turmas / 3 posts em 2025 e 4 turmas / 6 posts em 2026.",
        "Q8 (Views Públicas): escola_avisos_publicos retornou 4 de 6 avisos; escola_eventos_publicos retornou 3 de 5 eventos.",
    ]:
        add_bullet(doc, q)

    # =========================================================================
    # 11. CONSIDERAÇÕES FINAIS E REFERÊNCIAS
    # =========================================================================
    add_heading_1(doc, "11. CONSIDERAÇÕES FINAIS")
    add_body(
        doc,
        "O modelo relacional consolidado para o Portal Escolar da EEB Professor Benonívio João Martins atende às normas 1FN, 2FN e 3FN, "
        "garante integridade declarativa no PostgreSQL 17 e separa de forma segura a exposição pública do controle administrativo via RLS "
        "e Views com security_invoker = true."
    )

    add_heading_1(doc, "REFERÊNCIAS")
    refs = [
        "DATE, Christopher J. Introdução a sistemas de bancos de dados. 8. ed. Rio de Janeiro: Elsevier, 2004.",
        "ELMASRI, Ramez; NAVATHE, Shamkant B. Sistemas de banco de dados. 7. ed. São Paulo: Pearson, 2019.",
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

    entrega_docx = ROOT / "04_entrega_final" / "01_Dicionario_de_Dados_A3_EEB_Benonivio.docx"
    entrega_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(entrega_docx))
    print("DOCX_ENTREGA_SAVED:", entrega_docx)
    try:
        doc.save(str(OUT_PATH))
        print("DOCX_SAVED:", OUT_PATH)
    except PermissionError:
        print("WARN_LOCKED:", OUT_PATH, "(arquivo aberto no Word; versao atualizada salva em 04_entrega_final)")


if __name__ == "__main__":
    build_doc()
