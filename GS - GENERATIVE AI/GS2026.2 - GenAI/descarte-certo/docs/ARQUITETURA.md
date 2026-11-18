# Arquitetura e decisões

## Problema e escopo

O cidadão encontra informações de descarte distribuídas entre páginas municipais, com diferenças entre serviços, exceções por unidade e limites divergentes. O Descarte Certo reúne seis sínteses identificáveis e responde com evidências sobre o município de São Paulo.

## Fluxo

~~~mermaid
flowchart TD
    A[Pergunta e histórico] --> B[Validação e proteção local]
    B --> M{Resposta aprovada em cache?}
    M -->|Não| C[BM25: até 12 candidatos]
    M -->|Sim| L
    D[Seis fontes municipais] --> E[Chunks de até 90 palavras]
    E --> C
    C --> F[Jev: relevância e injeção]
    F --> G[Até seis evidências]
    G --> H[Jev: escopo, ambiguidade e suficiência]
    H --> I[OpenAI: afirmações com IDs]
    I --> J[Validação estrutural]
    J --> K[Jev: sustentação e pertinência do material]
    K --> L[Resposta citada, esclarecimento ou abstenção]
~~~

O fluxo admite uma correção após rejeição. Uma resposta parcialmente aprovada só é exibida quando a verificação de cobertura preserva os fatos e as ressalvas essenciais. Falhas de provedor produzem indisponibilidade, distinta de ausência de evidência.

## Reutilização de respostas

Após a proteção local, o cache procura igualdade exata de pergunta, histórico, corpus, prompt e configuração por SHA-256. Somente respostas aprovadas pelo fluxo completo são armazenadas, com suas citações. A validade é de cinco minutos, sem renovação na leitura, e a capacidade é de 128 respostas. Alterações nas entradas invalidam a chave; o reinício elimina o cache. Abstenções, esclarecimentos e erros continuam no fluxo normal.

O armazenamento é exclusivamente em memória e não contém a pergunta como chave legível nem credenciais. Os textos das respostas podem refletir a consulta. As avaliações de qualidade desativam o cache; o experimento de otimização distingue primeira consulta e repetição.

## Segmentação

A configuração utiliza até 90 palavras por trecho, sobreposição de 15, agrupamento por parágrafos e janelas para parágrafos maiores. Palavras permitem reprodução sem tokenizador; não equivalem a tokens. A sobreposição pode iniciar no meio de uma frase, portanto o contexto precisa preservar a evidência principal.

Cada trecho mantém ID, fonte, título, URL, escopo, datas e SHA-256. O hash registra integridade, sem certificar veracidade. A comparação de 45/8, 90/15 e 160/20 consta da avaliação de recuperação. A configuração intermediária limita contexto e fragmentação, sem pretensão de superioridade universal.

## Recuperação e decisões

A busca BM25 utiliza normalização de acentos, palavras funcionais, singularização simples, k1=1,5, b=0,75 e até 12 candidatos. Jev seleciona até seis trechos com relevância ≥0,35 e risco de injeção <0,70. O limiar de suficiência/cobertura é 0,75; o de sustentação é 0,80. Esses escores não são probabilidades calibradas de correção.

Jev opera depois do chunking e da busca. Uma fonte ausente dos candidatos permanece inacessível ao seletor. O fluxo público dispensa embeddings porque o corpus é pequeno; o comparativo experimental inclui busca vetorial e híbrida para medir essa escolha. A arquitetura pública continua com Jev obrigatório.

O modelo jev-1.14.0 utiliza a API System One da TypeSafe. Cada questão noul referencia explicitamente um trecho ou uma afirmação. Valores ausentes, não numéricos, infinitos ou fora de [0,1] são rejeitados.

## Geração e verificação

A Responses API utiliza gpt-5.4-mini-2026-03-17, store=false, raciocínio low, orçamento de 4.000 tokens e JSON Schema estrito. A saída admite até três afirmações de 70 palavras, em português-BR e terceira pessoa ou construção impessoal. O prompt completo consta de descarte/provedores.py. URLs são associadas pelo código a IDs existentes.

A sustentação de fatos exige as fontes citadas. Declarações sobre limites do conhecimento consideram todo o contexto: a confirmação de Berrini não prova rejeição nas demais unidades de Pinheiros. Uma decisão adicional detecta justificativas sobre outro material, com rejeição a partir de 0,50. Comparar limites diferentes do mesmo material não caracteriza desvio.

Divergências publicadas sobre entulho são apresentadas explicitamente, sem equivalência automática ou garantia universal. Quando apenas a impossibilidade de generalização permanece, uma decisão de cobertura pode autorizar o fato confirmado acompanhado de ressalva controlada. Conflitos numéricos ou dados solicitados não podem ser omitidos por essa alternativa.

O código valida IDs, tamanho e alfabeto latino. Essas verificações não certificam gramática nem correção factual. Abstenções utilizam mensagens controladas. O modelo foi escolhido pela saída estruturada e pelas respostas curtas; não houve comparação entre geradores que demonstrasse superioridade de qualidade ou custo.

## Fontes e segurança

O corpus contém sínteses editoriais de páginas oficiais, com datas e escopos preservados. Limites divergentes permanecem identificados. Horários publicados não demonstram funcionamento ao vivo. Atualizações exigem revisão das fontes, versionamento e reavaliação.

Credenciais são lidas no backend. A operação normal não grava perguntas; os registros de avaliação contêm casos artificiais. A interface usa textContent, restringe links ao domínio municipal e aplica CSP. O servidor valida origem e Host, limita corpo, concorrência e frequência, escuta em 127.0.0.1 e usa porta exclusiva no Windows. O endpoint /api/estado expõe somente a configuração pública de disponibilidade e versão.

## Referências

- [API System One — TypeSafe](https://docs.typesafe.ai/api/system-one)
- [GPT-5.4 mini — OpenAI](https://developers.openai.com/api/docs/models/gpt-5.4-mini)
- [Saídas estruturadas — OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Embeddings — OpenAI](https://developers.openai.com/api/docs/guides/embeddings)
- [Fusão recíproca de rankings — Elastic](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

A integração REST permite rastreamento das decisões sem dependências adicionais. Resultados de benchmarks externos não são atribuídos ao protótipo.
