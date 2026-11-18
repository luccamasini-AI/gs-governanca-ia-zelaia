# Correspondência com o PDF

Referência: GS2026.2 GenerativeAI.pdf, duas páginas. O [relatório final](../relatorios/REVISAO-FINAL.md) registra resultados e limites.

| Requisito | Evidência |
|---|---|
| Assistente funcional integrado à CitizenTech | Interface web e API local, com histórico |
| Base identificável e relevante | dados/corpus.json: seis sínteses municipais com URLs e datas |
| Chunking, tamanho, overlap e metadados justificados | ARQUITETURA.md; comparação de três configurações |
| Retriever, top-k, parâmetros, embeddings e reranking | BM25 + Jev no produto; comparação com embeddings e busca híbrida no relatório de desempenho |
| LLM, papel, prompt, contexto, formato e parâmetros | Código, configuração e ARQUITETURA.md |
| Avaliação individual de recuperação | relatorios/revisao/componentes/teste-recuperacao.json |
| Geração controlada e falta de evidência | Treze casos respondíveis e três insuficientes em componentes/ |
| Pelo menos dez perguntas variadas | Dez cenários, duas rodadas por variante, com histórico, ambiguidade, escopo e falta de evidência |
| Contextos, respostas e julgamentos | fluxo-repetido.json e julgamentos.json em revisao/final/ |
| Sistema completo, fundamentação, utilidade e consistência | Relatório, métricas reproduzíveis e decisões Jev |
| Pelo menos dois testes adversariais | Dois ataques indiretos e um direto, todos repetidos |
| Mitigação demonstrável | Seleção, suficiência, validação de fontes, sustentação, cobertura e abstenção |
| Código, dependências e execução | README, requirements.txt, Python padrão |
| Corpus e configuração reproduzíveis | dados/ e manifestos com hashes |
| Relatório por componente e end-to-end | relatorios/REVISAO-FINAL.md |
| Vídeo de até cinco minutos, sucesso, falha, mitigação e limites | Pendente de gravação pelo integrante, com a própria voz; roteiro em ROTEIRO-VIDEO.md |
| Até três integrantes com nomes e RMs | README, relatório, interface e roteiro |
| Não expor segredos | Chaves fora da entrega e varredura do pacote |

A matriz relaciona os requisitos às evidências entregues. Os limites da amostra e as falhas observadas constam dos relatórios.
