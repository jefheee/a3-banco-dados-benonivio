from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent.parent
OUT_DOCX = ROOT / "03_apresentacao" / "GUIA_EQUIPE_APRESENTACAO.docx"

NAVY = RGBColor(0x0F, 0x25, 0x37)
BLUE = RGBColor(0x1E, 0x40, 0xAF)
TEAL = RGBColor(0x0F, 0x76, 0x6E)
DARK = RGBColor(0x1E, 0x29, 0x3B)
MUTED = RGBColor(0x47, 0x55, 0x69)


def set_cell_shading(cell, fill_hex):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))


def set_cell_margins(cell, top=65, bottom=65, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1"):
    table._tbl.tblPr.append(parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="0F2537"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        </w:tblBorders>
    '''))


def add_section_title(doc, text, page_break=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0 if page_break else 10)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.page_break_before = page_break
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(14.5)
    r.font.color.rgb = NAVY
    p._p.get_or_add_pPr().append(
        parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="3" w:color="1E40AF"/></w:pBdr>')
    )
    return p


def add_sub(doc, text, color=BLUE):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(11)
    r.font.color.rgb = color
    return p


def add_p(doc, text, bold_prefix=None, size=10, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(size)
        rb.font.color.rgb = NAVY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = DARK
    return p


def add_bullet(doc, text, bold_prefix=None, size=9.8):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.13
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Calibri"
        rb.font.size = Pt(size)
        rb.font.color.rgb = NAVY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.font.color.rgb = DARK
    return p


def add_box(doc, title, lines, accent_hex="1E40AF", bg_hex="F8FAFC"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.7)
    set_cell_shading(cell, bg_hex)
    set_cell_margins(cell, top=80, bottom=80, left=120, right=110)
    tbl._tbl.tblPr.append(parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>
            <w:left w:val="single" w:sz="18" w:space="0" w:color="{accent_hex}"/>
        </w:tblBorders>
    '''))
    tbl.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_after = Pt(3)
    rt = p0.add_run(title)
    rt.bold = True
    rt.font.name = "Calibri"
    rt.font.size = Pt(10.5)
    rt.font.color.rgb = NAVY

    for ln in lines:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.13
        r = p.add_run(ln)
        r.font.name = "Calibri"
        r.font.size = Pt(9.6)
        r.font.color.rgb = DARK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(3)


def add_member_block(doc, header, slides_info, understand, script_bullets, screen_steps, page_break=False):
    add_section_title(doc, header, page_break=page_break)
    add_p(doc, slides_info, bold_prefix="Sua parte na apresentação: ", size=10, space_after=5)
    add_box(doc, "O que você precisa entender (em português simples)", understand, accent_hex="0F766E")
    add_sub(doc, "Roteiro de fala natural (fale com suas palavras, sem decorar):", color=BLUE)
    for bp, txt in script_bullets:
        add_bullet(doc, txt, bold_prefix=bp)
    add_sub(doc, "O que mostrar / clicar na tela:", color=TEAL)
    for st in screen_steps:
        add_bullet(doc, st)


def build_guide():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(1.7)
        sec.bottom_margin = Cm(1.6)
        sec.left_margin = Cm(2.1)
        sec.right_margin = Cm(2.1)
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run("USO INTERNO DA EQUIPE — NÃO ENVIAR AOS PROFESSORES  |  Guia de Apresentação A3  |  Pág. ")
        r.font.name = "Calibri"
        r.font.size = Pt(8)
        r.font.color.rgb = MUTED
        p._p.append(parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls("w")))

    # =========================================================================
    # PAGINA 1 — RESUMO EM 1 MINUTO + DIVISÃO DO GRUPO
    # =========================================================================
    p_top = doc.add_paragraph()
    p_top.paragraph_format.space_after = Pt(2)
    rt = p_top.add_run("GUIA DE ESTUDO E FALA DA EQUIPE — AVALIAÇÃO A3 (BANCO DE DADOS)")
    rt.bold = True
    rt.font.name = "Calibri"
    rt.font.size = Pt(15)
    rt.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(8)
    rs = p_sub.add_run(
        "Material exclusivo para estudo do grupo (Jefherson, Daniel, Maicon e Gabriel). "
        "Fácil de ler no celular ou impresso. NÃO enviar este arquivo por e-mail aos professores."
    )
    rs.italic = True
    rs.font.name = "Calibri"
    rs.font.size = Pt(9.5)
    rs.font.color.rgb = MUTED

    add_section_title(doc, "1. Resumo do Projeto em 1 Minuto")
    add_box(
        doc,
        "A história do nosso trabalho em 4 frases:",
        [
            "• O site da EEB Prof. Benonívio João Martins (escolabenonivio.vercel.app) já existe e funciona de verdade em Palhoça.",
            "• Na versão inicial, o banco tinha 9 tabelas com fotos e links guardados em listas JSON, sem separar ano letivo das turmas e repetindo o turno no grupo de WhatsApp.",
            "• Na A3, refizemos o banco do zero no PostgreSQL (Supabase) com 15 tabelas normalizadas (1FN, 2FN e 3FN), 5 ENUMs, 13 chaves estrangeiras e 2 Views públicas.",
            "• Validamos tudo com 102 registros realistas (2025 e 2026), testes que provam que o banco bloqueia erros sozinho e consultas SQL respondendo perguntas reais da escola.",
        ],
        accent_hex="1E40AF",
    )

    add_section_title(doc, "2. Divisão do Grupo e Ordem de Fala (~10 a 12 minutos no total)")
    tbl = doc.add_table(rows=5, cols=5)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)
    widths = [1.4, 3.2, 2.2, 4.9, 5.0]
    headers = ["Ordem", "Integrante (RA)", "Tempo", "Slides e Assunto", "O que abrir na tela"]
    for i, h in enumerate(headers):
        c = tbl.cell(0, i)
        c.width = Cm(widths[i])
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(c, "0F2537")
        set_cell_margins(c, top=75, bottom=75, left=75, right=75)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    plan_rows = [
        ("1º", "Jefherson Luiz\n(10725114819)", "2,5 a 3 min", "Slides 1, 2 e 3\nCapa, Projeto Real e Antes vs. Depois", "Slides + site escolabenonivio.vercel.app aberto em uma aba (rápido)"),
        ("2º", "Daniel Alves\n(1072517730)", "2,5 a 3 min", "Slides 4, 5 e 6\n1FN/2FN/3FN, Diagrama Conceitual e Lógico", "Slides 4, 5 e 6 (apontar as ligações nos diagramas)"),
        ("3º", "Maicon Lodetti\n(1072511629)", "2,5 a 3 min", "Slides 7 e 8\nRegras de Integridade + Testes no Banco", "Slides 7–8 + SQL Editor do Supabase rodando 2 testes rápidos"),
        ("4º", "Gabriel Grando\n(10725118226)", "2,5 a 3 min", "Slides 9 e 10\nConsultas SQL ao vivo + Encerramento", "Slide 9 + SQL Editor rodando consultas + Slide 10 (Obrigado)"),
    ]
    for r_i, row_d in enumerate(plan_rows, start=1):
        tbl.rows[r_i]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate(row_d):
            c = tbl.cell(r_i, c_i)
            c.width = Cm(widths[c_i])
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_shading(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=75, right=75)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = DARK
            if c_i in (0, 1):
                r.bold = True

    add_p(doc, "", space_after=4)
    add_p(
        doc,
        "Professores avaliadores: Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves (UNISUL Pedra Branca).",
        bold_prefix="Banca: ",
        size=9.5,
    )

    # =========================================================================
    # PAGINA 2 — JEFHERSON & DANIEL (começando em página nova)
    # =========================================================================
    add_member_block(
        doc,
        "Parte 1 — Jefherson Luiz (RA: 10725114819)",
        "Slides 1, 2 e 3 (~2,5 a 3 minutos) — Abertura, Projeto Real e Antes vs. Depois.",
        [
            "• Você abre a apresentação dando contexto: o site da escola já existe de verdade, não é um exemplo inventado.",
            "• O ponto-chave é mostrar a dor real da versão antiga: listas dentro de JSON, turmas sem ano letivo e dado repetido.",
            "• Feche sua fala passando a bola para o Daniel explicar como normalizamos isso na 1FN, 2FN e 3FN.",
        ],
        [
            ("Slide 1 (Capa): ", "Cumprimente os professores Fernando e Henrique, apresente o nome do grupo e o tema: reconstrução do banco de dados do Portal Escolar da EEB Prof. Benonívio João Martins."),
            ("Slide 2 (O Projeto Real): ", "Explique que esse portal já está publicado em escolabenonivio.vercel.app, atendendo alunos, pais e professores com avisos, turmas, grupos de WhatsApp, eventos, documentos, acervo e cardápio."),
            ("Slide 3 (Antes vs. Depois): ", "Mostre o salto: saímos de 9 tabelas com listas em JSON para 15 tabelas organizadas; colocamos ano letivo nas turmas para guardar o histórico de 2025, 2026 e próximos anos; tiramos o turno repetido do WhatsApp; trouxemos as validações para o banco e separamos acesso de visitante e equipe."),
            ("Gancho pro Daniel: ", "'Agora o Daniel vai mostrar como aplicamos 1FN, 2FN e 3FN e como ficou a modelagem conceitual e lógica.'"),
        ],
        [
            "Deixar a apresentação em tela cheia (Slide 1 -> 2 -> 3).",
            "Opcional: mostrar por 15 segundos a aba do portal real (escolabenonivio.vercel.app) para a banca ver que o sistema existe.",
        ],
        page_break=True,
    )

    add_member_block(
        doc,
        "Parte 2 — Daniel Alves (RA: 1072517730)",
        "Slides 4, 5 e 6 (~2,5 a 3 minutos) — Normalização (1FN, 2FN, 3FN) e Diagramas Conceitual e Lógico.",
        [
            "• 1FN = nada de lista dentro de uma coluna (tiramos fotos e links de dentro do JSON e criamos tabelas filhas).",
            "• 2FN = relação muitos-para-muitos resolvida com tabela do meio (escola_turmas_eventos liga Eventos e Turmas).",
            "• 3FN = não repetir dado que já existe em outra tabela (turno fica só em Turmas, saiu de WhatsApp).",
            "• No Diagrama Conceitual focamos nas ideias e ligações (1:1, 1:N, N:N); no Lógico aparecem as 15 tabelas reais com chaves e tipos.",
        ],
        [
            ("Slide 4 (1FN, 2FN e 3FN): ", "Dê 1 exemplo rápido de cada forma normal: 1FN tirando fotos e links de listas para tabelas próprias; 2FN criando escola_turmas_eventos para ligar eventos e turmas; 3FN removendo turno repetido do grupo de WhatsApp."),
            ("Slide 5 (Diagrama Conceitual): ", "Aponte 4 ligações na imagem: 1:1 entre Turma e Grupo de WhatsApp; 1:N de Aviso para Imagens e Turma para Posts/Links; N:N entre Evento e Turma; e autoria opcional (0..1:N) ligada a Usuário."),
            ("Slide 6 (Diagrama Lógico): ", "Mostre como o Conceitual virou 15 tabelas concretas no banco, divididas em 5 grupos (Acesso, Turmas, Mural, Memória/Arquivos e Agenda/Rotina), com 13 chaves estrangeiras e 5 ENUMs."),
            ("Gancho pro Maicon: ", "'Agora o Maicon vai explicar as regras que protegem esses dados e rodar os testes no banco.'"),
        ],
        [
            "Passar para o Slide 4 e apontar cada coluna (1FN, 2FN, 3FN).",
            "No Slide 5 e Slide 6, usar o mouse para apontar na imagem a ligação Turma–WhatsApp (1:1) e a tabela escola_turmas_eventos (N:N).",
        ],
        page_break=True,
    )

    # =========================================================================
    # PAGINA 4 — MAICON & GABRIEL
    # =========================================================================
    add_member_block(
        doc,
        "Parte 3 — Maicon Lodetti (RA: 1072511629)",
        "Slides 7 e 8 (~2,5 a 3 minutos) — Regras de Integridade, Segurança e Testes ao Vivo no Supabase.",
        [
            "• Em vez de depender só do site para evitar erros, colocamos as regras dentro do próprio PostgreSQL.",
            "• CASCADE = apagou o pai (ex.: aviso ou turma), o banco limpa junto as fotos/links filhos. SET NULL = apagou um usuário autor, os avisos continuam no ar (só ficam sem autor).",
            "• Nos testes ao vivo, o objetivo É DAR ERRO! O erro vermelho na tela prova que o banco bloqueou o dado errado.",
        ],
        [
            ("Slide 7 (Regras e Segurança): ", "Explique os 4 pilares: chaves únicas (não duplica turma no mesmo ano nem cardápio no mesmo dia/turno), validações de data e texto vazio, diferença entre CASCADE e SET NULL, e controle de acesso (visitante só vê o que está publicado)."),
            ("Slide 8 (Testes de Validação): ", "Diga: 'Para não ficar só na teoria, testamos erros de propósito no PostgreSQL para ver o banco barrar'. Cite os 4 casos da tabela."),
            ("Ao vivo no Supabase: ", "Rode 2 testes rápidos (ex.: tentar duplicar um cardápio no mesmo dia/turno e tentar cadastrar um evento com data final antes da inicial) mostrando a mensagem de bloqueio."),
            ("Gancho pro Gabriel: ", "'Com o banco protegido, agora o Gabriel vai mostrar as consultas SQL respondendo perguntas reais da escola.'"),
        ],
        [
            "Abrir a aba do Supabase -> SQL Editor no projeto problemaescola vFinal.",
            "Colar e rodar o Teste T2 (cardápio duplicado) dentro de BEGIN; ... ROLLBACK; -> mostrar o erro de chave única.",
            "Rodar o Teste T4 (evento com data final antes da inicial) -> mostrar o erro da regra CHECK de datas.",
        ],
        page_break=True,
    )

    add_member_block(
        doc,
        "Parte 4 — Gabriel Grando (RA: 10725118226)",
        "Slides 9 e 10 (~2,5 a 3 minutos) — Demonstração das Consultas SQL ao Vivo e Encerramento.",
        [
            "• Você fecha mostrando o banco funcionando com dados reais simulados (102 registros entre 2025 e 2026).",
            "• Cada consulta prova um conceito da disciplina: JOIN (3FN), COUNT/SUM/AVG, LEFT JOIN / NOT EXISTS, histórico por ano letivo e Views.",
            "• O ponto alto é mostrar as Views: a tabela tem 6 avisos (com rascunho e vencido), mas a View só mostra os 4 válidos para o público.",
        ],
        [
            ("Slide 9 (Consultas SQL): ", "Apresente rapidamente as 4 perguntas da escola que o banco responde com os dados de 2025 e 2026."),
            ("Ao vivo no Supabase: ", "Execute 3 ou 4 consultas na tela comentando o resultado: (1) Turmas de 2026 com WhatsApp e contagem de links via JOIN; (2) Documentos por categoria somando tamanho em MB; (3) Turma 901 sem WhatsApp (NOT EXISTS); (4) Comparativo 2025 vs 2026 + View escola_avisos_publicos exibindo só 4 de 6 avisos."),
            ("Slide 10 (Encerramento): ", "Agradeça aos professores Fernando e Henrique, reforce que o modelo já está pronto para evoluir o portal real em produção e abra para perguntas."),
        ],
        [
            "No SQL Editor do Supabase, deixar as consultas de 04_consultas_demonstracao.sql já abertas em uma aba separada.",
            "Executar Q1 (JOIN 3FN), Q2 (COUNT/SUM/AVG), Q6 (NOT EXISTS) e Q8 (Views públicas) — leva menos de 1 minuto no total.",
            "Voltar para o Slide 10 (Obrigado!) para responder às perguntas da banca.",
        ],
        page_break=True,
    )

    # =========================================================================
    # PAGINA 5 — SE O PROFESSOR PERGUNTAR... + CHECKLIST
    # =========================================================================
    add_section_title(doc, "Se o Professor Perguntar... (Cola Rápida em Português Simples)", page_break=True)

    qa = [
        (
            "1. O que é 1FN, 2FN e 3FN no projeto de vocês?",
            "1FN: tiramos listas de fotos e links de campos JSON e criamos tabelas filhas próprias. 2FN: criamos escola_turmas_eventos para resolver o muitos-para-muitos entre Eventos e Turmas. 3FN: tiramos o campo turno repetido de escola_whatsapp_grupos, deixando só em escola_turmas."
        ),
        (
            "2. Qual a diferença entre Modelo Conceitual e Modelo Lógico?",
            "O Conceitual mostra a visão de negócio — entidades e ligações (1:1, 1:N, N:N) sem entrar em detalhes do banco. O Lógico traduz isso para a estrutura real do PostgreSQL: as 15 tabelas, chaves primárias e estrangeiras, tipos de dados, ENUMs e tabela associativa."
        ),
        (
            "3. Por que vocês tiraram as colunas JSONB da versão antiga?",
            "Porque guardar listas dentro de JSON quebra a 1FN, dificulta validar cada item individualmente (como ordem única ou link vazio) e deixa consultas e filtros mais lentos. Separando em tabelas próprias, o banco garante integridade de cada foto e link."
        ),
        (
            "4. Qual a diferença entre ON DELETE CASCADE e ON DELETE SET NULL no projeto?",
            "CASCADE apaga automaticamente os filhos dependentes quando o pai é excluído (ex.: apagar um aviso apaga suas fotos). SET NULL preserva o conteúdo histórico quando um usuário sai da escola (os avisos e documentos ficam no portal, apenas com autor_id vazio)."
        ),
        (
            "5. Qual a diferença entre INNER JOIN e LEFT JOIN nas consultas?",
            "INNER JOIN traz só o que tem correspondência dos dois lados (ex.: só turmas que têm grupo de WhatsApp). LEFT JOIN mantém todas as turmas da tabela da esquerda mesmo quando não há posts ou grupo cadastrado, permitindo enxergar os zeros."
        ),
        (
            "6. Por que existe a tabela escola_turmas_eventos?",
            "Porque um evento escolar pode envolver várias turmas e uma mesma turma participa de vários eventos no ano (relação N:N). Em banco relacional, precisamos dessa tabela intermediária com chave composta (evento_id, turma_id) para ligar os dois lados sem duplicar dados."
        ),
        (
            "7. Para que servem as Views públicas que vocês criaram?",
            "Elas funcionam como consultas salvas e prontas para o site: escola_avisos_publicos e escola_eventos_publicos já filtram automaticamente rascunhos, avisos arquivados, eventos inativos e itens com data expirada, deixando o site mais simples e seguro."
        ),
        (
            "8. Por que escola_refeicoes e escola_notificacoes não têm linha ligada às outras tabelas?",
            "Porque são entidades independentes no domínio da escola: o cardápio vale para a escola inteira por data e turno (não pertence a uma turma só), e as notificações são alertas globais exibidos para todos os visitantes do portal."
        ),
    ]
    for q, a in qa:
        add_p(doc, a, bold_prefix=q + "\n", size=9.5, space_after=5)

    add_section_title(doc, "Checklist 5 Minutos Antes da Apresentação")
    for chk in [
        "[ ] Slides abertos em PDF/PPTX em tela cheia e testados no projetor.",
        "[ ] Aba do Supabase aberta no projeto 'problemaescola vFinal' (conferir que NÃO é o banco de produção!).",
        "[ ] Aba 1 no SQL Editor: script de testes de integridade pronto para o Maicon.",
        "[ ] Aba 2 no SQL Editor: script de consultas pronto para o Gabriel.",
        "[ ] Aba 3 no navegador: escolabenonivio.vercel.app aberta para o Jefherson mostrar rapidamente.",
        "[ ] Zoom do navegador em 125% no Supabase para os professores conseguirem ler os resultados do fundo da sala.",
    ]:
        add_p(doc, chk, size=9.5, space_after=2.5)

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DOCX))
    print("GUIA_DOCX_SAVED:", OUT_DOCX)


if __name__ == "__main__":
    build_guide()
