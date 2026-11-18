# Descarte Certo

Assistente CitizenTech sobre descarte de resíduos no município de São Paulo, integrado a um protótipo web com fontes municipais, recuperação BM25, decisões Jev e geração OpenAI.

**Equipe:** Lucca Phelipe Masini (RM 564121), Igor Paixão Sarak (RM 563726) e Bernardo Braga Perobeli (RM 562468).

## Execução

O projeto requer Python 3.11 ou superior e conexão com a internet. A aplicação utiliza exclusivamente a biblioteca padrão do Python e arquivos HTML, CSS e JavaScript, sem compilação.

A configuração depende de uma cópia de `.env.exemplo` denominada `.env.local`, com as variáveis OPENAI_API_KEY e TYPESAFE_API_KEY preenchidas. Esse arquivo contém segredos e permanece fora da entrega e do controle de versão.

~~~powershell
python -m descarte
~~~

O protótipo fica disponível em [127.0.0.1:8765](http://127.0.0.1:8765). A opção `--env caminho/credenciais.env` permite um arquivo externo; `--porta 8766` altera a porta. O encerramento do processo interrompe o servidor.

## Validação

Os testes locais e os resumos dos resultados não consomem créditos:

~~~powershell
python -m unittest discover -s testes -v
python -m descarte.resumo_revisao
python -m descarte.otimizacao --resumir relatorios/otimizacao/execucoes.json
python -m descarte.resumo_desempenho --arquivo relatorios/desempenho/execucoes.json
~~~

As avaliações com APIs reais exigem credenciais e consomem créditos. Cada execução deve utilizar uma pasta de saída nova, preservando as evidências entregues.

~~~powershell
python -m descarte.revisao --env .env.local --saida novos-resultados/revisao --repeticoes 2 --executar-api
python -m descarte.otimizacao --env .env.local --saida novos-resultados/otimizacao --executar-api
python -m descarte.validacao_adicional --env .env.local --saida novos-resultados/adicionais --executar-api
python -m descarte.desempenho --env .env.local --saida novos-resultados/desempenho --executar-api
python -m descarte.avaliacao --etapa recuperacao --saida novos-resultados/componentes
python -m descarte.avaliacao --env .env.local --etapa geracao --saida novos-resultados/componentes --executar-api
python -m descarte.avaliacao --env .env.local --etapa geracao_sem_evidencia --saida novos-resultados/componentes --executar-api
~~~

Novas respostas exigem novos julgamentos de fundamentação e utilidade. O comparativo de desempenho contém seis variantes, dez cenários e duas rodadas, além da preparação e da indexação vetorial registradas separadamente.

## Materiais

| Conteúdo | Local |
|---|---|
| Aplicação e avaliações reproduzíveis | descarte/ e web/ |
| Corpus, configuração, equipe e perguntas | dados/ |
| Testes locais | testes/ |
| Decisões técnicas e correspondência com o enunciado | docs/ARQUITETURA.md e docs/MATRIZ-REQUISITOS.md |
| Avaliação de qualidade e limitações | relatorios/REVISAO-FINAL.md |
| Comparação medida de desempenho | relatorios/DESEMPENHO.md |
| Contextos, respostas, decisões, julgamentos e métricas | relatorios/revisao/, desempenho/, otimizacao/ e adicionais/ |
| Roteiro para gravação de até cinco minutos | docs/ROTEIRO-VIDEO.md |

## Escopo e privacidade

A base contém seis sínteses de publicações municipais. O protótipo não consulta filas, operação ou itinerários ao vivo, não agenda coleta e não registra denúncias. O gerador isolado constitui um componente experimental; as respostas públicas passam pelo fluxo completo com Jev.

Nas consultas novas, perguntas e evidências são enviadas à TypeSafe e à OpenAI. Respostas aprovadas podem ser reutilizadas por cinco minutos quando pergunta, histórico, corpus e configuração permanecem idênticos. O histórico permanece na memória do navegador até o recarregamento ou o início de nova conversa. A proteção local reconhece alguns padrões de dados pessoais e ataques, sem cobertura universal.

A aplicação funciona localmente. Os resultados descrevem uma amostra reutilizada na depuração, com julgamento editorial por agente, sem avaliação humana independente ou garantia de desempenho em novas consultas.

O vídeo com a voz do integrante será gravado separadamente e deverá acompanhar a submissão. O pacote não contém vídeo.
