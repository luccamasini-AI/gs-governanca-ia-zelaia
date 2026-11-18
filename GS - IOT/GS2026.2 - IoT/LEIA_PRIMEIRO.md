# OuviAí | Material para entrega

Abra Relatorio GS2026.2 - IOT.pdf para consultar metodologia, resultados e evidências. O relatório apresenta as gravações dos conjuntos públicos, o lote de audio utilizado e as variações usadas para ampliar a diversidade. A primeira página contém os nomes e RMs dos três integrantes.

## Conteúdo

- evidencias/ reúne cinco capturas do Studio e os registros textuais do modelo 08 int8. As imagens históricas do modelo 01 estão identificadas.
- robustez/ reúne métricas, previsões e divisão da bateria pública no Studio.
- experimento_sinteticos/ reúne os resultados de nove treinamentos locais em PyTorch e o manifesto dos WAVs selecionados para treino.
- sinteticos/ reúne os audios WAVs sintéticos e as transformações.
- atribuicoes/ reúne os manifestos de autoria e licenças dos dados públicos.

O modelo principal do projeto é o 08 int8 no Edge Impulse. Os resultados em PyTorch correspondem ao ensaio local, em float32. O escopo documentado neste pacote é a avaliação com os arquivos públicos e o ensaio com o lote de dados.

## Projeto no Studio

https://studio.edgeimpulse.com/studio/1161308/impulse/8/learning/keras/25
