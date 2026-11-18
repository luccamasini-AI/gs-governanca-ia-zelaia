# Relatório de avaliação — Descarte Certo

CitizenTech · Global Solution 2026.2 · Generative AI & Advanced Nets · 2TIAPF  
Lucca Phelipe Masini — RM 564121  
Igor Paixão Sarak — RM 563726  
Bernardo Braga Perobeli — RM 562468  
Versão de prompt: 2026-11-10.18. Avaliação em 10/11/2026.

## Atendimento ao enunciado

O projeto apresenta assistente integrado à aplicação web, corpus identificável, decisões de chunking, recuperação e geração, avaliações por componente e do fluxo completo, dez perguntas representativas, testes adversariais, mecanismos de mitigação, código reproduzível e roteiro para vídeo de até cinco minutos. A gravação com a voz do integrante permanece pendente e não integra o pacote. A [matriz de requisitos](../docs/MATRIZ-REQUISITOS.md) relaciona cada exigência do PDF inicial às evidências da entrega.

## Método

Dez cenários foram executados duas vezes no fluxo completo com Jev, com o cache vazio antes de cada primeira consulta. As vinte execuções iniciais foram extraídas integralmente do experimento de otimização, sem seleção de tentativas favoráveis. Cada consulta recebeu uma repetição imediata, contabilizada separadamente. Dez perguntas adicionais foram executadas duas vezes com cache desativado. O histórico foi fixado em cada cenário.

O conjunto foi reutilizado na depuração e constitui avaliação de regressão, não teste cego. O julgamento editorial foi realizado por agente contra as evidências, sem avaliador humano independente. As repetições verificam estabilidade local. Os registros brutos permanecem separados dos julgamentos.

| Caso | Capacidade avaliada | Comportamento observado | Critério atendido |
|---|---|---|---:|
| R01 | Geladeira em ecoponto | Diferencia ecoponto e Cata-Bagulho | 2/2 |
| R02 | Telhas de amianto | Preserva a restrição nos dois serviços | 2/2 |
| R03 | Caixa de pizza suja de óleo | Não encaminha à coleta seletiva | 2/2 |
| R04 | Vinte sacos de entulho de cinquenta litros | Apresenta os limites divergentes, sem garantia universal | 2/2 |
| R05 | Gesso em Pinheiros e Berrini | Confirma Berrini sem inferir rejeição nas demais unidades | 2/2 |
| R06 | Óleo de cozinha em garrafa | Identifica categorias de pontos participantes | 2/2 |
| R07 | Fila e recebimento neste minuto | Reconhece ausência de informação ao vivo | 2/2 |
| R08 | Material não identificado | Solicita esclarecimento | 2/2 |
| R09 | Regras aplicadas em Santo André | Preserva o escopo municipal | 2/2 |
| R10 | Horário dominical após referência a Teresa Cristina | Resolve o histórico e informa 6h–18h | 2/2 |

## Resultados do fluxo completo

| Medida | Resultado |
|---|---:|
| Estados esperados | 20/20 |
| Critérios editoriais atendidos | 20/20 |
| Respostas substantivas / casos respondíveis | 14/14 |
| Afirmações exibidas / erros factuais identificados | 21/0 |
| Pares com mesmo estado | 10/10 |
| Pares com texto e referências idênticos | 4/10 |
| Cobertura literal esperada antes/depois de Jev | 100%/100% |
| Média de candidatos / trechos selecionados nos casos respondíveis | 10,71/3,14 |
| Latência média / mediana | 2,185 s / 2,418 s |
| P95 pelo posto mais próximo | 3,819 s |
| Chamadas externas nas vinte execuções | 71 |

A taxa observada de afirmações não sustentadas foi 0/21 nessa revisão; não constitui garantia para novas consultas. Algumas respostas repetem fatos ou incluem detalhes sustentados além do necessário. A cobertura literal procura expressões do gabarito nos trechos, inclusive em eventuais abstenções; não equivale a anotação exaustiva de relevância.

Os casos de entulho e gesso atenderam aos critérios nas duas rodadas. Em entulho, a divergência publicada é informação suficiente para explicar os dois limites e recomendar confirmação, sem equivalência automática. Em gesso, a confirmação de Berrini não fundamenta rejeição nas demais unidades. Geração e verificação distinguem limite do conhecimento de negativa factual. Não há respostas fixas para esses cenários nem consulta ao gabarito durante a operação.

Contextos, decisões, respostas e tempos constam de revisao/final/fluxo-repetido.json. Julgamentos, métricas reproduzíveis e manifesto acompanham o arquivo. A otimização reduziu a média de 2,185 s para 0,129 s nas repetições, ganho de 94,1%, com vinte pares de resultados idênticos. O ganho depende de cache válido e não se aplica a perguntas inéditas. A [comparação de desempenho](DESEMPENHO.md) distingue esse resultado do experimento anterior com RAG convencional.

## Controles Jev e segurança

| Controle | Decisões corretas |
|---|---:|
| Sustentação de afirmações | 18/18 |
| Desvio de material | 6/6 |
| Cobertura completa | 6/6 |
| Autorização de resposta parcial com ressalva | 3/4 |
| Total | 33/34 |

O erro ocorreu na primeira rodada do controle C03: uma afirmação que confirma apenas Berrini poderia ser exibida com a ressalva controlada, mas recebeu 0,72, abaixo do limiar de 0,75. A segunda rodada atingiu 0,75 e foi aprovada. Trata-se de um falso negativo conservador. Os limiares foram mantidos; o resultado registra risco de recusa excessiva em novas consultas. R05 do fluxo completo foi aprovado nas duas rodadas.

Dois documentos artificiais com instruções maliciosas foram excluídos nas duas repetições, totalizando 4/4 bloqueios. O ataque direto foi bloqueado antes das APIs nas duas rodadas. Os testes não utilizaram credenciais reais. A proteção de dados pessoais inclui padrões sintéticos nos testes locais, sem promessa de detecção universal.

A seleção Jev isolada não assegura o contrato final: no comparativo, R09 da primeira rodada retornou afirmações junto do estado sem_evidencia. O produto mantém decisões de escopo/suficiência e mensagens controladas, sem exibir afirmações geradas nesses estados. Esse caso documenta uma falha de componente e a função da mitigação aplicada.

## Perguntas adicionais

Dez perguntas distintas das utilizadas na otimização foram definidas antes da execução e repetidas duas vezes, sem cache ou ajuste posterior do gabarito. Foram obtidos 19/20 estados esperados. H02 apresentou uma abstenção desnecessária na primeira rodada: a exigência de sacos transparentes no Cata-Bagulho estava nas fontes, mas recebeu sustentação de 0,73 e 0,74, abaixo do limiar de 0,80, nas duas tentativas. Na segunda rodada, a resposta foi aprovada. Os limiares foram preservados.

Não houve erro factual identificado nas afirmações exibidas. H06 repetiu a mesma informação; H08 manteve abstenção sobre Vila Madalena sem generalizar a aceitação de gesso no Berrini. H09 apresentou os limites divergentes sem garantir aceitação. O resultado evidencia recusa excessiva ocasional e não sustenta alegação de qualidade perfeita. Perguntas, respostas e julgamentos constam de dados/cenarios-adicionais.json e relatorios/adicionais/.

## Avaliação por componente

Os registros por componente pertencem à versão 13. A segmentação, a busca, o gerador e os prompts de decisão permanecem iguais na versão 18; o cache é desativado nessas avaliações. A recuperação foi avaliada em treze perguntas respondíveis, com três configurações:

| Tamanho / sobreposição em palavras | Chunks | Palavras indexadas | Cobertura de fontes | MRR de fontes |
|---|---:|---:|---:|---:|
| 45/8 | 31 | 1.038 | 1,00 | 0,962 |
| 90/15 | 15 | 973 | 1,00 | 0,923 |
| 160/20 | 7 | 858 | 1,00 | 1,000 |

Trechos grandes são favorecidos pela métrica por fonte em um corpus pequeno. A escolha de 90/15 mantém contexto moderado e metadados rastreáveis, sem alegação de superioridade universal. As buscas vetorial e híbrida foram comparadas adicionalmente no experimento de desempenho.

Na geração isolada, treze perguntas receberam documentos de referência completos, selecionados pelo gabarito para excluir erros de recuperação. Foram produzidas treze respostas e 17 afirmações, com IDs válidos e escores de sustentação Jev acima de 0,80. A revisão não identificou erro factual. T07 e T09 incluíram detalhes além da dúvida; T02 poderia explicitar que o horário é publicado.

Nos três casos com contexto insuficiente, houve esclarecimento ou abstenção com afirmações vazias, conforme o contrato. T13 ainda solicitou endereço para verificar itinerário, o que pode sugerir capacidade dinâmica inexistente. O fluxo público controla esse limite antes da geração e utiliza mensagens próprias. O componente gerador não constitui, isoladamente, o produto.

Os resultados e julgamentos por componente estão em revisao/componentes/, com manifestos. A suíte local contém **44 testes aprovados**, incluindo contratos de provedores, contexto, citações, correção, proteção, servidor, métricas, cosseno, fusão de rankings, expiração e invalidação do cache.

## Limitações e melhorias

O corpus contém seis sínteses editoriais municipais, com datas e URLs; não cobre todos os serviços ou endereços e pode ficar desatualizado. As respostas não confirmam operação ao vivo. Os escores Jev não são probabilidades calibradas, e a revisão por agente não substitui validação humana independente.

As melhorias prioritárias são ampliar a avaliação independente, investigar recusas indevidas sem reduzir os limiares apenas para atender ao gabarito, reduzir repetição nas respostas e ampliar o corpus mediante curadoria. A adoção de busca vetorial ou híbrida depende de evidência de ganho de cobertura em consultas novas e de corpus maior; o experimento atual não demonstra necessidade de alterar a arquitetura pública.

Código, dependências, corpus, configuração, testes, instruções, relatórios, registros e roteiro compõem o pacote. A entrega acadêmica ainda depende do vídeo gravado pelo integrante com a própria voz. Os materiais de apresentação utilizam terceira pessoa ou construção impessoal. Entradas adversariais e retornos brutos permanecem literais para preservar a validade da avaliação.
