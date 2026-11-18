# Roteiro Prático de Gravação do Vídeo (5 a 7 Minutos — Alvo: 6m00s)

> **Regras do Barema (3 Pontos):**
> - Duração obrigatória: **entre 5m00s e 7m00s** (Alvo ideal: **5m45s a 6m15s**).
> - Publicar no YouTube como **"Não Listado"**.
> - **Zero leitura de documento PDF/Word:** Você vai conduzir 100% da apresentação navegando pelas **4 telas do Hub Web Moderno (`http://127.0.0.1:8505`)** e clicando nos cartões e simuladores.

---

## Preparação (Antes de Apertar "Gravar" no OBS Studio)

1. Dê duplo clique em **`Iniciar_Hub_Governanca.bat`** para abrir o Hub em `http://127.0.0.1:8505`.
2. Aperte **`F11`** no navegador (tela cheia) para esconder a barra de favoritos e deixar o visual de sistema profissional.
3. Deixe o VS Code (ou o Explorador de Arquivos do Windows) aberto em segundo plano na pasta `GS FINAL GOVERNANÇA` apenas para mostrar por 15 segundos no início que as 8 pastas estão lá.

---

## Passo a Passo da Apresentação (Dividido pelas 4 Telas do Topo)

### 🎬 Bloco 1: Abertura + Tela 1 (`1. Ecossistema & Integração`) — `0:00` até `2:00` (2 min)

1. **Nos primeiros 20 segundos (VS Code / Pasta):**
   - Mostre rapidamente a pasta raiz com as **8 pastas das disciplinas** (`GS - CLUSTER`, `GS - COMPUTAÇÃO QUANTICA`, `GS - FRONT END`, `GS - GENERATIVE AI`, `GS - IOT`, `GS - NLP`, `GS - RPA`, `GS - VISÃO COMPUTACIONAL`) e diga:
     *"Olá, somos o grupo formado por Lucca Masini, Igor Sarak e Bernardo Perobeli. Nesta Global Solution de Governança em IA e Business Analytics, reunimos todos os 8 módulos desenvolvidos no semestre em um monorepo unificado e construímos este Hub Executivo em Python para demonstrar a arquitetura, o que foi integrado, o que ficou desacoplado e as métricas reais."*
2. **Mude para o Navegador na Tela 1 (`1. Ecossistema & Integração`):**
   - **Aponte para a faixa do Fluxograma no topo (`Cadeia Operacional Integrada: Núcleo ZelaIA`):**
     - Explique que **4 disciplinas foram integradas no fluxo de zeladoria urbana (ZelaIA)**:
       1. **Front-End (`ZelaAI`):** O cidadão relata o problema urbano com acessibilidade WCAG AAA; o FastAPI mascara dados LGPD, cruza clima ao vivo (`Open-Meteo` e `ViaCEP`), roda um `RandomForest` e usa o `Gemini 2.5 Flash` com validação humana.
       2. **Visão Computacional:** Recebe a foto do concreto e usa `MobileNetV3-Small` + `Grad-CAM` para detectar fissuras preventivamente (`99,71%` de acurácia).
       3. **Cluster Computing (`iSPD 2.0`):** Dimensiona os servidores para processar lotes de `1.000` fotos simultâneas, cortando o tempo pela metade (`-49,99%`) ao dobrar de 2 para 4 workers.
       4. **Computação Quântica:** Entra depois da triagem para otimizar quais chamados as equipes da prefeitura devem atender no limite de 8 horas diárias (Mochila Binária / QAOA) e aplica o roadmap de Criptografia Pós-Quântica (`PQC ML-KEM`).
   - **Clique nos filtros `🟢 Integrados no ZelaIA (4)` e depois em `🔵 Verticais Independentes (4)`:**
     - Explique por que as outras **4 disciplinas ficaram desacopladas no código**, mas governadas pelo mesmo Hub:
       - **RPA** atende `127 serviços documentais (.gov.br)` como CNH e INSS (não zeladoria de rua);
       - **Generative AI (`Descarte Certo`)** opera sobre corpus fechado de Ecopontos com verificador `TypeSafe Jev`;
       - **NLP (`Fábrica de Corpus`)** é um pipeline batch de 90 minutos em GPU no Colab para o Código de Defesa do Consumidor;
       - **IoT (`OuviAí`)** é um modelo acústico `int8` embarcado (`Cortex-M4F`) para detectar campainha e batida na porta para pessoas surdas.
   - **Demonstre o Modal clicando em 2 cartões:**
     - Clique no cartão de **`Visão Computacional`** (mostre a Matriz de Confusão e os mapas Grad-CAM reais que abrem no modal e feche no `✕`).
     - Clique no cartão de **`Cognitive IoT (OuviAí)`** (mostre o link do Edge Impulse Studio, o alvo `Cortex-M4F 80MHz` e as **5 capturas reais do Studio** e feche no `✕`).

---

### ⚡ Bloco 2: Tela 2 (`2. Simulador Ponta a Ponta`) — `2:00` até `3:45` (1 min 45s)

Clique na 2ª pílula do topo (**`2. Simulador Ponta a Ponta`**) e interaja ao vivo com os 4 cartões na ordem:

1. **Card 1 (`Portão de Sanitização LGPD`):**
   - Aponte para as tags verdes `[CPF PROTEGIDO - LGPD]`, `[TELEFONE PROTEGIDO - LGPD]` e `[EMAIL PROTEGIDO - LGPD]`. Clique no botão `Exemplo 2` e depois volte ao `Exemplo 1` para mostrar a interceptação automática em tempo real antes de qualquer envio ao modelo.
2. **Card 2 (`Triagem Preventiva de Fissuras`):**
   - Troque a imagem no seletor entre uma amostra `🔴 Com Fissura` e uma `🟢 Normal (Sem Fissura)`.
   - Volte para uma com fissura e marque a caixinha **`Ativar Modo Sombra (Limiar T = 0,35)`**, explicando que sob sombras fortes a probabilidade cai para a faixa de `35% a 48%`, e reduzir o limiar para `0,35` recupera o Recall de `89,4%` para `97,6%`.
3. **Card 3 (`Escalabilidade no Cluster iSPD`):**
   - Arraste o slider de `1.000 fotos` para `2.500` ou `3.000 fotos` mostrando os MFLOPs e os segundos atualizando na hora e provando a redução linear de `49,9945%` entre 2 e 4 workers.
4. **Card 4 (`Computação Quântica vs. Heurística`):**
   - Deixe o slider em **`8 horas`** e mostre o placar: a **Heurística Gulosa** escolhe `C + A + D` e entrega `18 pontos`, enquanto o **Ótimo Combinatório / QAOA** encontra `A + B + C` entregando **`20 pontos (+2 pts de prioridade social)`**. Mova o slider rapidamente para `10h` ou `6h` para mostrar o cálculo dinâmico.

---

### 📊 Bloco 3: Tela 3 (`3. Business Analytics`) — `3:45` até `5:00` (1 min 15s)

Clique na 3ª pílula do topo (**`3. Business Analytics`**) e destaque 1 ponto de cada um dos 4 painéis:

1. **Painel 1 (`Qualidade Preditiva & Guardrails`):** Destaque como no **RPA** a acurácia bruta era `88,9%`, mas ao reter casos com confiança abaixo de `0,60` para revisão humana, a acurácia automática subiu para **`100%`** (zero resposta errada ao cidadão).
2. **Painel 2 (`Eficiência Operacional`):** Destaque a redução de `70,9%` na latência do **GenAI Descarte Certo** usando o verificador `Jev` no lugar de LLM puro, e `94,1%` usando cache de respostas aprovadas.
3. **Painel 3 (`GS - IOT • OuviAí`):** Aponte para a tabela comparativa do ensaio em PyTorch mostrando que adicionar os **31 áudios sintéticos e 72 variações acústicas** aumentou a acurácia sob chuva intensa (`SNR 10 dB`) de **`34,8%` para `40,7%`**, embora tenha reduzido levemente nos áudios limpos (`65,2%` para `60,7%`).
4. **Painel 4 (`GS - NLP • Fábrica de Corpus`):** Mostre que os 3 corpus revisados manualmente superaram a meta mínima de `30%` de linguagem informal cidadã (`58,3%` no Chat, `50,0%` no Teste e `38,1%` no QA).

---

### 🛡️ Bloco 4: Tela 4 (`4. Conformidade & LGPD`) e Encerramento — `5:00` até `6:00` (1 min)

1. Clique na 4ª pílula do topo (**`4. Conformidade & LGPD`**).
2. Aponte para os **4 Pilares no topo** (`Art. 6º, 23 e 46 da LGPD`, `Art. 20 Supervisão Humana HITL`, `Zero Data Leakage com GroupShuffleSplit e Hashes SHA-256`, e `Guardrails Anti-Alucinação`).
3. Role suavemente pelos 8 cartões de auditoria mostrando que todos os limites operacionais de cada modelo foram declarados com transparência (ex.: imagens 2D não medem profundidade de fissura, computadores quânticos ainda não têm vantagem comprovada hoje para poucos itens, e juízes automáticos de NLP precisam de revisão humana).
4. Se quiser, clique no botão **`☀️ Tema Claro / 🌙 Tema Escuro`** no canto superior direito apenas para mostrar o acabamento da interface e encerre o vídeo por volta de **6m00s**!
