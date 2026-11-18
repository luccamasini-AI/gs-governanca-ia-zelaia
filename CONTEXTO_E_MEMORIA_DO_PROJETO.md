# Contexto e Memória do Projeto — GS Governança em IA e Business Analytics

**Última atualização:** 18/11/2026  
**Instituição / Curso:** FIAP — Tecnologia em Inteligência Artificial (Global Solution 2026.2)  
**Disciplina Central:** Governança em IA e Business Analytics  
**Tema Global:** Ecossistema CitizenTech & ZelaIA  

---

## 1. Integrantes do Grupo (Alinhamento Vertical na Capa e Folha de Rosto)

- **Lucca Phelipe Masini** - RM 564121
- **Igor Paixão Sarak** - RM 563726
- **Bernardo Braga Perobeli** - RM 562468

---

## 2. Requisitos e Barema Oficial do Enunciado

| Entregável | Peso | Regras Críticas do Edital | Status Atual |
| :--- | :---: | :--- | :--- |
| **1. Documentação (ABNT/FIAP)** | **4,0 pts** | Limite estrito de **10 a 15 páginas** (entregue com **13 páginas**). Capa, Folha de Rosto, Listas de Ativos, Sumário, Introdução, 1 tópico por disciplina finalizando com Governança (mostrando o que foi e o que não foi integrado), Tópico Links e Conclusão. Sem jargões de IA ou travessões (`—`). Compatível com **WPS Office**. | **Concluído** (`Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx`) |
| **2. Repositório GitHub** | **3,0 pts** | Repositório contendo todos os itens desenvolvidos (as 8 pastas das disciplinas + Hub de Governança + Relatório). Commits realizados antes da entrega e sem exposição de chaves `.env`. | **Concluído e Versionado** |
| **3. Vídeo de Demonstração** | **3,0 pts** | Duração de **5 a 7 minutos**, publicado no YouTube como **"Não Listado"**. **Proibida leitura massiva de documento** (apresentação feita navegando pelo Hub Web Moderno). | **Roteiro Pronto** (`ROTEIRO_VIDEO_5_A_7_MINUTOS.md`) — Pendente gravação pelo grupo |

---

## 3. Arquitetura de Integração e Governança Adotada

Para respeitar a engenharia de cada projeto sem criar acoplamentos artificiais entre linguagens e hardwares distintos, os **8 módulos** foram organizados em **2 blocos** supervisionados pelo **Hub Web Moderno (`hub_governanca.py`)**:

### Bloco A — Núcleo Integrado de Zeladoria Urbana (`ZelaIA`)
Operam em sequência lógica sobre o mesmo objeto de negócio (a ocorrência urbana georreferenciada com foto):
1. **`GS - FRONT END` (`ZelaAI`):** Portal acessível (Streamlit WCAG 2.1 AAA + TTS) e API REST (`FastAPI`) com anonimização LGPD via Regex, consulta ao vivo `ViaCEP` + `Open-Meteo`, modelo `RandomForestRegressor` (`scikit-learn`), `Gemini 2.5 Flash` estruturado (`Pydantic`), duplo *Human-in-the-Loop* e 13 testes `pytest` (100%).
2. **`GS - VISÃO COMPUTACIONAL` (`CitizenTech Manutenção Urbana`):** Classificador `MobileNetV3-Small` + `WSOL / Grad-CAM` para detecção preventiva de fissuras em concreto (`4.000` imagens Mendeley, `GroupShuffleSplit` janela 85 contra *data leakage*, Acurácia `99,71%`, Precisão `100,00%`, Recall `99,41%`, `223,2 FPS` em GPU T4 / `32,6 FPS` em CPU e limiar sensível a sombra `T = 0,35`).
3. **`GS - CLUSTER` (`ZelaIA no iSPD 2.0`):** Simulação de infraestrutura distribuída no `iSPD 2.0` (UNESP / Java Temurin 8) para lotes de `1.000` imagens simultâneas (`1.000 MFLOP` e `8 Mbit` por tarefa, escalonamento `RoundRobin`). Escalar de 2 para 4 workers reduziu o tempo total em **`49,9945%`** (`500,019 s` para `250,037 s`).
4. **`GS - COMPUTAÇÃO QUANTICA` (`ZelaIA Otimização e PQC`):** Formulação binária (Problema da Mochila / QUBO compatível com `QAOA` e *quantum annealing*) para priorização das equipes de rua sob orçamento de `8 horas`. Comprova que a heurística gulosa escolhe `C+A+D` (`18 pts`), enquanto a combinação ótima é `A+B+C` (`20 pts`). Inclui roadmap de Criptografia Pós-Quântica (`PQC ML-KEM`, padrão `NIST FIPS 203`).

### Bloco B — Verticais Independentes Governadas (`CitizenTech`)
Mantidas desacopladas no código-fonte por possuírem escopos documentais, bancos ou hardwares próprios, mas auditadas pelo mesmo Hub:
5. **`GS - RPA` (`Robô de Triagem de Serviços Públicos`):** Triagem sobre **`127 fontes oficiais aprovadas (.gov.br)`** (58 federais, 33 estaduais SP e 36 municipais SP), com sanitização de 9 tipos de PII, classificador `Regex + TF-IDF + Regressão Logística`, verificação HTTP 200 e fila humana (`needs_human`). Corte de confiança `0,60` retém `33,3%` para revisão humana e eleva a acurácia automática de `88,9%` para **`100,0%`**.
6. **`GS - GENERATIVE AI` (`Descarte Certo`):** Assistente web sobre Ecopontos e Cata-Bagulho em SP (biblioteca padrão Python, `44` testes unitários), busca léxica `BM25` (`chunks 90/15`), verificador factual `TypeSafe Jev` (`33/34` controles corretos, `20/20` estados esperados, `0/21` erros factuais, `4/4` bloqueios de *prompt injection*). Redução de latência de **`70,9%`** com Jev vs. LLM puro e **`94,1%`** com cache validado (`2,185 s` para `0,129 s`).
7. **`GS - NLP` (`Fábrica de Corpus CitizenTech — CDC`):** Pipeline em GPU T4 no Google Colab (`Qwen2.5-7B-Instruct` 4-bit + `spaCy pt_core_news_lg` + Regex) sobre legislação do consumidor. Gerou `68` trechos de texto, `112` pares QA (de 126 após revisão humana integral), `33` diálogos de chat e `24` testes inéditos, superando a meta de `30%` de linguagem informal cidadã (`38,1%` QA, `58,3%` Chat e `50,0%` Teste).
8. **`GS - IOT` (`OuviAí — Modelo 08 int8 + Ensaio Sintéticos PyTorch`):** Classificador acústico embarcado no *Edge Impulse Studio* (projeto `1161308`, alvo `Cortex-M4F 80MHz`, `MFE FFT 512 + CNN 1D int8`, limiar `0,60`) para apoiar pessoas com deficiência auditiva (campainha, batida na porta e ambiente). Avaliado em **`3.900 decisões`** no Studio (`66,7%` validação/histórico, `55,6%` limpos, `51,1%` em `-12 dB`, `33,3%` em `SNR 20 dB` e `31,1%` em `SNR 10 dB`) + **ensaio local em PyTorch (`float32`, 3 sementes `[17, 29, 43]`, 78 públicos + 31 sintéticos + 72 variações acústicas)** que elevou a acurácia sob chuva `SNR 10 dB` de `34,8%` para `40,7%`, além de manifestos `CC BY` e hashes `SHA-256` em `atribuicoes/`.

---

## 4. Mapa de Arquivos Criados na Raiz do Projeto

- `hub_governanca.py`: Servidor Web local em Python (porta `8505` com fallback automático `8505..8519`) que alimenta o Hub de Governança e serve as imagens reais das pastas.
- `Iniciar_Hub_Governanca.bat`: Inicializador em 1 clique para Windows (encerra instâncias antigas na porta 8505 e abre `http://127.0.0.1:8505`).
- `governanca_hub/`:
  - `domain_contracts.py`: Contratos de dados (`ModuleGovernanceRecord`, `KnapsackTaskItem`, `OptimizationComparisonResult`, `SanitizationAuditResult`).
  - `repository_data_loader.py`: Leitor dos JSONs, CSVs e imagens das 8 pastas.
  - `governance_simulation_engine.py`: Motor de sanitização LGPD, cálculo de cluster iSPD e solver combinatório exato vs. guloso.
  - `web/index.html`, `web/styles.css`, `web/app.js`: Interface SPA moderna no estilo *Bento Grid / Glassmorphism* com 4 visões e modais de inspeção.
- `Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx`: Documento Word ABNT/FIAP de 13 páginas compatível com WPS Office, já com a conclusão humanizada na Seção 5.
- `ROTEIRO_VIDEO_5_A_7_MINUTOS.md`: Guia minuto a minuto para gravar o vídeo de 6 minutos navegando pelas 4 pílulas do Hub.
- `README.md` e `.gitignore`: Documentação do monorepo e proteção contra vazamento de arquivos `.env`.

---

## 5. O Que Falta Fazer na Próxima Sessão / Antes da Entrega Final

1. **Gravar o vídeo de 5 a 7 minutos** seguindo o `ROTEIRO_VIDEO_5_A_7_MINUTOS.md` com o Hub aberto (`Iniciar_Hub_Governanca.bat`) e publicar no YouTube como **Não Listado**.
2. **Inserir o link do YouTube Não Listado** no **Quadro 11 (Página 12)** do arquivo `Relatorio_Integracao_Governanca_IA_ZelaIA_ABNT.docx` e no `README.md`.
