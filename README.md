# 🌧️ Preditor de Alagamentos e Enchentes - Francisco Morato (SP)

## Índice

1.  [Visão Geral do Projeto]
2.  [Tecnologias Utilizadas]
3.  [Modelo de Machine Learning]
4.  [Estrutura do Projeto]
5.  [Instalação e Execução]
6.  [Uso do Aplicativo]
7.  [Arquivos Essenciais]
8.  [Desenvolvimento e Contribuição]

-----

## 1\. Visão Geral do Projeto

Este projeto consiste em um aplicativo web interativo, desenvolvido com **Streamlit**, que utiliza um modelo de Machine Learning para prever o risco de alagamentos e enchentes na cidade de **Francisco Morato**, na Região Metropolitana de São Paulo.

O objetivo principal é fornecer uma ferramenta de alerta precoce que, baseada em dados meteorológicos em tempo real, possa auxiliar a Defesa Civil, moradores e comerciantes a tomarem medidas preventivas.

### 🎯 Objetivo

Classificar a probabilidade de ocorrência de enchente (risco Alto ou Baixo/Moderado) em tempo real, utilizando um limiar de alerta definido para a classificação binária.

### 📍 Localização Focada

Francisco Morato/SP, uma região historicamente afetada por eventos de cheias, especialmente na área central próxima aos córregos.

-----

## 2\. Tecnologias Utilizadas

O projeto é baseado nas seguintes tecnologias e bibliotecas:

  * **Python:** Linguagem principal de desenvolvimento.
  * **Streamlit:** Framework para criação da interface web interativa.
  * **Machine Learning (XGBoost):** Algoritmo de classificação para a predição.
  * **Joblib/Pickle:** Para serialização e carregamento do modelo e da lista de *features*.
  * **Pandas/NumPy:** Para manipulação de dados na fase de inferência.
  * **API Externa:** Para coleta de dados meteorológicos em tempo real (implementada em `api_data_collector.py`).
  * **HTML/CSS:** Para estilização da interface (via `style.css` e `st.markdown`).

-----

## 3\. Modelo de Machine Learning

### 🧠 Algoritmo

O núcleo do sistema é um modelo de **XGBoost (Extreme Gradient Boosting)**, um algoritmo robusto e eficiente, ideal para problemas de classificação.

### ⚙️ Funcionamento

1.  O usuário clica no botão **"Consultar Risco de Enchente Agora"**.
2.  O sistema utiliza a função `get_real_time_features` (do `api_data_collector.py`) para coletar dados meteorológicos atualizados (ex: precipitação acumulada, temperatura, umidade, vento, etc.).
3.  Esses dados são processados e formatados nas *features* esperadas pelo modelo (definidas em `features_cols.joblib`).
4.  O modelo XGBoost calcula a **probabilidade** de ocorrência de enchente.
5.  A probabilidade é comparada com o **limite de alerta (`THRESHOLD = 0.55` ou 55%)**:
      * **Probabilidade $\geq 55\%$:** Risco Alto (Alerta Vermelho/Laranja).
      * **Probabilidade $< 55\%$:** Risco Baixo/Moderado (Alerta Verde/Amarelo).

-----

## 4\. Estrutura do Projeto

O repositório está organizado da seguinte forma:

```
.
preditor_enchente/
├── apps.py                 # Aplicação principal Streamlit
├── api_data_collector.py   # Módulo para coleta e processamento dos dados da API (Assumido)
├── style.css               # Arquivo CSS para estilização da interface
├── modelo_enchente_final_xgb.joblib # Arquivo binário do modelo treinado (XGBoost)
├── features_cols.joblib    # Lista das colunas (features) esperadas pelo modelo
└── README.md               # Este arquivo de documentação
```

-----

## 5\. Instalação e Execução

Siga os passos abaixo para clonar o repositório e rodar o aplicativo localmente.

### 5.1 Pré-requisitos

Certifique-se de ter o Python instalado (versão recomendada: 3.8+).

### 5.2 Instalação das Dependências

Crie um ambiente virtual (opcional, mas recomendado) e instale as bibliotecas necessárias:

```bash
# 1. (Opcional) Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate   # No Windows

# 2. Instale as dependências listadas no arquivo requirements.txt usando o pip:
pip install -r requirements.txt
```

### 5.3 Execução do Aplicativo

Certifique-se de que os arquivos do modelo (`.joblib`) estão na mesma pasta que o `apps.py`.

Execute a aplicação Streamlit no terminal:

```bash
streamlit run apps.py
```

O Streamlit irá iniciar um servidor local e abrir o aplicativo no seu navegador padrão (geralmente em `http://localhost:8501`).

-----

## 6\. Uso do Aplicativo

A interface é simples e intuitiva:

1.  **Tela Inicial:** Você verá o título do projeto e um botão principal.
2.  **Ação:** Clique no botão **"Consultar Risco de Enchente Agora"**.
3.  **Processamento:** Aguarde enquanto o Streamlit busca os dados meteorológicos e executa a predição.
4.  **Resultado do Tempo:** O aplicativo exibirá as condições atuais do tempo em Francisco Morato (temperatura, umidade, etc.).
5.  **Resultado da Predição:** A seção **"Resultado da Predição"** mostrará:
      * Uma caixa verde (Risco Baixo/Moderado) ou vermelha (Risco Alto).
      * A probabilidade exata de enchente (%) calculada pelo modelo.
6.  **Detalhes:** Utilize o *expander* **"📊 Ver detalhes das variáveis utilizadas"** para inspecionar os valores das *features* que foram alimentadas no modelo.

-----

## 7\. Arquivos Essenciais

| Arquivo | Descrição |
| :--- | :--- |
| `apps.py` | Lógica da aplicação Streamlit, carregamento do modelo, coleta de dados, predição e renderização da interface. |
| `style.css` | Folha de estilos externa para customização visual do Streamlit (fundo, cards de tempo, botões). |
| `api_data_collector.py` | **Módulo Crítico.** Contém a lógica de conexão com a API de tempo, extração e cálculo das variáveis (*features*) necessárias para a predição. |
| `modelo_enchente_final_xgb.joblib` | O modelo XGBoost treinado e serializado. |
| `features_cols.joblib` | Lista na ordem correta das *features* (colunas) que o modelo espera receber. **A ordem é vital.** |

-----
## 8\.🔑 Configuração da Chave de API
O aplicativo requer uma chave de API do OpenWeatherMap para coletar dados meteorológicos.

Para rodar o projeto, você precisa configurar o arquivo de segredos do Streamlit:

1. Obter a Chave
Crie uma conta no OpenWeatherMap.

Gere e copie sua chave de API na seção "API keys" do seu painel de usuário.

2. Criar o Arquivo de Segredos
Crie o arquivo secrets.toml dentro da pasta .streamlit/ na raiz do seu projeto.
```
.
preditor_enchente/
└── .streamlit/
    └── secrets.toml  <-- CRIE ESTE
3. Inserir a Chave
Cole sua chave de API dentro do arquivo secrets.toml no formato TOML (usando aspas duplas):


```
Ini, TOML
[api]
chave_tempo = "SUA_CHAVE_DE_API_AQUI"
Após este passo, o aplicativo estará pronto para ser executado:
```

```bash

streamlit run preditor_enchente/apps.py
```
-----

## 9\. Desenvolvimento e Contribuição

Este projeto foi desenvolvido como **Projeto Integrador IV**. Sugestões de melhoria são bem-vindas\!

**Ideias para Próximas Fases:**

  * Adicionar previsão para horizontes futuros (ex: risco nas próximas 3, 6 e 12 horas).
  * Integrar dados de pluviômetros locais para validação e *feature engineering*.
  * Implementar um *mapa* interativo mostrando áreas de risco com base na previsão.
  * Otimizar a função de coleta de dados para tratamento de falhas mais robusto.



-----

*Projeto Integrador IV - Univesp*