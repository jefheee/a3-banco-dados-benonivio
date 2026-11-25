# Portal Escolar EEB Prof. Benonívio João Martins — Modelagem e Reconstrução Relacional (A3)

O Portal Escolar da Escola de Educação Básica Professor Benonívio João Martins (Palhoça – SC) é um sistema real publicado em produção ([https://escolabenonivio.vercel.app/](https://escolabenonivio.vercel.app/)), com código-fonte original em [https://github.com/jefheee/escola-benonivio](https://github.com/jefheee/escola-benonivio), desenvolvido em Next.js com PostgreSQL na plataforma Supabase.

Na primeira versão colocada no ar, o banco contava com 9 tabelas, guardava galerias de fotos e links dentro de campos `JSONB`, não separava o histórico de turmas por ano letivo e repetia o campo de turno nos grupos de WhatsApp. Na Avaliação A3 da Unidade Curricular de Banco de Dados (UNISUL — Campus Pedra Branca, 2026), reconstruímos o banco do zero de forma estruturada e normalizada até a 3FN para garantir integridade e preservar o histórico escolar ano após ano.

---

## Resumo da Evolução: Antes vs. Depois

| Aspecto | Versão Inicial (Produção) | Nova Estrutura (Avaliação A3) |
|---|---|---|
| Estrutura das tabelas | 9 tabelas com listas em `JSONB` | 15 tabelas normalizadas (1FN, 2FN e 3FN) |
| Domínios padronizados | Textos livres sem validação | 5 tipos `ENUM` (`turno`, `status`, `publicacao_status`, `importancia`, `usuario_role`) |
| Relacionamentos | Vínculos parciais sem regra padrão | 13 chaves estrangeiras (`ON DELETE CASCADE` e `ON DELETE SET NULL`) |
| Histórico escolar | Turmas sobrescritas na virada do ano | Separação por `ano_letivo` com chave única `(ano_letivo, ano, nome, turno)` |
| Dados repetidos | Turno duplicado em grupos de WhatsApp | Turno único em `escola_turmas` (3FN), consultado via `JOIN` |
| Validações | Regras concentradas apenas no site | Restrições `UNIQUE`, `CHECK` de datas, e-mail, slug e textos não vazios no banco |
| Exposição pública | Consultas diretas sem filtro central | 2 Views públicas (`escola_avisos_publicos` e `escola_eventos_publicos`) e controle de acesso por perfil |

---

## Diagramas de Modelagem

### Modelo Conceitual

![Modelo Conceitual](01_modelagem/der_conceitual.png)

### Modelo Lógico (15 Tabelas, 5 ENUMs e 13 Chaves Estrangeiras)

![Modelo Lógico](01_modelagem/der_logico_dbdiagram.png)

---

## Estrutura do Repositório

```text
a3-banco-dados-benonivio/
├── 00_docs_originais/                          # Documentos base iniciais da equipe
├── 01_modelagem/                               # DBML, Mermaid, HTML interativo, PNGs e Dicionário editável (.docx/.pdf)
├── 02_sql/                                     # Scripts SQL originais e relatório de validação
├── 03_apresentacao/                            # Slides (.pptx/.pdf) e Guia exclusivo de estudo da equipe (uso interno)
├── 04_entrega_final/                           # Pasta limpa exclusiva para entrega aos professores
│   ├── Dicionario_de_Dados_Portal_Escolar_A3.pdf
│   ├── Apresentacao_Portal_Escolar_A3.pdf
│   ├── Apresentacao_Portal_Escolar_A3.pptx
│   ├── Scripts_SQL_Portal_Escolar_A3.zip       # Pacote ZIP pronto para envio por e-mail
│   ├── Scripts_SQL/
│   │   ├── 01_criacao_banco_ddl.sql
│   │   ├── 02_dados_exemplo_seed.sql
│   │   ├── 03_testes_integridade.sql
│   │   └── 04_consultas_demonstracao.sql
│   └── Diagramas/
│       ├── der_conceitual.png
│       ├── der_logico_dbdiagram.png
│       └── der_logico.dbml
├── scripts/                                    # Scripts locais de geração, auditoria e exportação PDF
├── .gitignore
└── README.md
```

---

## Como Reproduzir do Zero no PostgreSQL / Supabase

Execute os 4 scripts da pasta `04_entrega_final/Scripts_SQL/` nesta ordem em um schema `public` limpo:

1. **`01_criacao_banco_ddl.sql`** — Cria os 5 ENUMs, as 15 tabelas normalizadas, chaves, validações, índices, triggers de atualização, as 2 Views públicas e as políticas de controle de acesso por perfil.
2. **`02_dados_exemplo_seed.sql`** — Popula 102 registros realistas distribuídos entre os anos letivos de 2025 e 2026.
3. **`03_testes_integridade.sql`** — Contém 6 blocos de teste isolados (`BEGIN; ... ROLLBACK;`) comprovando o bloqueio de duplicidades, datas inválidas, textos vazios e referências inexistentes.
4. **`04_consultas_demonstracao.sql`** — Executa 8 consultas SQL demonstrando `JOIN` em 3FN, `COUNT`/`SUM`/`AVG`/`MIN`/`MAX`, `GROUP BY` + `HAVING`, `LEFT JOIN` + `COALESCE`, `NOT EXISTS`, comparativo histórico 2025 vs. 2026 e leitura via Views públicas.

---

## Créditos Acadêmicos

- **Instituição:** Universidade do Sul de Santa Catarina – UNISUL | Campus Pedra Branca
- **Curso:** Análise e Desenvolvimento de Sistemas
- **Unidade Curricular:** Banco de Dados (Avaliação A3) — Palhoça - SC, 2026
- **Professores:** Fernando Costa Leite e Henrique Pereira Oliveira D'Eça Neves
- **Integrantes (ordem alfabética):**
  - Daniel Alves — RA: 1072517730
  - Gabriel Grando — RA: 10725118226
  - Jefherson Luiz — RA: 10725114819
  - Maicon Lodetti — RA: 1072511629
- **Portal em produção:** [https://escolabenonivio.vercel.app/](https://escolabenonivio.vercel.app/)
- **Repositório original do site:** [https://github.com/jefheee/escola-benonivio](https://github.com/jefheee/escola-benonivio)
