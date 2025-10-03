import requests

def baixar_dados_cemaden(estacao_id=7217, caminho_saida='data/raw/cemaden_7217.csv'):
    """
    Baixa os dados da estação CEMADEN de Suzano (ID 7217) e salva em um arquivo CSV.

    Args:
        estacao_id (int): ID da estação CEMADEN (default: 7217 - Suzano).
        caminho_saida (str): Caminho para salvar o arquivo CSV.
    """
    url = f'https://cemaden.gov.br/api/chuva/{estacao_id}/dados'  # Exemplo de endpoint, ajuste conforme necessário

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
        with open(caminho_saida, 'wb') as f:
            f.write(resposta.content)
        print(f'Dados salvos em {caminho_saida}')
    except Exception as e:
        print(f'Erro ao baixar dados: {e}')

# Exemplo de uso:
# baixar_dados_cemaden()