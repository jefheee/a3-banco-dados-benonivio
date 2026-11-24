Todas as correções editoriais, visuais e de validação local foram concluídas e sincronizadas com [04_entrega_final/](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final) (sem qualquer alteração no Supabase).

### 1. DER Conceitual (`01_modelagem/der_conceitual.*`)
- **Cardinalidades corrigidas** em [der_conceitual.mmd](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/der_conceitual.mmd) e [visualizador_diagramas.html](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/visualizador_diagramas.html):
  - `|o--o{` nas 6 associações de `USUARIO` (`ACERVO`, `DOCUMENTO`, `EVENTO`, `PAGINA_INSTITUCIONAL`, `AVISO`, `POST_TURMA`), refletindo `autor_id` anulável com `ON DELETE SET NULL`.
  - `}o--o{` entre `EVENTO` e `TURMA`.
- **Padronização visual** via `theme: 'base'` + [mermaid_conceitual.css](file:///c:/Projetos/a3-banco-dados-benonivio/scripts/mermaid_conceitual.css): cabeçalhos em azul-marinho (`#1E3A8A`) com texto branco sem cortes (`foreignObject { overflow: visible }`), linhas alternadas em `#FFFFFF` / `#F8FAFC` com texto `#0F172A`, linhas `#334155` e círculos de opcionalidade vazados (`#FFFFFF`).
- PNG re-renderizado em alta resolução e validado visualmente em [der_conceitual.png](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/der_conceitual.png).

### 2. DBML com Zero Avisos (`01_modelagem/der_logico.dbml`)
- As 6 chaves estrangeiras anuláveis de autoria (`autor_id` com `[delete: set null]`) em [der_logico.dbml](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/der_logico.dbml) foram ajustadas para o operador opcional `>?` (`many-to-0..1`), mantendo o parser do auditor atualizado em [auditar_sql_vs_docx.py](file:///c:/Projetos/a3-banco-dados-benonivio/scripts/auditar_sql_vs_docx.py).
- **Validação `@dbml/parse`:** `parseFile`, `validateFile` e `interpretFile` retornaram **`errors=0, warnings=0, infos=0`** (`tables=15, enums=5, refs=13`).

### 3. Dicionário de Dados (`DOCX` + `PDF`)
- Atualizado em [gerar_dicionario_a3.py](file:///c:/Projetos/a3-banco-dados-benonivio/scripts/gerar_dicionario_a3.py) e exportado para [Dicionario_de_Dados_A3_FINAL.pdf](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/Dicionario_de_Dados_A3_FINAL.pdf) e [01_Dicionario_de_Dados_A3_EEB_Benonivio.pdf](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/01_Dicionario_de_Dados_A3_EEB_Benonivio.pdf) (`19` páginas):
  - Coluna `Tam.` com larguras `[2.8, 2.3, 2.5, 1.3, 5.2, 2.4]` cm, `keep_with_next = True` no cabeçalho das tabelas e Seção 7 com cardinalidades corrigidas (`N:0..1 (Opcional)`, `N:1 (Composição)`, `1:1 (UNIQUE)`, `N:1 (Associativa N:N)`).
  - **Conferência 100% do Sumário via `pypdf`:**

| Seção | Página no Sumário | Página Real no PDF |
|---|---|---|
| `1. INTRODUÇÃO` | 4 | 4 |
| `2. OBJETIVOS E EVOLUÇÃO DO MODELO` | 4 | 4 |
| `3. REGRAS DE NEGÓCIO E NORMALIZAÇÃO (1FN, 2FN E 3FN)` | 4 | 4 |
| `4. DICIONÁRIO DE DADOS DAS 15 TABELAS` | 5 | 5 |
| `5. VIEWS PÚBLICAS` | 13 | 13 |
| `6. TIPOS ENUMERADOS (5 ENUMs)` | 14 | 14 |
| `7. RESUMO DOS RELACIONAMENTOS (13 CHAVES ESTRANGEIRAS)` | 14 | 14 |
| `8. DIAGRAMA CONCEITUAL` | 16 | 16 |
| `9. DIAGRAMA LÓGICO / FÍSICO` | 17 | 17 |
| `10. EVIDÊNCIAS DE VALIDAÇÃO EM BANCO` | 18 | 18 |
| `11. CONSIDERAÇÕES FINAIS E REFERÊNCIAS` | 19 | 19 |

### 4. Apresentação (`PPTX` + `PDF`) & Limpeza
- [gerar_apresentacao_a3.py](file:///c:/Projetos/a3-banco-dados-benonivio/scripts/gerar_apresentacao_a3.py) regenerou [Apresentacao_A3_Portal_Escolar.pptx](file:///c:/Projetos/a3-banco-dados-benonivio/03_apresentacao/Apresentacao_A3_Portal_Escolar.pptx) e [Apresentacao_A3_Portal_Escolar.pdf](file:///c:/Projetos/a3-banco-dados-benonivio/03_apresentacao/Apresentacao_A3_Portal_Escolar.pdf).
- Inspeção visual confirmada nos slides renderizados: Slide 3 (`"Políticas heterogêneas sem controle por papel (role)"`), Slide 6 (`"Trigger única de updated_at com search_path = ''."`) e Slide 10 (`"Obrigado! | Daniel Alves, Gabriel Grando, Jefherson Luiz e Maicon Lodetti"` com ambos os professores abaixo). Os PNGs temporários e SVGs de teste foram removidos.
- `dbml-error.log` foi removido da raiz do projeto (`*.log` permanece em [.gitignore](file:///c:/Projetos/a3-banco-dados-benonivio/.gitignore)).

### 5. Auditoria Final e Inventário em `04_entrega_final/`
- `python scripts/auditar_sql_vs_docx.py 01_modelagem/Dicionario_de_Dados_A3_FINAL.docx`: `AUDIT_SUMMARY: tables=15, enums=5, views=2, fks=13` — **`DIVERGENCIAS: 0`**.
- `python scripts/auditar_sql_vs_docx.py 04_entrega_final/01_Dicionario_de_Dados_A3_EEB_Benonivio.docx`: `AUDIT_SUMMARY: tables=15, enums=5, views=2, fks=13` — **`DIVERGENCIAS: 0`**.
- Hash de [01_modelagem/der_logico.dbml](file:///c:/Projetos/a3-banco-dados-benonivio/01_modelagem/der_logico.dbml) idêntico ao de [04_entrega_final/04_Diagramas/der_logico.dbml](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/04_Diagramas/der_logico.dbml).
- Arquivos ativos em `04_entrega_final/`:
  - [01_Dicionario_de_Dados_A3_EEB_Benonivio.docx](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/01_Dicionario_de_Dados_A3_EEB_Benonivio.docx) e [01_Dicionario_de_Dados_A3_EEB_Benonivio.pdf](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/01_Dicionario_de_Dados_A3_EEB_Benonivio.pdf)
  - [02_Apresentacao_A3_Portal_Escolar.pptx](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/02_Apresentacao_A3_Portal_Escolar.pptx) e [02_Apresentacao_A3_Portal_Escolar.pdf](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/02_Apresentacao_A3_Portal_Escolar.pdf)
  - `03_SQL_Entrega/`: [00_ddl_completo_do_zero.sql](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/03_SQL_Entrega/00_ddl_completo_do_zero.sql), [04_seed_escola_benonivio.sql](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/03_SQL_Entrega/04_seed_escola_benonivio.sql), [05_crash_test_integridade.sql](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/03_SQL_Entrega/05_crash_test_integridade.sql), [06_consultas_apresentacao.sql](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/03_SQL_Entrega/06_consultas_apresentacao.sql)
  - `04_Diagramas/`: [der_conceitual.png](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/04_Diagramas/der_conceitual.png), [der_logico.dbml](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/04_Diagramas/der_logico.dbml), [der_logico.png](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/04_Diagramas/der_logico.png), [der_logico_dbdiagram.png](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/04_Diagramas/der_logico_dbdiagram.png)
  - `05_Roteiro_Equipe/`: [ROTEIRO_APRESENTACAO_EQUIPE.md](file:///c:/Projetos/a3-banco-dados-benonivio/04_entrega_final/05_Roteiro_Equipe/ROTEIRO_APRESENTACAO_EQUIPE.md)