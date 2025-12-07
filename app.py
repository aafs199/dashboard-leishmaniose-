import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Leishmaniose Visceral - BH",
    page_icon="🏥",
    layout="wide"
)

# CABEÇALHO
st.title("🏥 PAINEL LEISHMANIOSE VISCERAL")
st.subheader("Belo Horizonte • Monitoramento Epidemiológico • 1994-2025")
st.markdown("---")

# FUNÇÃO PARA LIMPAR COLUNAS UNNAMED
def limpar_colunas_unnamed(df):
    """Remove colunas Unnamed e linhas/colunas vazias"""
    if df is None or df.empty:
        return df
    
    # Fazer uma cópia
    df = df.copy()
    
    # 1. Remover colunas completamente vazias
    df = df.dropna(axis=1, how='all')
    
    # 2. Renomear colunas Unnamed ou vazias
    novos_nomes = {}
    for i, col in enumerate(df.columns):
        col_str = str(col)
        if 'unnamed' in col_str.lower() or pd.isna(col) or col_str.strip() == '' or col_str == 'None' or col_str == 'nan':
            # Tentar usar primeira linha não-vazia como nome
            if len(df) > 0:
                primeira_linha_nao_vazia = None
                for val in df.iloc[:, i]:
                    if pd.notna(val) and str(val).strip() != '':
                        primeira_linha_nao_vazia = str(val).strip()
                        break
                
                if primeira_linha_nao_vazia and 'unnamed' not in primeira_linha_nao_vazia.lower():
                    novos_nomes[col] = primeira_linha_nao_vazia
                else:
                    novos_nomes[col] = f'Coluna_{i+1}'
            else:
                novos_nomes[col] = f'Coluna_{i+1}'
    
    if novos_nomes:
        df = df.rename(columns=novos_nomes)
    
    # 3. Remover linhas completamente vazias
    df = df.dropna(how='all')
    
    # 4. Remover espaços em branco nos nomes das colunas
    df.columns = [str(col).strip() for col in df.columns]
    
    return df

# FUNÇÃO PARA PROCESSAR DADOS
def carregar_dados(arquivo):
    if arquivo is not None:
        try:
            # Tentar diferentes formas de ler o arquivo
            try:
                # Primeira tentativa: ler normalmente
                df = pd.read_excel(arquivo)
            except:
                # Segunda tentativa: sem cabeçalho
                df = pd.read_excel(arquivo, header=None)
            
            # Aplicar limpeza
            df = limpar_colunas_unnamed(df)
            
            # Se ainda tiver colunas Unnamed, tentar mais limpeza
            colunas_unnamed = [col for col in df.columns if 'unnamed' in str(col).lower()]
            if colunas_unnamed:
                # Tentar usar segunda linha como cabeçalho
                if len(df) > 1:
                    # Verificar se a segunda linha tem dados bons
                    segunda_linha = df.iloc[1]
                    tem_dados_validos = False
                    for val in segunda_linha:
                        if pd.notna(val) and str(val).strip() != '':
                            tem_dados_validos = True
                            break
                    
                    if tem_dados_validos:
                        df.columns = df.iloc[1]
                        df = df[2:].reset_index(drop=True)
                        df = limpar_colunas_unnamed(df)
            
            return df
            
        except Exception as e:
            st.error(f"Erro ao ler {arquivo.name}: {str(e)[:200]}")
            return None
    return None

# MENU LATERAL
with st.sidebar:
    st.header("📁 CARREGAR DADOS")
    
    st.markdown("**Faça upload dos arquivos Excel:**")
    
    # Upload dos arquivos
    arquivo1 = st.file_uploader("Dados Humanos (incidencialetalidadelv.xlsx)", type="xlsx", key="upload1")
    arquivo2 = st.file_uploader("Dados por Regional (casoshumanoslvregional.xlsx)", type="xlsx", key="upload2")
    arquivo3 = st.file_uploader("Dados Caninos (anual 2014-2023.xlsx)", type="xlsx", key="upload3")
    
    st.markdown("---")
    st.info("💡 **Dica:** O sistema limpa automaticamente colunas 'Unnamed'")

# CARREGAR DADOS
dados_humanos = carregar_dados(arquivo1) if arquivo1 else None
dados_regionais = carregar_dados(arquivo2) if arquivo2 else None
dados_caninos = carregar_dados(arquivo3) if arquivo3 else None

# VERIFICAR SE ALGUM DADO FOI CARREGADO
dados_carregados = False

if dados_humanos is not None and isinstance(dados_humanos, pd.DataFrame) and not dados_humanos.empty:
    dados_carregados = True
elif dados_regionais is not None and isinstance(dados_regionais, pd.DataFrame) and not dados_regionais.empty:
    dados_carregados = True  
elif dados_caninos is not None and isinstance(dados_caninos, pd.DataFrame) and not dados_caninos.empty:
    dados_carregados = True

# SEÇÃO 1: TELA INICIAL (SEM DADOS)
if not dados_carregados:
    st.markdown("## 👋 Bem-vindo ao Painel de Monitoramento!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 **Como usar:**
        1. **Na barra lateral à esquerda ←**
        2. **Clique em 'Browse files'**
        3. **Selecione seus arquivos Excel**
        4. **Os gráficos aparecerão automaticamente**
        
        ### 🔧 **Limpeza automática:**
        - Remove colunas 'Unnamed'
        - Remove linhas/colunas vazias
        - Corrige nomes de colunas
        """)
    
    with col2:
        st.markdown("""
        ### 📁 **Arquivos necessários:**
        - `incidencialetalidadelv.xlsx`
        - `casoshumanoslvregional.xlsx`  
        - `anual 2014-2023.xlsx`
        
        ### 🎯 **Funcionalidades:**
        - 📈 Gráficos interativos
        - 🧹 Limpeza automática de dados
        - 📊 Indicadores em tempo real
        - 📥 Download dos dados limpos
        """)
    
    st.markdown("---")
    st.success("🚀 **Comece carregando seus dados na barra lateral!**")

# SEÇÃO 2: SE HOUVER DADOS CARREGADOS
else:
    # MOSTRAR INFORMAÇÕES SOBRE A LIMPEZA
    if dados_humanos is not None:
        colunas_originais = len(pd.read_excel(arquivo1).columns) if arquivo1 else 0
        colunas_limpas = len(dados_humanos.columns)
        if colunas_originais > colunas_limpas:
            st.success(f"✅ Limpeza aplicada: {colunas_originais - colunas_limpas} colunas 'Unnamed' removidas")
    
    # INDICADORES PRINCIPAIS
    st.markdown("## 📊 INDICADORES-CHAVE")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Período", "1994-2025")
    
    with col2:
        if dados_humanos is not None and not dados_humanos.empty:
            # Procurar coluna numérica para somar (casos)
            for col in dados_humanos.columns:
                if pd.api.types.is_numeric_dtype(dados_humanos[col]):
                    try:
                        total = int(dados_humanos[col].sum())
                        st.metric("🦠 Total de Casos", f"{total:,}")
                        break
                    except:
                        continue
            else:
                st.metric("🦠 Total de Casos", "N/A")
        else:
            st.metric("🦠 Total de Casos", "Carregue dados")
    
    with col3:
        if dados_regionais is not None and not dados_regionais.empty:
            num_regionais = len(dados_regionais)
            st.metric("🗺️ Regionais", num_regionais)
        else:
            st.metric("🗺️ Regionais", "Carregue dados")
    
    with col4:
        st.metric("📈 Status", "Ativo")
    
    st.markdown("---")
    
    # MOSTRAR NOMES DAS COLUNAS LIMPAS
    if dados_humanos is not None:
        st.info(f"📋 Colunas disponíveis nos dados humanos: {', '.join(dados_humanos.columns[:5])}{'...' if len(dados_humanos.columns) > 5 else ''}")
    
    # GRÁFICOS
    st.markdown("## 📈 VISUALIZAÇÕES")
    
    # GRÁFICO 1: DADOS HUMANOS
    if dados_humanos is not None and not dados_humanos.empty:
        st.markdown("### 📊 Evolução Temporal")
        
        # Selecionar colunas para o gráfico
        col1_graph, col2_graph = st.columns(2)
        
        with col1_graph:
            # Procurar coluna de ano
            coluna_ano_opcoes = []
            for col in dados_humanos.columns:
                # Verificar se a coluna parece ter anos
                try:
                    valores = dados_humanos[col].dropna()
                    if len(valores) > 0:
                        # Verificar se valores estão na faixa de anos
                        valores_numericos = pd.to_numeric(valores, errors='coerce').dropna()
                        if len(valores_numericos) > 0:
                            min_val = valores_numericos.min()
                            max_val = valores_numericos.max()
                            if 1900 < min_val < 2100 and 1900 < max_val < 2100:
                                coluna_ano_opcoes.append(col)
                except:
                    continue
            
            if not coluna_ano_opcoes and len(dados_humanos.columns) > 0:
                coluna_ano_opcoes = list(dados_humanos.columns[:3])
            
            coluna_ano = st.selectbox(
                "Selecione a coluna para o eixo X (ano):",
                coluna_ano_opcoes,
                key="coluna_ano"
            )
        
        with col2_graph:
            # Procurar colunas numéricas para o eixo Y
            colunas_numericas = []
            for col in dados_humanos.columns:
                if col != coluna_ano and pd.api.types.is_numeric_dtype(dados_humanos[col]):
                    colunas_numericas.append(col)
            
            if not colunas_numericas and len(dados_humanos.columns) > 1:
                # Tentar converter colunas para numérico
                for col in dados_humanos.columns:
                    if col != coluna_ano:
                        try:
                            pd.to_numeric(dados_humanos[col], errors='coerce')
                            colunas_numericas.append(col)
                        except:
                            continue
            
            coluna_valores = st.selectbox(
                "Selecione a coluna para o eixo Y (valores):",
                colunas_numericas if colunas_numericas else [col for col in dados_humanos.columns if col != coluna_ano][:5],
                key="coluna_valores"
            )
        
        # Criar gráfico
        if coluna_ano and coluna_valores:
            try:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dados_humanos[coluna_ano],
                    y=dados_humanos[coluna_valores],
                    mode='lines+markers',
                    name=coluna_valores,
                    line=dict(color='blue', width=3)
                ))
                
                fig.update_layout(
                    title=f'Evolução: {coluna_valores}',
                    xaxis_title=coluna_ano,
                    yaxis_title=coluna_valores,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao criar gráfico: {str(e)[:100]}")
    
    # GRÁFICO 2: DADOS REGIONAIS
    if dados_regionais is not None and not dados_regionais.empty:
        st.markdown("### 🗺️ Distribuição por Regional")
        
        try:
            # Encontrar coluna de regionais (primeira coluna não totalmente numérica)
            col_regional = None
            for col in dados_regionais.columns:
                if not pd.api.types.is_numeric_dtype(dados_regionais[col]):
                    col_regional = col
                    break
            
            if col_regional is None and len(dados_regionais.columns) > 0:
                col_regional = dados_regionais.columns[0]
            
            # Encontrar colunas numéricas (dados)
            colunas_numericas = []
            for col in dados_regionais.columns:
                if col != col_regional:
                    try:
                        pd.to_numeric(dados_regionais[col], errors='coerce')
                        colunas_numericas.append(col)
                    except:
                        continue
            
            if colunas_numericas and col_regional:
                # Seletor de coluna de dados
                coluna_dados = st.selectbox(
                    "Selecione a coluna de dados:",
                    colunas_numericas,
                    key="coluna_dados_regionais"
                )
                
                # Preparar dados
                df_plot = dados_regionais[[col_regional, coluna_dados]].copy()
                df_plot = df_plot.dropna(subset=[coluna_dados])
                df_plot[coluna_dados] = pd.to_numeric(df_plot[coluna_dados], errors='coerce')
                df_plot = df_plot.dropna(subset=[coluna_dados])
                df_plot = df_plot.sort_values(coluna_dados, ascending=True)
                
                # Criar gráfico de barras
                if not df_plot.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=df_plot[col_regional],
                        x=df_plot[coluna_dados],
                        orientation='h',
                        marker_color='green'
                    ))
                    
                    fig.update_layout(
                        title=f'Distribuição por Regional - {coluna_dados}',
                        xaxis_title=coluna_dados,
                        yaxis_title=col_regional,
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados para a coluna selecionada")
            else:
                st.write("Dados regionais carregados:")
                st.dataframe(dados_regionais.head())
                
        except Exception as e:
            st.error(f"Erro ao processar dados regionais: {str(e)[:100]}")
    
    # SEÇÃO 3: TABELAS DE DADOS LIMPOS
    st.markdown("---")
    st.markdown("## 📋 DADOS LIMPOS (sem colunas Unnamed)")
    
    tabs = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos"])
    
    with tabs[0]:
        if dados_humanos is not None and not dados_humanos.empty:
            st.dataframe(dados_humanos, use_container_width=True)
            
            # Botão para download
            csv = dados_humanos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados humanos limpos (CSV)",
                data=csv,
                file_name="dados_humanos_limpos.csv",
                mime="text/csv"
            )
        else:
            st.info("Carregue dados humanos para ver esta tabela")
    
    with tabs[1]:
        if dados_regionais is not None and not dados_regionais.empty:
            st.dataframe(dados_regionais, use_container_width=True)
            
            csv = dados_regionais.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados regionais limpos (CSV)",
                data=csv,
                file_name="dados_regionais_limpos.csv",
                mime="text/csv"
            )
        else:
            st.info("Carregue dados regionais para ver esta tabela")
    
    with tabs[2]:
        if dados_caninos is not None and not dados_caninos.empty:
            st.dataframe(dados_caninos, use_container_width=True)
            
            csv = dados_caninos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados caninos limpos (CSV)",
                data=csv,
                file_name="dados_caninos_limpos.csv",
                mime="text/csv"
            )
        else:
            st.info("Carregue dados caninos para ver esta tabela")
    
    # RODAPÉ
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        🏥 <strong>Sistema de Monitoramento Epidemiológico</strong><br>
        Dados limpos automaticamente • Desenvolvido para a Secretaria Municipal de Saúde • 2025
    </div>
    """, unsafe_allow_html=True)

# Mensagem de ajuda
st.sidebar.markdown("---")
st.sidebar.caption("🔄 O sistema remove automaticamente colunas 'Unnamed' e linhas vazias")
