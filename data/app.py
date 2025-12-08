import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import glob
import re

# ============================================
# FUNÇÕES DE SUPORTE E CARREGAMENTO DE DADOS ESCALÁVEL
# ============================================

# Define o caminho para a pasta de dados
DATA_PATH = "data/"

# Função para limpeza de colunas (necessária devido a acentuação e espaços)
def clean_col_name_simple(col):
    col = str(col).strip().upper()
    col = col.replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('/', '_')
    # Tratamento da acentuação:
    col = col.replace('CÃES', 'CAES').replace('ÓBITOS', 'OBITOS').replace('POPULAÇÃO', 'POPULACAO')
    return col


@st.cache_data
def carregar_dados_consolidados():
    # 1. SETUP E LISTAGEM
    filenames = glob.glob(DATA_PATH + "*.csv")

    # --- A. CONSOLIDAÇÃO DOS DADOS DE ATIVIDADES DE BH (1994-2024) ---
    # CORREÇÃO: Usa a verificação mais robusta (minúsculas) para capturar os 6 arquivos 'anual'.
    activity_files = [f for f in filenames if 'anual' in f.lower()]
    
    if not activity_files:
        raise ValueError("Nenhum arquivo de atividade ('anual' no nome) foi encontrado na pasta 'data'.")

    df_activities_list = []

    for file_name in activity_files:
        try:
            df_temp = pd.read_csv(file_name, sep=',', encoding='utf-8')
            df_temp.columns = [clean_col_name_simple(c) for c in df_temp.columns]
            df_temp = df_temp[~df_temp['ANO'].astype(str).str.contains('TOTAL', case=False, na=False)]
            df_activities_list.append(df_temp)
        except Exception: pass
            
    df_activities = pd.concat(df_activities_list, ignore_index=True).drop_duplicates(subset=['ANO'])
    df_activities.columns = ['Ano', 'Sorologias_Realizadas', 'Caes_Soropositivos', 'Caes_Eutanasiados', 'Imoveis_Borrifados']
    
    for col in df_activities.columns[1:]:
        df_activities[col] = pd.to_numeric(df_activities[col], errors='coerce')


    # --- B. CONSOLIDAÇÃO DOS DADOS DE INCIDÊNCIA E LETALIDADE (BH) ---
    # CORREÇÃO: Busca pelo NOVO nome do arquivo: 'incidencialetalidadelv.xlsx'
    incidence_file_list = [f for f in filenames if "incidencialetalidadelv.xlsx" in f]
    if not incidence_file_list:
        raise FileNotFoundError("O arquivo de Incidência/Letalidade (incidencialetalidadelv.xlsx) não foi encontrado na pasta 'data'.")
    
    incidence_file = incidence_file_list[0]
    # O arquivo tem 39 linhas de cabeçalho (skiprows=40)
    df_incidence = pd.read_csv(incidence_file, skiprows=40, sep=',', encoding='utf-8')
    df_incidence = df_incidence[df_incidence['Ano'].astype(str).str.match(r'^\d{4}$', na=False)].copy()
    
    df_incidence.columns = [clean_col_name_simple(c) for c in df_incidence.columns]
    df_incidence = df_incidence[['ANO', 'CASOS_INCIDENTES', 'POPULACAO', 'INC_POR_100000_HAB', 'OBITOS_INCIDENTES', 'LETALIDADE_INCIDENTES_%']]
    df_incidence.columns = ['Ano', 'Casos', 'População', 'Incidência_100k', 'Óbitos', 'Letalidade_%']

    for col in df_incidence.columns[1:]:
        df_incidence[col] = pd.to_numeric(df_incidence[col], errors='coerce')


    # --- C. CONSOLIDAÇÃO DOS DADOS REGIONAIS ---
    # CORREÇÃO: Busca pelo NOVO nome do arquivo: 'casoshumanoslvregional.xlsx'
    regional_file_list = [f for f in filenames if "casoshumanoslvregional.xlsx" in f]
    
    if not regional_file_list:
        # Se falhar, usa o protótipo fixo (fallback).
        df_reg = pd.DataFrame({
            'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
            '2024': [1, 0, 1, 0, 0, 0, 0, 0, 0, 0], '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1], '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0], '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1], '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
        })
    else:
        regional_file = regional_file_list[0]
        df_reg = pd.read_csv(regional_file, sep=',', encoding='utf-8')
        
        # Limpeza de colunas (remoção de *, ** e espaços)
        df_reg.columns = [re.sub(r'[^\d\w\s]', '', col).strip() for col in df_reg.columns]
        df_reg = df_reg.rename(columns={'REGIONAL': 'Regional'})
        
        # Seleciona a coluna Regional e todas as colunas que são anos (dígitos)
        df_reg = df_reg.loc[:, ['Regional'] + [c for c in df_reg.columns if c.isdigit()]]
        
        # Converte colunas de ano para numérico
        for col in [c for c in df_reg.columns if c.isdigit()]:
             df_reg[col] = pd.to_numeric(df_reg[col], errors='coerce').fillna(0).astype(int)


    # --- D. MERGE E CRIAÇÃO DOS DFs HUMANOS E CANINOS ---
    df_humanos = df_incidence.merge(df_activities, on='Ano', how='left')
    
    df_caninos = df_humanos.dropna(subset=['Caes_Soropositivos']).copy()
    df_caninos['Positividade_%'] = (df_caninos['Caes_Soropositivos'] / df_caninos['Sorologias_Realizadas'].replace(0, 1) * 100).round(2)
    df_caninos = df_caninos[['Ano', 'Sorologias_Realizadas', 'Caes_Soropositivos', 'Imoveis_Borrifados', 'Positividade_%']]
    
    df_humanos['Letalidade_%'] = df_humanos['Letalidade_%'].fillna(0)
        
    return df_humanos, df_reg, df_caninos

# -------------------------------------------------------------
# CHAMADA PRINCIPAL DA FUNÇÃO DE CARREGAMENTO
# -------------------------------------------------------------
try:
    dados_humanos, dados_regionais, dados_caninos = carregar_dados_consolidados()
except Exception as e:
    st.error(f"ERRO CRÍTICO NO CARREGAMENTO DOS DADOS: Verifique se a pasta 'data' existe e contém todos os arquivos CSV originais. Detalhe do Erro: {e}")
    st.stop()


# ============================================
# FUNÇÃO DE MAPA E CONSTANTES DE LAYOUT
# (O restante do código de layout, CSS e gráficos permanece o mesmo.)
# ============================================

# Dicionário de cores para a graduação AMARELO -> VERMELHO (Risco)
COLOR_MAP_RISK = {
    'Baixo': '#ffeda0',
    'Médio': '#feb24c',
    'Alto': '#e31a1c'   
}
# Coordenadas aproximadas das regionais de BH (necessárias para o mapa)
coordenadas_regionais = {
    'Barreiro': {'lat': -19.9667, 'lon': -44.0333},
    'Centro Sul': {'lat': -19.9333, 'lon': -43.9333},
    'Leste': {'lat': -19.8833, 'lon': -43.8833},
    'Nordeste': {'lat': -19.8500, 'lon': -43.9167},
    'Noroeste': {'lat': -19.9000, 'lon': -43.9667},
    'Norte': {'lat': -19.8500, 'lon': -43.9667},
    'Oeste': {'lat': -19.9167, 'lon': -43.9500},
    'Pampulha': {'lat': -19.8500, 'lon': -43.9833},
    'Venda Nova': {'lat': -19.8167, 'lon': -43.9500},
    'Ignorado': {'lat': -19.9167, 'lon': -43.9333}
}


def criar_mapa_interativo(ano_selecionado, mostrar_nomes, filtro_risco):
    
    map_data = []
    
    # Verifica se a coluna do ano existe nos dados regionais antes de iterar
    if ano_selecionado not in dados_regionais.columns:
         st.warning(f"Atenção: Dados regionais para o ano {ano_selecionado} não estão disponíveis.")
         return None

    for idx, row in dados_regionais.iterrows():
        regional = row['Regional']
        if regional == 'Ignorado': continue
        
        coords = coordenadas_regionais.get(regional)
        lat, lon = coords['lat'], coords['lon']
        casos = row[ano_selecionado]
        
        if casos <= 1: risco_label = "Baixo (0-1 casos)"
        elif casos <= 4: risco_label = "Médio (2-4 casos)"
        else: risco_label = "Alto (5+ casos)"
        
        if risco_label not in filtro_risco: continue
            
        tamanho = 10 + (casos * 4) 
        
        map_data.append({
            'Regional': regional,
            'Latitude': lat,
            'Longitude': lon,
            'Casos': casos,
            'Risco': risco_label,
            'Tamanho': tamanho,
            'Cor_Hex': COLOR_MAP_RISK[risco_label.split(' ')[0]],
            'Texto_Hover': f"<b>{regional}</b><br>Casos em {ano_selecionado}: {casos}<br>Nível de Risco: {risco_label}"
        })
    
    df_map = pd.DataFrame(map_data)
    if df_map.empty: return None
    
    fig = px.scatter_mapbox(
        df_map,
        lat='Latitude',
        lon='Longitude',
        size='Tamanho',
        color='Risco',
        color_discrete_map={
            "Baixo (0-1 casos)": COLOR_MAP_RISK['Baixo'],
            "Médio (2-4 casos)": COLOR_MAP_RISK['Médio'],
            "Alto (5+ casos)": COLOR_MAP_RISK['Alto']
        },
        hover_name='Regional',
        custom_data=['Texto_Hover'],
        title=f'Distribuição de Casos por Regional - {ano_selecionado}',
        zoom=10,
        height=600
    )
    
    fig.update_layout(
        mapbox_style="carto-positron", 
        mapbox_zoom=10,
        mapbox_center={"lat": -19.9167, "lon": -43.9333},
        margin={"r":0,"t":40,"l":0,"b":0
