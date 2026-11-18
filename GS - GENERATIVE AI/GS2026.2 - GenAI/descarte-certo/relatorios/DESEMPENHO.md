# Desempenho — Descarte Certo

A otimização mantém o fluxo completo com Jev e reutiliza somente respostas já aprovadas, por até cinco minutos. A pergunta, o histórico, o corpus, o prompt e a configuração precisam ser idênticos. O cache permanece em memória, limitado a 128 respostas; abstenções e erros não são armazenados.

## Ganho medido

Dez cenários foram executados em duas rodadas. Cada par começou com cache vazio e recebeu uma repetição imediata: 40 execuções, sem exclusão de resultados.

| Medida no backend | Primeira consulta | Repetição |
|---|---:|---:|
| Média dos vinte casos | 2,185 s | 0,129 s |
| Média das quatorze respostas substantivas | 2,938 s | 1,06 ms |
| Chamadas externas | 71 | 12 |
| Estados esperados | 20/20 | 20/20 |

A redução média foi de **94,1% no conjunto repetido**. As quatorze respostas recuperadas do cache dispensaram APIs; os vinte pares preservaram integralmente o resultado. As seis consultas sem resposta substantiva continuaram passando pelo fluxo normal.

O ganho decorre da reutilização exata, sem aceleração comprovada para perguntas inéditas ou para a inferência do Jev. A medição não inclui rede do navegador nem renderização. A vantagem em uso real depende da frequência de repetições com o mesmo histórico. Registros e cálculo reproduzível constam de [otimizacao/](otimizacao/).

## Comparação com RAG convencional

O experimento anterior, versão 13, contém 120 execuções: dez cenários, duas rodadas e seis variantes. Os tempos abaixo pertencem àquela execução, sem o cache local novo.

| Variante | Média |
|---|---:|
| BM25 + geração | 2,368 s |
| Busca vetorial + geração | 3,309 s |
| Busca híbrida + geração | 2,948 s |
| Seleção Jev + geração | 2,580 s |
| Fluxo completo com Jev | 2,234 s |
| Fluxo completo com decisões pelo LLM | 7,676 s |

Jev reduziu a média em **70,9% frente às mesmas decisões realizadas pelo LLM**. Entre casos respondíveis, a redução foi de 67,4%; nesse recorte, o fluxo Jev levou 29,3% mais tempo que BM25 simples, pois acrescentou verificações. Não há superioridade universal de velocidade sobre RAG básico. Os percentuais dos dois experimentos não são cumulativos.

A comparação usa o mesmo corpus e gerador, mas os caminhos de abstenção diferem. Preparação e indexação ficam fora dos tempos; o cache automático dos provedores permanece ativo. A amostra pequena e reutilizada na depuração não representa toda a carga de produção. Dados e parâmetros constam de [desempenho/](desempenho/).

## Alternativas descartadas

Reutilização de conexão HTTPS e decisão adicional de complexidade aumentaram a média em 13,9% e 0,6%. Menor verbosidade e resposta em uma única afirmação reduziram a média em 5,8% e 4,0%, porém os intervalos bootstrap de 95% incluíram ausência de ganho. Essas alterações foram revertidas. O cache foi mantido por preservar respostas já validadas e apresentar redução direta nas repetições.
