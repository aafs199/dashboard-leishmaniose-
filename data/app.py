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
    col = col.replace('CÃES', 'CAES').replace('ÓBITOS', 'OBITOS').replace('POPULAÇÃO', 'POPULACAO')
    return col


@st.cache_data
def carregar_dados_consolidados():
    # 1. SETUP E LISTAGEM
    filenames = glob.glob(DATA_PATH + "*.csv")

    # --- A. CONSOLIDAÇÃO DOS DADOS DE ATIVIDADES DE BH (1994-2024) ---
    # CORREÇÃO FINAL: Usando a verificação de string simples em minúsculas (a mais robusta)
    activity_files = [f for f in filenames if 'anual' in f.lower()]
    
    if not activity_files:
        # Se falhar aqui, o erro No objects to concatenate é acionado.
        raise ValueError("Nenhum arquivo de atividade ('anual' no nome) foi encontrado. Verifique a pasta 'data'.")

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
    incidence_file_list = [f for f in filenames if f.startswith(DATA_PATH + "29-8-25smsa-incidletlv25.8_0.xlsx")]
    if not incidence_file_list:
        raise FileNotFoundError("O arquivo de Incidência/Letalidade (29-8-25smsa...) não foi encontrado na pasta 'data'.")
    
    incidence_file = incidence_file_list[0]
    df_incidence = pd.read_csv(incidence_file, skiprows=40, sep=',', encoding='utf-8')
    df_incidence = df_incidence[df_incidence['Ano'].astype(str).str.match(r'^\d{4}$', na=False)].copy()
    
    df_incidence.columns = [clean_col_name_simple(c) for c in df_incidence.columns]
    df_incidence = df_incidence[['ANO', 'CASOS_INCIDENTES', 'POPULACAO', 'INC_POR_100000_HAB', 'OBITOS_INCIDENTES', 'LETALIDADE_INCIDENTES_%']]
    df_incidence.columns = ['Ano', 'Casos', 'População', 'Incidência_100k', 'Óbitos', 'Letalidade_%']

    for col in df_incidence.columns[1:]:
        df_incidence[col] = pd.to_numeric(df_incidence[col], errors='coerce')


    # --- C. MERGE FINAL E CRIAÇÃO DOS DFs FINAIS ---
    df_humanos = df_incidence.merge(df_activities, on='Ano', how='left')
    
    df_caninos = df_humanos.dropna(subset=['Caes_Soropositivos']).copy()
    df_caninos['Positividade_%'] = (df_caninos['Caes_Soropositivos'] / df_caninos['Sorologias_Realizadas'].replace(0, 1) * 100).round(2)
    df_caninos = df_caninos[['Ano', 'Sorologias_Realizadas', 'Caes_Soropositivos', 'Imoveis_Borrifados', 'Positividade_%']]
    
    df_humanos['Letalidade_%'] = df_humanos['Letalidade_%'].fillna(0)


    # --- D. DADOS REGIONAIS (PROTÓTIPO FIXO PARA O MAPA) ---
    df_reg = pd.DataFrame({
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
        '2024': [1, 0, 1, 0, 0, 0, 0, 0, 0, 0], '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1], '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0], '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1], '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
    })
    
    return df_humanos, df_reg, df_caninos

# -------------------------------------------------------------
# CHAMADA PRINCIPAL DA FUNÇÃO DE CARREGAMENTO
# -------------------------------------------------------------
try:
    dados_humanos, dados_regionais, dados_caninos = carregar_dados_consolidados()
except Exception as e:
    # Se o erro for o "No objects to concatenate", esta mensagem será exibida.
    st.error(f"ERRO CRÍTICO NO CARREGAMENTO DOS DADOS: Verifique se a pasta 'data' existe e contém todos os arquivos CSV originais. Detalhe do Erro: {e}")
    st.stop()

# ... (O restante do código Streamlit que você já tem, Funções de Mapa, Layout, etc., deve vir abaixo) ...
