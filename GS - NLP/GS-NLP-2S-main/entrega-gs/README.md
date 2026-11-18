# GS 2027 — Fábrica de Corpus CitizenTech (Código de Defesa do Consumidor)

Notebook do Google Colab que transforma documentos públicos sobre direitos do consumidor em quatro
corpus em JSONL para o fine-tuning de um modelo de linguagem pequeno (SLM) de atendimento ao cidadão.

**Integrantes**

- Igor Paixão Sarak — RM 563726
- Lucca Phelipe Masini — RM 564121
- Bernardo Braga Perobeli — RM 562468

## Persona e cenário de uso simulado

O atendimento simulado é o de um consumidor com **pouca escolaridade**, que escreve pelo celular, usa
gíria e não conhece os termos da lei. Para testar a capacidade do modelo nesse cenário do dia a dia,
as perguntas dos corpus foram escritas **de propósito com jargões, linguagem informal e erros de
português** (por exemplo: «aff», «mano», «q», «oq», «help», palavras em caixa-alta, letras trocadas
como «deovlve», «psoso», «precsio», e pontuação exagerada, como «??»).

- Pelo menos 30% das perguntas de cada corpus têm essa «língua real» (medido no relatório de qualidade).
- As respostas, ao contrário, ficam em português simples, correto e acolhedor, sem juridiquês.
- O conjunto de teste inclui perguntas diretas, «pegadinhas», assuntos fora do tema e casos de urgência
  (risco à vida ou à saúde, em que o modelo deve mandar ligar para o 192 ou 193).
- O corpus de chat inclui diálogos de 2 turnos em que a segunda pergunta depende da primeira, e recusas
  ou encaminhamentos (fora do tema, orientação individual, urgência).

Esse cenário é uma simulação feita pelo grupo (com apoio de um modelo aberto para gerar variações),
não dados de pessoas reais. ODS 16 (paz, justiça e instituições eficazes), metas 16.3 e 16.6.

## Fontes

| Documento | Órgão | Volátil? |
|---|---|---|
| Lei nº 8.078/1990 — Código de Defesa do Consumidor | Presidência da República | parcial (art. 57, MP 1.393/2026) |
| Lei nº 14.181/2021 — Superendividamento | Presidência da República | não |
| Decreto nº 13.135/2026 — SAC | Presidência da República | sim |
| Decreto nº 7.962/2013 — Comércio eletrônico | Presidência da República | não |
| Guia do Consumidor para a Black Friday (2024) | Senacon / Ministério da Justiça | sim |
| Ficha de atendimento fictícia | fictício (teste de anonimização) | n/a |

Fatos que mudam (prazos, valores, multas) **não** entram como resposta decorada nos corpus de QA e
chat: ficam no corpus de texto, para o RAG. Os links e as datas de acesso estão em
`metadados_documentos.json`.

## Como executar

1. Abra `GS_NLP_CitizenTech.ipynb` no Google Colab.
2. Menu *Ambiente de execução → Alterar tipo de ambiente de execução → **T4 GPU***.
3. *Executar tudo*. Não precisa de chave de API: os documentos são baixados de uma pasta pública e o
   modelo (Qwen2.5-7B-Instruct, aberto, em 4 bits) vem do Hugging Face Hub. Duração: de 60 a 90 minutos,
   quase toda na geração (seções 9 e 10).
4. A pasta de saída é `/content/gs_nlp/saida`; a última célula gera o zip para baixar.

O notebook entregue já está executado, com as saídas visíveis.

### Bibliotecas

`pypdf`, `python-docx`, `beautifulsoup4`, `lxml`, `ftfy`, `gdown`, `spacy` (`pt_core_news_lg`),
`sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), `transformers`, `accelerate`,
`bitsandbytes`. Contagem de tokens com o tokenizador do modelo Qwen2.5 de 0,5 bilhão de parâmetros.

## Etapas do pipeline

Ingestão (PDF, HTML, DOCX, TXT e texto colado) → extração → limpeza → normalização → anonimização
(spaCy + regex, com tabela antes/depois) → segmentação em trechos de 256 a 512 tokens → geração dos
corpus → filtros e juízes automáticos → conferência final → relatório de qualidade.

## Arquivos de saída

| Arquivo | Conteúdo | Quantidade final |
|---|---|---|
| `corpus_texto.jsonl` | trechos limpos, com fonte e seção (base do RAG) | 68 |
| `corpus_qa.jsonl` | pares pergunta/resposta com o trecho de apoio | 112 |
| `corpus_chat.jsonl` | diálogos de 2 turnos (14 escritos à mão, 19 gerados) | 33 (12 recusas ou encaminhamentos) |
| `corpus_teste.jsonl` | perguntas de teste fora do treino | 24 |
| `revisao.csv` | registro da revisão humana (arquivo, linha, alterado, comentário) | ver abaixo |
| `amostra_fidelidade.csv` | 20 pares conferidos à mão | 13 de 20 fiéis |
| `relatorio_qualidade.json` | estatísticas, filtros, similaridade, língua real | — |
| `anonimizacao_antes_depois.txt` | exemplos de anonimização | — |

As quantidades são as do corpus **depois** da revisão humana (os originais da geração ficam em
`*.original.jsonl`; o `relatorio_qualidade.json` descreve a geração, antes da revisão).

## Revisão humana

O grupo revisou todos os 126 pares de QA e os 22 diálogos gerados (os 14 escritos à mão foram lidos
em conjunto), usando as planilhas de apoio convertidas em texto para leitura (`REVISAO_QA.md`,
`REVISAO_CHAT.md`, `REVISAO_FIDELIDADE.md`) e os scripts `scripts/revisao_md.py` e
`scripts/aplicar_revisao.py`.

- QA: 126 → 112 pares (14 excluídos, 15 corrigidos).
- Chat: 22 diálogos gerados revisados (3 excluídos, 9 corrigidos); total 36 → 33.
- Fidelidade, antes da revisão: 13 de 20 (65%) dos pares da amostra tinham a resposta sustentada pelo
  trecho. Os 7 reprovados (respostas vagas ou sem relação com a pergunta) foram excluídos ou corrigidos.

Principais defeitos encontrados na geração automática: pergunta e resposta que não combinam, resposta
mais ampla que o trecho, valores e prazos que mudam (R$, BTN, horas) e órgãos inexistentes no chat.

## Limitações

- Os pares e diálogos gerados por um modelo de 7 bilhões de parâmetros precisam de revisão humana;
  os juízes automáticos aprovam alguns pares ruins.
- Os corpus não ensinam valores e prazos que mudam; o modelo deve consultar o RAG ou orientar a
  confirmar no Procon ou no consumidor.gov.br.
- O corpus de teste é pequeno (24 perguntas) e serve de verificação, não de benchmark.
- Fora do escopo: ajuste fino com LoRA (bônus não realizado).

## Privacidade (LGPD)

Os documentos de origem são públicos. A anonimização remove CPF, e-mail, telefone e nomes de pessoas
(os documentos de teste são fictícios, com dados sintéticos). A conferência final confirma que não há
CPF, e-mail nem telefone nos corpus.

## Estrutura da entrega

- `GS_NLP_CitizenTech.ipynb`: o notebook entregue, já executado.
- `relatorio_GS_NLP_CitizenTech.pdf`: relatório (até 6 páginas).
- `saida/`: corpus finais, `revisao.csv`, `amostra_fidelidade.csv`, relatório de qualidade, os corpus originais da geração
  (`*.original.jsonl`) e os arquivos de apoio da revisão.
- `docs_entrada/`: documentos de entrada (`drive/` são os arquivos usados, com o documento-teste fictício) e `metadados_documentos.json`
  em `saida/`.
- `scripts/`: `revisao_md.py` converte as planilhas de revisão em texto e de volta; `aplicar_revisao.py` aplica a revisão aos corpus.
