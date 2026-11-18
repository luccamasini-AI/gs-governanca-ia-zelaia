# Verificação da entrega

Versão de prompt 2026-11-10.18. Ambiente: Python 3.12.14 no Windows.

| Verificação | Resultado |
|---|---|
| Fluxo completo sem reutilização | Dez cenários, duas rodadas; 20/20 estados e critérios atendidos |
| Entulho e gesso | Critérios preservados nas duas rodadas |
| Afirmações do fluxo principal | 21, sem erro factual identificado na amostra |
| Cache | Vinte repetições; quatorze acertos de cache; vinte resultados idênticos aos originais |
| Perguntas adicionais sem cache | Dez cenários, duas rodadas; 19/20 estados esperados; uma abstenção indevida |
| Controles Jev | 33/34 decisões corretas; um falso negativo conservador |
| Ataques | Quatro indiretos excluídos e dois diretos bloqueados |
| Testes locais | 44 aprovados |
| Comparativo anterior, versão 13 | 120 execuções, seis variantes; componentes e geração isolada preservados |
| Vídeo | Ausente; gravação com a voz do integrante pendente |

O ganho de 94,1% corresponde à média do conjunto repetido com cache, sem promessa de aceleração de consultas novas. O relatório de desempenho apresenta os números e as condições da medição.

Os manifestos identificam código, entradas e resultados de cada experimento. Registros históricos preservam os hashes da versão em que foram produzidos; o manifesto editorial identifica a composição atual. Julgamentos por agente permanecem separados dos dados brutos, sem avaliação humana independente.

A conferência final inclui extração do ZIP, repetição dos testes locais, recálculo das métricas, verificação de hashes e varredura das credenciais configuradas. O pacote contém apenas código, dados, documentação e evidências pertinentes; não contém vídeo nem credenciais.
