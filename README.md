# Ecossistema CitizenTech e ZelaIA: Governança em IA e Business Analytics

**FIAP | Global Solution 2026.2 | Disciplina: Governança em IA e Business Analytics**

Repositório unificado (monorepo) contendo os **8 módulos disciplinares** desenvolvidos na Global Solution 2026.2, o **Hub Visual Executivo de Governança e Business Analytics** (`hub_governanca.py`) e o **Relatório Técnico em formato ABNT/FIAP** (`Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx`).

---

## Integrantes do Grupo

- **Lucca Phelipe Masini** - RM 564121
- **Igor Paixão Sarak** - RM 563726
- **Bernardo Braga Perobeli** - RM 562468

---

## 1. Estrutura do Monorepo (8 Disciplinas + Camada de Governança)

```text
.
├── hub_governanca.py                                      # Servidor Web HTTP do Hub de Governança e Business Analytics (SPA)
├── Iniciar_Hub_Governanca.bat                             # Inicializador rápido em 1 clique para Windows (Porta 8505)
├── governanca_hub/                                        # Módulos de domínio, telemetria, simulação e interface Web do Hub
│   ├── domain_contracts.py                                # Contratos imutáveis de auditoria e otimização
│   ├── repository_data_loader.py                          # Carregador de métricas JSON/CSV e artefatos das 8 pastas
│   ├── governance_simulation_engine.py                    # Sanitizador LGPD, simulador iSPD e solver combinatório QAOA
│   └── web/                                               # Front-End SPA (Bento Grid / Glassmorphism: index.html, styles.css, app.js)
├── Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx    # Relatório Técnico Oficial (Normas ABNT/FIAP - 13 páginas)
├── requirements.txt                                       # Dependências do Hub de Governança
├── GS - FRONT END/                                        # 1. Plataforma ZelaAI (Streamlit + FastAPI + ML + Gemini 2.5)
├── GS - VISÃO COMPUTACIONAL/                              # 2. Inspeção Preventiva de Fissuras (MobileNetV3 + Grad-CAM)
├── GS - CLUSTER/                                          # 3. Processamento em Cluster no Simulador iSPD 2.0 (2 vs 4 workers)
├── GS - COMPUTAÇÃO QUANTICA/                              # 4. Otimização Combinatória de Despacho (QAOA) e PQC (ML-KEM)
├── GS - RPA/                                              # 5. Robô de Triagem de Serviços Públicos (127 fontes .gov.br)
├── GS - GENERATIVE AI/                                    # 6. Assistente Descarte Certo (BM25 + Guarda Factual Jev)
├── GS - NLP/                                              # 7. Fábrica de Corpus CitizenTech (Código de Defesa do Consumidor)
└── GS - IOT/                                              # 8. Assistente Sonoro Embarcado OuviAí (Modelo 08 int8 Edge Impulse)
```

---

## 2. Como Executar o Hub Visual de Governança e Business Analytics

### Opção 1: Inicialização em 1 Clique (Windows)
Dê um duplo clique no arquivo **`Iniciar_Hub_Governanca.bat`** na raiz deste repositório.

### Opção 2: Terminal (PowerShell / CMD)
```powershell
python hub_governanca.py
```
O Hub Web Moderno (Design *Bento Grid / Glassmorphism*) abrirá automaticamente em `http://127.0.0.1:8505` com 4 visões interativas e resposta instantânea (0 ms):
1. **1. Ecossistema & Integração:** Fluxograma interativo da cadeia integrada do **Núcleo ZelaIA** (Front-End, Visão Computacional, Cluster e Computação Quântica), filtros e cartões *Bento Grid* das 8 matérias com modais de inspeção (exibindo arquivos verificados no disco e galerias de imagens reais).
2. **2. Simulador Ponta a Ponta:** Executa em tempo real a sanitização LGPD, a triagem visual sobre amostras reais de fissuras em concreto (com Modo Sombra `T = 0,35`), o dimensionamento de lote no cluster iSPD e o solver combinatório comparando a heurística gulosa com a solução ótima.
3. **3. Business Analytics:** Painéis comparativos com as métricas reais extraídas dos arquivos JSON, CSV e relatórios das 8 pastas (incluindo o estudo de áudios sintéticos e 72 variações em PyTorch do módulo IoT).
4. **4. Conformidade & LGPD:** Pilares regulatórios da Lei 13.709/2018 (Arts. 6º, 20, 23 e 46), supervisão humana (*Human-in-the-Loop*), prevenção de *data leakage* e cartões de auditoria individual por disciplina.

---

## 3. Síntese da Matriz de Integração Arquitetural

| Disciplina | Pasta no Repositório | Status de Integração | Métrica Principal Auditada |
| :--- | :--- | :--- | :--- |
| **Front-End em Sistemas de IA** | `GS - FRONT END` | **Integrado (Núcleo ZelaIA)** | 13 testes `pytest` (100%), WCAG AAA e duplo *Human-in-the-Loop* |
| **Visão Computacional** | `GS - VISÃO COMPUTACIONAL` | **Integrado (Núcleo ZelaIA)** | Acurácia `99,71%`, Precisão `100,00%`, Recall `99,41%` (`223,2 FPS` GPU) |
| **Cluster Computing** | `GS - CLUSTER` | **Integrado (Núcleo ZelaIA)** | Redução de `49,9945%` no tempo (`500,019 s` para `250,037 s` c/ 4 workers) |
| **Computação Quântica** | `GS - COMPUTAÇÃO QUANTICA` | **Integrado (Núcleo ZelaIA)** | Prioridade `20 pts` (ótimo A+B+C em 8h) vs `18 pts` (heurística gulosa) + PQC |
| **AI for RPA** | `GS - RPA` | **Vertical Independente Governada** | `100,0%` acurácia nos respondidos sozinho (`88,9%` geral) em `127 fontes .gov.br` |
| **Generative AI** | `GS - GENERATIVE AI` | **Vertical Independente Governada** | `20/20` estados esperados, `0/21` erros factuais, `-70,9%` latência com guarda Jev |
| **NLP** | `GS - NLP` | **Vertical Independente Governada** | `112` pares QA e `33` diálogos revisados manualmente (`>= 38,1%` língua informal) |
| **Cognitive IoT** | `GS - IOT` | **Vertical Independente Governada** | `3.900` decisões auditadas (`Modelo 08 int8`: `66,7%` validação / `55,6%` limpos) |

---

## 4. Links de Entrega

- **Vídeo de Demonstração (YouTube Não Listado - 5 a 7 minutos):** *[Inserir Link do Vídeo Aqui após gravação]*
- **Relatório Técnico ABNT/FIAP:** [`Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx`](Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx)
