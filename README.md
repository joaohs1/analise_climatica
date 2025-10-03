# 🌧️ MVP - Previsão de Enchentes Suzano (Palmeiras)

Este projeto é um **MVP de previsão de risco de enchentes/alagamentos** usando dados de chuva do **CEMADEN** e alagamento/enchentes do **S2id/MDR** , aprendizado de máquina e visualização via **Streamlit**.

---

## 1. Estrutura de pastas

analise_climatica/
├─ data/
│ ├─ raw/ # CSVs brutos (ex.: dados da estação CEMADEN e S2id/MDR)
│ └─ processed/ # dados processados para treino/modelo
├─ notebooks/
│ ├─ 01-exploracao.ipynb
│ └─ 02-exploracao.ipynb
├─ src/
│ ├─ ingest.py
│ ├─ preprocess.py
│ ├─ train.py
│ └─ app_streamlit.py
├─ requirements.txt
└─ README.md

