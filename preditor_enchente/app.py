import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Importa função de coleta de dados
from api_data_collector import get_real_time_features, LAT_FM, LON_FM
# --- CONFIGURAÇÕES ---
THRESHOLD = 0.55  # Limite de alerta
NOME_DO_MODELO = 'modelo_enchente_final_xgb.joblib'
NOME_FEATURES = 'features_cols.joblib'
#LAT = -23.29  # Francisco Morato

# ✅ Caminho absoluto baseado no diretório atual do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_MODELO = os.path.join(BASE_DIR, NOME_DO_MODELO)
CAMINHO_FEATURES = os.path.join(BASE_DIR, NOME_FEATURES)


# --- 1. Carregar Modelo e Features ---
@st.cache_resource
def load_resources():
    """Carrega o modelo e a lista de features."""
    try:
        model = joblib.load(CAMINHO_MODELO)
        feature_cols = joblib.load(CAMINHO_FEATURES)
        return model, feature_cols
    except FileNotFoundError:
        st.error(f"❌ Arquivo do modelo ou das features não encontrado.\nVerifique se '{NOME_DO_MODELO}' e '{NOME_FEATURES}' estão na pasta correta.")
        return None, None


# --- 2. Carregamento dos recursos ---
model, feature_cols = load_resources()

# --- Carregamento da Chave de API de forma segura ---
try:
    # A chave é lida do arquivo .streamlit/secrets.toml
    API_KEY_TEMPO = st.secrets["api"]["chave_tempo"] 
except (KeyError, FileNotFoundError):
    st.error("❌ Erro de Configuração: Chave de API ('api.chave_tempo') não encontrada no `secrets.toml`.")
    st.warning("Certifique-se de que o arquivo `.streamlit/secrets.toml` existe e contém a chave.")
    st.stop() # Interrompe a execução para evitar chamadas à API sem chave
    

# --- 3. Interface principal ---
if model and feature_cols:
    st.set_page_config(page_title="Preditor de Enchentes", layout="centered")
    
    # Define o CSS para a cor de fundo e borda
    st.markdown(f"""
                <div style="background:linear-gradient(145deg,#ebe7e7,#ffffff);
                            color:dark-gray;padding:20px;border-radius:15px;
                            text-align:center;box-shadow:0 5px 15px rgba(128,128,128,128.2);">
                    <h1>🌧️Preditor de Alagamentos🌧️</h1>
                    <h2>Francisco Morato</h1>
                    <p>Modelo XGBoost - Projeto Integrador IV</p>
                </div>
                """, unsafe_allow_html=True)
    
    
    # --- Fundo azul - claro ---
    st.markdown("""
    <style>
        .stApp {
            background-color: #d5e2fb; /* Fundo azul - claro */
        }
    </style>
    """, unsafe_allow_html=True)

    # Botão de ação
    if st.button("Consultar Risco de Enchente Agora", type="primary"):
        with st.spinner('🔄 Buscando dados meteorológicos e calculando risco...'):
            
          # --- 4. Obter dados da API ---
            # Chamada injetando a chave de API e usando as coordenadas do módulo de dados
            status, features_dict, meteo_data = get_real_time_features(
                api_key=API_KEY_TEMPO, # INJEÇÃO DA CHAVE
                lat=LAT_FM,            # Uso da constante do módulo de dados
                lon=LON_FM             # Uso da constante do módulo de dados (melhora a legibilidade)
            )

            # --- 5. Exibir informações do tempo ---
            st.markdown(f"### 📍 Francisco Morato, BR — {meteo_data['descricao'].capitalize()}")

            # --- CSS para cards ---
            st.markdown("""
            <style>
            .weather-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 15px;
                margin-top: 10px;
            }

            /* Estilo geral dos cards */
            .weather-card {
                background: linear-gradient(145deg, #ebe7e7, #ffffff);
                border-radius: 20px;
                padding: 15px;
                color: dark-gray;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                transition: transform 0.2s ease-in-out;
            }

            .weather-card:hover {
                transform: scale(1.05);
            }

            /* Card especial: Temperatura Atual */
            .weather-card.main {
                background: linear-gradient(145deg, #1e3a8a, #274bba); /* Azul escuro */
                grid-column: span 4; /* Ocupa mais espaço */
                color: white;
                font-size: 1.1em;
                box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            }

            .weather-card h2 {
                font-size: 1.6em;
                margin: 0;
            }

            .weather-card p {
                margin: 5px 0;
                font-size: 0.95em;
            }

            /* Responsividade */
            @media (max-width: 600px) {
                .weather-card.main {
                    grid-column: span 1;
                }
                .weather-card h2 {
                    font-size: 1.3em;
                }
                .weather-card p {
                    font-size: 0.85em;
                }
            }
            </style>
            """, unsafe_allow_html=True)

            # --- Layout dos cards ---
            st.markdown(f"""
            <div class="weather-grid">
                <div class="weather-card main">
                    <h2>🌡️{meteo_data['temp_atual']}°C</h2>
                    <p><b>Temperatura Atual</b></p>
                </div>
                <div class="weather-card">
                    <h2>⬆️{meteo_data['temp_max']}°C</h2>
                    <p><b>Temp. Máxima (24h)</b></p>
                </div>
                <div class="weather-card">
                    <h2>⬇️{meteo_data['temp_min']}°C</h2>
                    <p><b>Temp. Mínima (24h)</b></p>
                </div>
                <div class="weather-card">
                    <h2>💧{meteo_data['umidade']}%</h2>
                    <p><b>Umidade</b></p>
                </div>
                <div class="weather-card">
                    <h2>🌧️{meteo_data['prob_chuva_24h']}%</h2>
                    <p><b>Prob. de Chuva (24h)</b></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # --- 6. Preparar dados para predição ---
            try:
                feature_values = [features_dict[col] for col in feature_cols]
                X_infer = np.array(feature_values).reshape(1, -1)
            except KeyError as e:
                st.error(f"⚠️ Erro: coluna ausente {e}. Verifique api_data_collector.py.")
                st.stop()

            # --- 7. Predição do modelo ---
            proba_enchente = model.predict_proba(X_infer)[0, 1]
            risco_enchente = proba_enchente >= THRESHOLD
            prob_percent = proba_enchente * 100

            # --- 8. Exibir resultado da predição ---
            st.subheader("🧠 Resultado da Predição de alagamento")
            
            if risco_enchente:
                st.markdown(f"""
                <div style="background:linear-gradient(145deg,#ff4b4b,#ff7c7c);
                            color:white;padding:20px;border-radius:15px;
                            text-align:center;box-shadow:0 5px 15px rgba(0,0,0,0.2);">
                    <h2>⚠️ RISCO ALTO DE ALAGAMENTO</h2>
                    <h3>{prob_percent:.1f}% de probabilidade</h3>
                    <p>O modelo superou o limite de alerta (<b>55%</b>).
                    Inicie medidas preventivas e mantenha-se atento às atualizações.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:linear-gradient(145deg,#44c776,#6de091);
                            color:white;padding:20px;border-radius:15px;
                            text-align:center;box-shadow:0 5px 15px rgba(0,0,0,0.2);">
                    <h2>✅ RISCO BAIXO/MODERADO</h2>
                    <h3>{prob_percent:.1f}% de probabilidade</h3>
                    <p>A probabilidade está abaixo do limite de alerta. Continue monitorando o clima.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # --- 9. Exibir features do modelo ---
            with st.expander("📊 Ver detalhes das variáveis utilizadas"):
                df_features = pd.DataFrame([features_dict]).T.rename(columns={0: 'Valor Calculado'})
                st.dataframe(df_features)

else:
    st.error("❌ O modelo ou as features não foram carregados corretamente.")
