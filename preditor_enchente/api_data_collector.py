import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Union

# --- CONFIGURAÇÕES FIXAS (Não contêm a chave de API) ---
LAT_FM = -23.29 
LON_FM = -46.73

# Coordenadas dos vizinhos
VIZINHOS: Dict[str, Tuple[float, float]] = {
  'Franco_da_Rocha': (-23.32, -46.73),
  'Caieiras': (-23.36, -46.74),
  'Jundiai': (-23.18, -46.88)
}

# Nomes das features esperadas
EXPECTED_FEATURES = [
  'Chuva_FM_3h', 'Chuva_FM_6h', 'Chuva_FM_12h', 'Chuva_FM_24h', 
  'Chuva_Vizinha_6h', 'Chuva_Vizinha_24h', 'Chuva_FM_Max_1h', 
  'Chuva_Vizinha_Max_1h', 'Chuva_FM_Taxa_Aumento'
]

# Estrutura base para os dados meteorológicos extras
METEO_DATA_TEMPLATE = {
  'temp_atual': np.nan,
  'temp_max': np.nan,
  'temp_min': np.nan,
  'umidade': np.nan,
  'vel_vento': np.nan,
  'prob_chuva_24h': np.nan, 
  'descricao': 'N/D'
}

# --- FUNÇÕES DE REQUISIÇÃO E PROCESSAMENTO ---

def _fetch_current_weather(lat: float, lon: float, api_key: str) -> Dict[str, Union[float, str]]:
  """Busca o tempo atual e retorna dados formatados."""
  url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br"
  
  try:
    response = requests.get(url)
    response.raise_for_status() 
    data = response.json()
    
    main = data.get('main', {})
    weather = data.get('weather', [{}])[0]
    wind = data.get('wind', {})

    return {
      'temp_atual': round(main.get('temp', np.nan), 1),
      'umidade': main.get('humidity', np.nan),
      'vel_vento': round(wind.get('speed', np.nan) * 3.6, 1), 
      'descricao': weather.get('description', 'Dados indisponíveis').capitalize(),
      'temp_max': np.nan, # Será atualizado pelo forecast
      'temp_min': np.nan, # Será atualizado pelo forecast
      'prob_chuva_24h': np.nan, # Será atualizado pelo forecast
    }
  except requests.exceptions.RequestException:
    # Em caso de erro, retorna o template com NANs
    return METEO_DATA_TEMPLATE.copy()


def _fetch_and_process_rain(lat: float, lon: float, api_key: str) -> Union[Tuple[List[float], Dict[str, float]], None]:
  """
  Busca a previsão no endpoint /forecast e simula dados horários.
  Retorna: lista de chuva horária simulada (mm/h) e um dicionário de previsões (Max/Min/Prob).
  """
  url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
  
  try:
    response = requests.get(url)
    response.raise_for_status() 
    data = response.json()
  except requests.exceptions.RequestException:
    return None
  
  hourly_data = data.get('list', []) 
  previsao_chuva = []
  temps = []
  prob_chuva_list = []
  
  # Processa os primeiros 8 registros de 3h (totalizando 24h para Max/Min)
  for item in hourly_data[:8]: 
    main = item.get('main', {})
    temps.append(main.get('temp_max', -999))
    temps.append(main.get('temp_min', 999))
    prob_chuva_list.append(item.get('pop', 0))
  
  # Processa os primeiros 16 registros de 3h (totalizando 48h simuladas para features)
  for item in hourly_data[:16]: 
    rain_mm = item.get('rain', {}).get('3h', 0)
    chuva_horaria_simulada = rain_mm / 3 
    previsao_chuva.extend([chuva_horaria_simulada] * 3)
    
  meteo_forecast = {
    'temp_max': round(max(temps), 1) if temps and max(temps) > -999 else np.nan,
    'temp_min': round(min(temps), 1) if temps and min(temps) < 999 else np.nan,
    'prob_chuva_24h': round(np.mean(prob_chuva_list[:8]) * 100) if prob_chuva_list else np.nan
  }
    
  return previsao_chuva[:48], meteo_forecast


def get_real_time_features(api_key: str, lat: float = LAT_FM, lon: float = LON_FM) -> Tuple[str, Union[Dict[str, float], None], Union[Dict[str, Union[float, str]], None]]:
  """
  Função principal. Busca dados, calcula features de ML e retorna status/resultados.
  """
  
  # 1. Obter DADOS METEOROLÓGICOS ATUAIS
  # Chama a função auxiliar, PASSANDO a chave de API
  meteo_data = _fetch_current_weather(lat, lon, api_key)

  # 2. Obter Previsão de Chuva para Francisco Morato (FM) e Max/Min
  fm_result = _fetch_and_process_rain(lat, lon, api_key)
  
  if fm_result is None:
    return "Falha ao obter dados /forecast para Francisco Morato.", None, meteo_data
  
  previsao_fm, meteo_forecast = fm_result
  
  # Adicionar Max/Min e Probabilidade do forecast aos dados meteo
  meteo_data.update(meteo_forecast)

  if len(previsao_fm) < 24: 
    return "Previsão incompleta para FM (menos de 24h calculadas).", None, meteo_data
  
  # 3. Obter Previsão de Chuva para Vizinhos (Lógica de média mantida)
  all_vizinhos_rain: List[List[float]] = []
  
  for _, (v_lat, v_lon) in VIZINHOS.items():
    vizinho_result = _fetch_and_process_rain(v_lat, v_lon, api_key)
    
    if vizinho_result is None: continue
    
    previsao_vizinho, _ = vizinho_result
    if len(previsao_vizinho) == 48:
      all_vizinhos_rain.append(previsao_vizinho)

  if not all_vizinhos_rain:
    previsao_vizinha_media = previsao_fm
  else:
    vizinhos_array = np.array(all_vizinhos_rain)
    previsao_vizinha_media = np.mean(vizinhos_array, axis=0).tolist()


  # --- ENGENHARIA DE FEATURES ---
  df_fm = pd.Series(previsao_fm).to_frame(name='Chuva_Horaria_FM')
  features: Dict[str, float] = {}

  # Acumulados de FM
  features['Chuva_FM_3h'] = df_fm['Chuva_Horaria_FM'].rolling(window=3).sum().iloc[-1]
  features['Chuva_FM_6h'] = df_fm['Chuva_Horaria_FM'].rolling(window=6).sum().iloc[-1]
  features['Chuva_FM_12h'] = df_fm['Chuva_Horaria_FM'].rolling(window=12).sum().iloc[-1]
  features['Chuva_FM_24h'] = df_fm['Chuva_Horaria_FM'].rolling(window=24).sum().iloc[-1]
  features['Chuva_FM_Max_1h'] = df_fm['Chuva_Horaria_FM'].max() 
  
  # Taxa de Aumento
  chuva_24h = features['Chuva_FM_24h']
  chuva_6h = features['Chuva_FM_6h']
  # Evita divisão por zero: se a diferença for muito pequena, considera a taxa 0.0
  features['Chuva_FM_Taxa_Aumento'] = chuva_6h / (chuva_24h - chuva_6h) if (chuva_24h - chuva_6h) > 0.01 else 0.0

  # Acumulados de Vizinhos
  df_vizinhos = pd.Series(previsao_vizinha_media).to_frame(name='Chuva_Horaria_Vizinha')
  features['Chuva_Vizinha_6h'] = df_vizinhos['Chuva_Horaria_Vizinha'].rolling(window=6).sum().iloc[-1]
  features['Chuva_Vizinha_24h'] = df_vizinhos['Chuva_Horaria_Vizinha'].rolling(window=24).sum().iloc[-1]
  features['Chuva_Vizinha_Max_1h'] = df_vizinhos['Chuva_Horaria_Vizinha'].max() 
  
  # Monta o dicionário de features na ordem correta
  final_features = {k: features.get(k, 0.0) for k in EXPECTED_FEATURES}
  
  return "Sucesso", final_features, meteo_data