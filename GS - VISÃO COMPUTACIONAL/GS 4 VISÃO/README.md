# CitizenTech — Módulo de Visão Computacional para Manutenção Urbana

Sistema de Visão Computacional baseado em Transferência de Aprendizado (`MobileNetV3-Small`) e Localização de Objetos Fracamente Supervisionada (`WSOL via Grad-CAM`) para identificação preventiva de fissuras em superfícies de concreto e simulação de monitoramento urbano contínuo em vídeo.

---

## Integrantes do Grupo

1. **Lucca Phelipe Masini** — RM 564121
2. **Igor Paixão Sarak** — RM 563726
3. **Bernardo Braga Perobeli** — RM 562468

- **Repositório Oficial no GitHub:** https://github.com/luccamasini-AI/citizentech-visao-computacional
- **Vídeo de Demonstração (YouTube):** https://youtu.be/91xrAAOsBxQ

---

## 1. Contextualização e Escopo Técnico

A identificação precoce de fissuras visíveis em estruturas de concreto (pontes, viadutos, muros de contenção e calçadas) auxilia a administração pública a priorizar vistorias de engenharia e planejar ações de manutenção. Este projeto integra ao protótipo **CitizenTech** um módulo completo de triagem visual automatizada com duas frentes operacionais:

- **Triagem de Imagem Individual:** Classifica superfícies de concreto entre *Com Fissura (Positive)* e *Sem Fissura (Negative)*, apresentando a probabilidade da predição, o grau de confiança do modelo, o mapa de atenção espacial via *Grad-CAM* e a caixa delimitadora obtida por **Localização Fracamente Supervisionada (*Weakly Supervised Object Localization — WSOL*)** sobre a região de ativação crítica (`>= 0,45`).
- **Monitoramento Urbano Contínuo (Vídeo e Sequência de Quadros):** Processa vídeos curtos com deslocamento contínuo de câmera (`.mp4`, `.avi`, `.mov`) ou sequências ordenadas de imagens de inspeção viária em passagem única (*single forward pass*), registrando telemetria em tempo real (latência por quadro em milissegundos e taxa de quadros por segundo — FPS), diagnóstico consolidado do trecho, inspetor individual de quadros e tabela auditável de ocorrências.

> **Diretriz de Governança e Engenharia Civil:** Esta solução atua exclusivamente como ferramenta de **triagem visual preventiva** para priorização de vistorias presenciais. A presença de fissuras superficiais em imagens bidimensionais, isoladamente, não permite determinar a profundidade do dano, sua origem patológica ou a segurança estrutural da edificação.

---

## 2. Estrutura do Repositório

```text
.
├── app_citizentech.py                      # Aplicação interativa do protótipo CitizenTech (Streamlit)
├── GS_FRONT.ipynb                          # Notebook executado (Preparação, Treinamento, Avaliação e Benchmark)
├── Relatório Técnico — Visão Computacional para Manutenção Urbana (CitizenTech).pdf # Relatório Técnico A4
├── Iniciar_CitizenTech.bat                 # Inicializador automatizado da aplicação para Windows
├── requirements.txt                        # Dependências de execução do ambiente local
├── artifacts/
│   ├── figures/                            # Gráficos gerados na avaliação do conjunto de teste
│   │   ├── confusion_matrix.png            # Matriz de confusão no conjunto de teste (678 imagens)
│   │   ├── training_history.png            # Curvas de perda (Loss) e acurácia no treinamento e validação
│   │   ├── correct_predictions_analysis.png# Exemplos de acertos acompanhados de mapas Grad-CAM
│   │   └── error_and_interference_analysis.png # Análise dos 2 FNs, sombra limítrofe e curva Precisão-Recall
│   ├── metrics/
│   │   └── evaluation_report.json          # Métricas consolidadas, sensibilidade de limiar e benchmarks
│   ├── model/
│   │   └── concrete_crack_mobilenetv3.pth  # Pesos treinados da arquitetura MobileNetV3-Small
│   └── sample_media/
│       ├── simulacao_monitoramento_urbano.mp4 # Vídeo de varredura contínua com deslocamento de câmera
│       └── test_images/                    # Amostras reais do conjunto de teste para demonstração
└── src/
    ├── domain/
    │   └── inspection_contracts.py         # Contratos de dados imutáveis e enumerações de domínio
    ├── inference/
    │   └── crack_classifier_service.py     # Serviço de inferência (fusão Conv-BN eps=1e-3) e WSOL/Grad-CAM
    ├── reporting/
    │   ├── bundle_and_report_manager.py    # Gerenciador seguro de artefatos e validação contra Zip Slip
    │   └── generate_printable_html_report.py # Gerador do relatório técnico A4 com gráficos em Base64
    └── video/
        └── urban_monitoring_processor.py   # Processador de fluxos de vídeo e renderizador de telemetria HUD
```

---

## 3. Metodologia e Prevenção de Vazamento de Dados

1. **Base de Dados:** *Concrete Crack Images for Classification* (Özgenel, 2019 — Mendeley Data), composta originalmente por 40.000 recortes RGB (`227x227 px`) extraídos de 458 fotografias originais de alta resolução.
2. **Amostragem Balanceada:** Utilizou-se uma amostra de **4.000 imagens** (`2.000 Positive` e `2.000 Negative`), dividida em **Treinamento (2.642)**, **Validação (680)** e **Teste (678)**.
3. **Heurística de Agrupamento por Superfície (*Zero Data Leakage*):** Como os arquivos da base Mendeley são numerados sequencialmente (`00001.jpg` a `20000.jpg`) com cerca de 87 recortes consecutivos por foto original, aplicou-se agrupamento por janelas contíguas de 85 índices (`índice // 85`) combinado ao sorteio aleatório de grupos (`GroupShuffleSplit` com `seed=42`), evitando que recortes adjacentes de uma mesma superfície fossem separados entre treino, validação e teste.
4. **Pré-processamento e Aumento de Dados:** Redimensionamento bilinear para `224x224 px`, normalização pelos parâmetros canônicos da ImageNet (`mean = [0.485, 0.456, 0.406]`, `std = [0.229, 0.224, 0.225]`) e aplicação de *Data Augmentation* no treino (espelhamento horizontal/vertical, rotação de ±15° e *ColorJitter*).

---

## 4. Resultados Experimentais, Análise de Erros e Desempenho

### 4.1. Métricas de Qualidade no Conjunto de Teste (678 Imagens Inéditas)

| Métrica | Resultado Obtido |
| :--- | :--- |
| **Precisão (Precision)** | `100,00%` (`FP = 0`) |
| **Sensibilidade (Recall)** | `99,41%` (`FN = 2`) |
| **F1-Score** | `99,70%` |
| **Acurácia Global** | `99,71%` (`TN = 339`, `TP = 337`) |
| **ROC-AUC / PR-AUC** | `1,0000 / 1,0000` |
| **Limiar de Confiança Padrão (Threshold)** | `0,50` (Modo Sensível para Sombras: `0,35`) |

### 4.2. Síntese da Análise de Erros e Sensibilidade ao Limiar

- **1º Falso Negativo (`Prob: 0,4%`):** Fissura vertical nítida, porém cercada lateralmente por intenso lascamento/desplacamento claro nas bordas (*spalling*), cujos contornos duplos levaram a rede a interpretá-la como degrau de relevo superficial.
- **2º Falso Negativo (`Prob: 0,8%`):** Grande cavidade/desplacamento escuro no canto inferior esquerdo, destoando da morfologia filamentar típica de trincas.
- **Sensibilidade ao Limiar sob Interferência de Sombra/Iluminação:** No conjunto de teste em iluminação ideal, a distribuição de probabilidades é bimodal (`Precisão = 100,00%` e `Recall = 99,41%` estáveis para `T` entre `0,10` e `0,90`). Contudo, sob sombras diagonais projetadas e baixa iluminação, fissuras reais têm sua probabilidade reduzida para a zona limítrofe (`35%–48%`, ex.: `46,1%`), onde a redução do limiar para `T = 0,35` recupera a detecção elevando o Recall sob sombra de `89,4%` para `97,6%`.

### 4.3. Benchmark de Latência e Taxa de Quadros (200 Imagens Reais de Teste)

| Ambiente de Hardware Avaliado | Resolução | Latência Média / Imagem | Latência P95 | Taxa de Quadros |
| :--- | :--- | :--- | :--- | :--- |
| **GPU NVIDIA Tesla T4 (Google Colab)** | `224x224 px` | `4,48 ms` (±0,52 ms) | `5,35 ms` | `223,2 FPS` |
| **CPU Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz** | `224x224 px` | `30,72 ms` (±0,74 ms) | `31,65 ms` | `32,6 FPS` |

*(Nota: Em processadores móveis de notebooks operando em economia de energia, a taxa situa-se entre `16,0 e 25,0 FPS`, mantendo fluidez adequada para varredura viária amostrada).*

---

## 5. Como Executar o Protótipo Localmente

### Opção 1 — Inicialização Rápida (Windows)

```bat
Iniciar_CitizenTech.bat
```

### Opção 2 — Execução Manual via Terminal

```bash
pip install -r requirements.txt
streamlit run app_citizentech.py
```

> **Equivalência Matemática e Portabilidade:** O serviço de inferência (`src/inference/crack_classifier_service.py`) realiza a fusão analítica de *Conv2d + BatchNorm2d* com `eps = 1e-3` (idêntico à especificação da `MobileNetV3-Small` no PyTorch/torchvision, com diferença numérica `< 1e-6`) e reutiliza as ativações em passagem única para geração do mapa Grad-CAM/WSOL.

---

## 6. Relatório Técnico (PDF)

O relatório técnico consolidado encontra-se na raiz do projeto no arquivo `Relatório Técnico — Visão Computacional para Manutenção Urbana (CitizenTech).pdf`.
