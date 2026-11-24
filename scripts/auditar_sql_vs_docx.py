import re
import sys
from pathlib import Path
from docx import Document

ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "02_sql" / "00_ddl_completo_do_zero.sql"
DBML_PATH = ROOT / "01_modelagem" / "der_logico.dbml"
DOCX_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else (ROOT / "04_entrega_final" / "01_Dicionario_de_Dados_A3_EEB_Benonivio.docx")


def parse_sql(sql_text: str):
    enums = {}
    for m in re.finditer(r"CREATE TYPE public\.(\w+) AS ENUM \(([^)]+)\);", sql_text):
        vals = [v.strip().strip("'") for v in m.group(2).split(",")]
        enums[m.group(1)] = vals

    views = re.findall(r"CREATE OR REPLACE VIEW public\.(\w+)", sql_text)

    tables = {}
    fks = []
    tbl_pattern = re.compile(r"CREATE TABLE public\.(\w+)\s*\((.*?)\n\);", re.DOTALL)
    for m in tbl_pattern.finditer(sql_text):
        tname = m.group(1)
        body = m.group(2)
        cols = {}
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("--"):
                continue
            if line.startswith("CONSTRAINT"):
                break
            line_no_comma = line.rstrip(",")
            parts = line_no_comma.split()
            cname = parts[0]
            rest = " ".join(parts[1:])
            is_nn = "NOT NULL" in rest or "PRIMARY KEY" in rest
            # Normalizar tipo base
            if rest.startswith("uuid"):
                ctype = "uuid"
            elif rest.startswith("text"):
                ctype = "text"
            elif rest.startswith("integer"):
                ctype = "integer"
            elif rest.startswith("bigint"):
                ctype = "bigint"
            elif rest.startswith("boolean"):
                ctype = "boolean"
            elif rest.startswith("timestamptz"):
                ctype = "timestamptz"
            elif rest.startswith("date"):
                ctype = "date"
            elif rest.startswith("public."):
                ctype = rest.split()[0].replace("public.", "")
            else:
                ctype = parts[1]
            cols[cname] = {"type": ctype, "not_null": is_nn}

            fk_m = re.search(r"REFERENCES public\.(\w+)\((\w+)\)\s+ON DELETE\s+(SET NULL|CASCADE|RESTRICT|NO ACTION)", rest)
            if fk_m:
                fks.append((tname, fk_m.group(1), cname, fk_m.group(3)))

        tables[tname] = cols

    return enums, views, tables, fks


def parse_dbml(dbml_text: str):
    enums = {}
    for m in re.finditer(r"Enum (\w+)\s*\{([^}]+)\}", dbml_text):
        vals = [ln.strip() for ln in m.group(2).splitlines() if ln.strip() and not ln.strip().startswith("//")]
        enums[m.group(1)] = vals

    tables = {}
    for m in re.finditer(r"Table (\w+)\s*\{(.*?)\n\}", dbml_text, re.DOTALL):
        tname = m.group(1)
        cols = {}
        in_indexes = False
        for raw_ln in m.group(2).splitlines():
            ln = raw_ln.strip()
            if not ln or ln.startswith("//") or ln.startswith("Note:"):
                continue
            if ln.startswith("Indexes"):
                in_indexes = True
                continue
            if in_indexes:
                if ln == "}":
                    in_indexes = False
                continue
            parts = ln.split()
            cname = parts[0]
            ctype = parts[1]
            cols[cname] = ctype
        tables[tname] = cols

    refs = []
    for m in re.finditer(r"Ref:\s*(\w+)\.(\w+)\s*[>-]\s*(\w+)\.(\w+)\s*\[delete:\s*(set null|cascade|restrict)\]", dbml_text):
        refs.append((m.group(1), m.group(3), m.group(2), m.group(5).upper()))

    return enums, tables, refs


def map_docx_type(docx_type: str):
    t = docx_type.lower()
    if "uuid" in t:
        return "uuid"
    if "texto" in t:
        return "text"
    if "int4" in t or "inteiro" in t or t.startswith("número (int4"):
        return "integer"
    if "int8" in t or "bigint" in t:
        return "bigint"
    if "boolean" in t:
        return "boolean"
    if "data/hora" in t or "timestamptz" in t:
        return "timestamptz"
    if t == "data":
        return "date"
    if "enum" in t:
        return "enum"
    return t


def audit():
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    dbml_text = DBML_PATH.read_text(encoding="utf-8")
    doc = Document(str(DOCX_PATH))

    sql_enums, sql_views, sql_tables, sql_fks = parse_sql(sql_text)
    dbml_enums, dbml_tables, dbml_refs = parse_dbml(dbml_text)

    errors = []

    # 1. Conferencia de professores no DOCX
    full_doc_text = "\n".join(p.text for p in doc.paragraphs)
    for prof in ["Fernando Costa Leite", "Henrique Pereira Oliveira D'Eça Neves"]:
        if prof not in full_doc_text:
            errors.append(f"DOCX sem professor obrigatorio: {prof}")

    # 2. SQL vs DBML
    if set(sql_enums.keys()) != set(dbml_enums.keys()):
        errors.append(f"ENUMs divergem SQL vs DBML: {set(sql_enums) ^ set(dbml_enums)}")
    else:
        for ek, ev in sql_enums.items():
            if ev != dbml_enums[ek]:
                errors.append(f"Valores do ENUM {ek} divergem SQL vs DBML: {ev} vs {dbml_enums[ek]}")

    if set(sql_tables.keys()) != set(dbml_tables.keys()):
        errors.append(f"Tabelas divergem SQL vs DBML: {set(sql_tables) ^ set(dbml_tables)}")
    else:
        for tname, cols in sql_tables.items():
            if set(cols.keys()) != set(dbml_tables[tname].keys()):
                errors.append(f"Colunas de {tname} divergem SQL vs DBML: {set(cols) ^ set(dbml_tables[tname])}")

    if set(sql_fks) != set(dbml_refs):
        errors.append(f"FKs divergem SQL vs DBML: {set(sql_fks) ^ set(dbml_refs)}")

    # 3. SQL vs DOCX (identificar cada tabela de 6 colunas pelo titulo anterior)
    table_headings = []
    for p in doc.paragraphs:
        m = re.match(r"4\.\d+\.\s+Tabela\s+(escola_\w+)", p.text.strip())
        if m:
            table_headings.append(m.group(1))

    if set(table_headings) != set(sql_tables.keys()):
        errors.append(f"Titulos 4.x no DOCX divergem do SQL: {set(table_headings) ^ set(sql_tables)}")

    six_col_tables = []
    enum_table = None
    fk_table = None
    view_tables = []
    for tbl in doc.tables:
        hdr = [c.text.strip() for c in tbl.rows[0].cells]
        if hdr == ["Nome", "Tipo", "Classe", "Tamanho", "Descrição", "Observação"]:
            six_col_tables.append(tbl)
        elif hdr == ["Tipo ENUM (public)", "Valores Permitidos", "Tabelas que Utilizam"]:
            enum_table = tbl
        elif hdr == ["Tabela Origem", "Tabela Destino", "Coluna (FK)", "Cardinalidade", "Política ON DELETE"]:
            fk_table = tbl
        elif hdr == ["Coluna", "Tipo", "Descrição"]:
            view_tables.append(tbl)

    if len(six_col_tables) != 15:
        errors.append(f"Esperadas 15 tabelas de 6 colunas no DOCX, encontradas {len(six_col_tables)}")
    else:
        for tname, tbl in zip(table_headings, six_col_tables):
            sql_cols = sql_tables[tname]
            docx_cols = {}
            for row in tbl.rows[1:]:
                cname = row.cells[0].text.strip()
                ctype = map_docx_type(row.cells[1].text.strip())
                obs = row.cells[5].text.strip()
                is_nn = "NN" in obs
                docx_cols[cname] = {"type": ctype, "not_null": is_nn, "raw_obs": obs}

            if set(sql_cols.keys()) != set(docx_cols.keys()):
                errors.append(f"DOCX {tname}: colunas divergem do SQL: {set(sql_cols) ^ set(docx_cols)}")
                continue
            for cname, sc in sql_cols.items():
                dc = docx_cols[cname]
                expected_t = "enum" if sc["type"].endswith("_enum") else sc["type"]
                if dc["type"] != expected_t:
                    errors.append(f"DOCX {tname}.{cname}: tipo {dc['type']} != {expected_t}")
                if dc["not_null"] != sc["not_null"]:
                    errors.append(f"DOCX {tname}.{cname}: NN={dc['not_null']} != SQL NN={sc['not_null']}")

    # Views no DOCX
    for v in sql_views:
        if v not in full_doc_text:
            errors.append(f"View {v} ausente no DOCX")
    if len(view_tables) != 2:
        errors.append(f"Esperadas 2 tabelas de Views no DOCX, encontradas {len(view_tables)}")

    # ENUMs no DOCX
    if enum_table is None:
        errors.append("Tabela resumo de ENUMs ausente no DOCX")
    else:
        docx_enums = {}
        for row in enum_table.rows[1:]:
            ename = row.cells[0].text.strip()
            evals = [x.strip() for x in row.cells[1].text.split(",")]
            docx_enums[ename] = evals
        if docx_enums != sql_enums:
            errors.append(f"ENUMs no DOCX divergem do SQL: {docx_enums} vs {sql_enums}")

    # 13 FKs no DOCX
    if fk_table is None:
        errors.append("Tabela resumo de 13 FKs ausente no DOCX")
    else:
        docx_fks = set()
        for row in fk_table.rows[1:]:
            orig = row.cells[0].text.strip()
            dest = row.cells[1].text.strip()
            col = row.cells[2].text.strip().split("→")[0].strip()
            on_del = row.cells[4].text.strip().upper()
            docx_fks.add((orig, dest, col, on_del))
        if docx_fks != set(sql_fks):
            errors.append(f"FKs no DOCX divergem do SQL: {docx_fks ^ set(sql_fks)}")

    print(f"AUDIT_SUMMARY: tables={len(sql_tables)}, enums={len(sql_enums)}, views={len(sql_views)}, fks={len(sql_fks)}")
    if errors:
        print("DIVERGENCIAS_ENCONTRADAS:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("DIVERGENCIAS: 0 (100% SINCRONIZADO ENTRE SQL, DBML E DOCX)")


if __name__ == "__main__":
    audit()
