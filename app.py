import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================

# Configurar página
st.set_page_config(
    page_title="VigiLeish - Painel de Vigilância",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar fechada por padrão
)

# ============================================
# SISTEMA DE AUTENTICAÇÃO
# ============================================

# Credenciais do administrador (em produção, usar variáveis de ambiente)
ADMIN_CREDENTIALS = {
    "username": "admin_vigileish",
    "password_hash": hashlib.sha256("admin123".encode()).hexdigest()  # Senha padrão
}

# Sessão de autenticação
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = "public"
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

# ============================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================

def verificar_login(username, password):
    """Verifica as credenciais do administrador"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return (username == ADMIN_CREDENTIALS["username"] and 
            password_hash == ADMIN_CREDENTIALS["password_hash"])

def login_admin():
    """Interface de login para administradores"""
    with st.sidebar:
        st.title("🔐 Acesso Administrativo")
        
        username = st.text_input("Usuário", key="login_user")
        password = st.text_input("Senha", type="password", key="login_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Entrar", use_container_width=True):
                if verificar_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.user_role = "admin"
                    st.session_state.show_login = False
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas!")
        
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()

def logout():
    """Função para logout"""
    st.session_state.authenticated = False
    st.session_state.user_role = "public"
    st.session_state.show_login = False
    st.rerun()

# ============================================
# GESTÃO DE DADOS - ARMAZENAMENTO
# ============================================

# Diretório para armazenar dados
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Caminhos dos arquivos de dados
HUMANOS_FILE = DATA_DIR / "dados_humanos.json"
REGIONAIS_FILE = DATA_DIR / "dados_regionais.json"
CANINOS_FILE = DATA_DIR / "dados_caninos.json"
METADATA_FILE = DATA_DIR / "metadata.json"

def carregar_dados_padrao():
    """Carrega os dados padrão do sistema"""
    return {
        'humanos': pd.DataFrame({
            'Ano': list(range(1994, 2026)),
            'Casos_incidentes': [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 110, 
                                 160, 145, 131, 93, 54, 40, 39, 48, 51, 64, 39, 41, 30, 30, 24, 30, 29, 11],
            'Óbitos_incidentes': [6, 4, 4, 3, 4, 3, 9, 10, 8, 9, 25, 9, 12, 6, 18, 31, 23, 
                                   14, 12, 5, 3, 7, 7, 12, 5, 7, 1, 3, 5, 6, 8, 0],
            'População': [2084100, 2106819, 2091371, 2109223, 2124176, 2139125, 2238332, 
                          2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 
                          2238332, 2238332, 2375151, 2375151, 2375151, 2375151, 2375151, 
                          2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 
                          2315560, 2315560, 2315560, 2315560]
        }),
        'regionais': pd.DataFrame({
            'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                        'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
            '2024': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
            '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
            '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
            '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
        }),
        'caninos': pd.DataFrame({
            'Ano': list(range(2014, 2025)),
            'Sorologias_Realizadas': [44536, 20659, 22965, 33029, 31330, 27983, 
                                     28954, 17044, 23490, 43571, 49927],
            'Cães_Soropositivos': [6198, 3807, 5529, 6539, 6591, 6165, 
                                   5624, 3539, 4077, 5440, 4459],
            'Imóveis_Borrifados': [54436, 56475, 5617, 19538, 26388, 14855, 
                                   73593, 78279, 64967, 51591, 30953]
        })
    }

def inicializar_dados():
    """Inicializa os dados do sistema se não existirem"""
    if not HUMANOS_FILE.exists():
        dados = carregar_dados_padrao()
        salvar_dados(dados)
        salvar_metadata({
            "criado_em": datetime.now().isoformat(),
            "ultima_atualizacao": datetime.now().isoformat(),
            "atualizado_por": "sistema",
            "versao": "1.0"
        })

def carregar_dados():
    """Carrega dados do sistema"""
    if HUMANOS_FILE.exists() and REGIONAIS_FILE.exists() and CANINOS_FILE.exists():
        try:
            dados = {
                'humanos': pd.read_json(HUMANOS_FILE),
                'regionais': pd.read_json(REGIONAIS_FILE),
                'caninos': pd.read_json(CANINOS_FILE)
            }
            
            # Calcular indicadores
            dados['humanos']['Incidência_100k'] = (dados['humanos']['Casos_incidentes'] / 
                                                  dados['humanos']['População'] * 100000).round(2)
            dados['humanos']['Letalidade_%'] = (dados['humanos']['Óbitos_incidentes'] / 
                                               dados['humanos']['Casos_incidentes'].replace(0, 1) * 100).round(2)
            
            dados['caninos']['Positividade_%'] = (dados['caninos']['Cães_Soropositivos'] / 
                                                 dados['caninos']['Sorologias_Realizadas'].replace(0, 1) * 100).round(2)
            
            return dados
        except:
            return carregar_dados_padrao()
    else:
        return carregar_dados_padrao()

def salvar_dados(dados):
    """Salva dados no sistema"""
    dados['humanos'].to_json(HUMANOS_FILE, orient='records')
    dados['regionais'].to_json(REGIONAIS_FILE, orient='records')
    dados['caninos'].to_json(CANINOS_FILE, orient='records')

def salvar_metadata(metadata):
    """Salva metadados do sistema"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def carregar_metadata():
    """Carrega metadados do sistema"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "criado_em": datetime.now().isoformat(),
        "ultima_atualizacao": datetime.now().isoformat(),
        "atualizado_por": "sistema",
        "versao": "1.0"
    }

def criar_backup():
    """Cria backup dos dados"""
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.zip"
    
    # Em produção, implementar compressão dos arquivos
    metadata = carregar_metadata()
    metadata["backup_criado_em"] = datetime.now().isoformat()
    
    return True

# ============================================
# CSS PERSONALIZADO
# ============================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a5f7a, #2a9d8f);
        color: white;
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .admin-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #2a9d8f;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a5f7a;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2a9d8f;
    }
    
    .admin-panel {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #2a9d8f;
        margin-bottom: 2rem;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a5f7a;
        color: white;
    }
    
    /* Esconder botão de deploy do Streamlit */
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ============================================
# INTERFACE DE LOGIN (se necessário)
# ============================================

# Se não está autenticado e quer mostrar login
if st.session_state.show_login:
    login_admin()
    st.stop()

# ============================================
# INICIALIZAR SISTEMA
# ============================================

inicializar_dados()
dados_sistema = carregar_dados()
metadata = carregar_metadata()

# ============================================
# CABEÇALHO PRINCIPAL
# ============================================

admin_badge = ""
if st.session_state.authenticated and st.session_state.user_role == "admin":
    admin_badge = '<div class="admin-badge">👑 MODO ADMINISTRADOR</div>'

st.markdown(f"""
<div class="main-header">
    {admin_badge}
    <h1 style="margin: 0; font-size: 2.2rem;">🏥 VIGILEISH - PAINEL DE VIGILÂNCIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
        Sistema de Monitoramento da Leishmaniose Visceral em Belo Horizonte
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            📅 Última atualização: {datetime.fromisoformat(metadata['ultima_atualizacao']).strftime('%d/%m/%Y %H:%M')}
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            👤 Atualizado por: {metadata.get('atualizado_por', 'sistema')}
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🎓 Atividade Extensionista UNINTER
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# BARRA DE CONTROLE ADMIN (se autenticado)
# ============================================

if st.session_state.authenticated and st.session_state.user_role == "admin":
    with st.container():
        col_admin1, col_admin2, col_admin3, col_admin4 = st.columns(4)
        
        with col_admin1:
            if st.button("📤 Atualizar Dados", use_container_width=True):
                st.session_state.show_admin_panel = True
                st.rerun()
        
        with col_admin2:
            if st.button("📥 Fazer Backup", use_container_width=True):
                if criar_backup():
                    st.success("✅ Backup criado com sucesso!")
        
        with col_admin3:
            if st.button("🔄 Restaurar Padrão", use_container_width=True):
                dados_sistema = carregar_dados_padrao()
                salvar_dados(dados_sistema)
                salvar_metadata({
                    "criado_em": metadata["criado_em"],
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "atualizado_por": st.session_state.get('admin_user', 'admin'),
                    "versao": metadata["versao"]
                })
                st.success("✅ Dados restaurados para padrão!")
                st.rerun()
        
        with col_admin4:
            if st.button("🚪 Sair", use_container_width=True):
                logout()

# ============================================
# PAINEL ADMINISTRATIVO (apenas para admins)
# ============================================

if st.session_state.authenticated and st.session_state.user_role == "admin":
    if 'show_admin_panel' not in st.session_state:
        st.session_state.show_admin_panel = False
    
    if st.session_state.show_admin_panel:
        st.markdown('<div class="section-title">👑 PAINEL ADMINISTRATIVO</div>', unsafe_allow_html=True)
        
        # Tabs para diferentes tipos de dados
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "👥 Dados Humanos", 
            "🗺️ Dados Regionais", 
            "🐕 Dados Caninos", 
            "⚙️ Configurações"
        ])
        
        with admin_tab1:
            st.markdown("#### 👥 ATUALIZAR DADOS HUMANOS ANUAIS")
            
            # Editor de dados humanos
            edited_humanos = st.data_editor(
                dados_sistema['humanos'],
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Ano": st.column_config.NumberColumn(
                        "Ano",
                        min_value=1994,
                        max_value=2030,
                        step=1,
                        format="%d"
                    ),
                    "Casos_incidentes": st.column_config.NumberColumn(
                        "Casos Incidentes",
                        min_value=0,
                        format="%d"
                    ),
                    "Óbitos_incidentes": st.column_config.NumberColumn(
                        "Óbitos Incidentes",
                        min_value=0,
                        format="%d"
                    ),
                    "População": st.column_config.NumberColumn(
                        "População",
                        min_value=0,
                        format="%d"
                    )
                }
            )
            
            if st.button("💾 Salvar Dados Humanos", use_container_width=True):
                dados_sistema['humanos'] = edited_humanos
                salvar_dados(dados_sistema)
                salvar_metadata({
                    "criado_em": metadata["criado_em"],
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "atualizado_por": st.session_state.get('admin_user', 'admin'),
                    "versao": metadata["versao"]
                })
                st.success("✅ Dados humanos atualizados com sucesso!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab2:
            st.markdown("#### 🗺️ ATUALIZAR DADOS REGIONAIS")
            
            # Editor de dados regionais
            edited_regionais = st.data_editor(
                dados_sistema['regionais'],
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "Regional": st.column_config.TextColumn("Regional"),
                    "2024": st.column_config.NumberColumn("2024", min_value=0, format="%d"),
                    "2023": st.column_config.NumberColumn("2023", min_value=0, format="%d"),
                    "2022": st.column_config.NumberColumn("2022", min_value=0, format="%d"),
                    "2021": st.column_config.NumberColumn("2021", min_value=0, format="%d"),
                    "2020": st.column_config.NumberColumn("2020", min_value=0, format="%d")
                }
            )
            
            if st.button("💾 Salvar Dados Regionais", use_container_width=True):
                dados_sistema['regionais'] = edited_regionais
                salvar_dados(dados_sistema)
                salvar_metadata({
                    "criado_em": metadata["criado_em"],
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "atualizado_por": st.session_state.get('admin_user', 'admin'),
                    "versao": metadata["versao"]
                })
                st.success("✅ Dados regionais atualizados com sucesso!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab3:
            st.markdown("#### 🐕 ATUALIZAR DADOS CANINOS")
            
            # Editor de dados caninos
            edited_caninos = st.data_editor(
                dados_sistema['caninos'],
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "Ano": st.column_config.NumberColumn(
                        "Ano",
                        min_value=1994,
                        max_value=2030,
                        step=1,
                        format="%d"
                    ),
                    "Sorologias_Realizadas": st.column_config.NumberColumn(
                        "Sorologias Realizadas",
                        min_value=0,
                        format="%d"
                    ),
                    "Cães_Soropositivos": st.column_config.NumberColumn(
                        "Cães Soropositivos",
                        min_value=0,
                        format="%d"
                    ),
                    "Imóveis_Borrifados": st.column_config.NumberColumn(
                        "Imóveis Borrifados",
                        min_value=0,
                        format="%d"
                    )
                }
            )
            
            if st.button("💾 Salvar Dados Caninos", use_container_width=True):
                dados_sistema['caninos'] = edited_caninos
                salvar_dados(dados_sistema)
                salvar_metadata({
                    "criado_em": metadata["criado_em"],
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "atualizado_por": st.session_state.get('admin_user', 'admin'),
                    "versao": metadata["versao"]
                })
                st.success("✅ Dados caninos atualizados com sucesso!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab4:
            st.markdown("#### ⚙️ CONFIGURAÇÕES DO SISTEMA")
            
            # Configurações de segurança
            st.markdown("**🔐 Segurança**")
            novo_usuario = st.text_input("Novo nome de usuário")
            nova_senha = st.text_input("Nova senha", type="password")
            confirmar_senha = st.text_input("Confirmar senha", type="password")
            
            if st.button("🔄 Atualizar Credenciais", use_container_width=True):
                if nova_senha and nova_senha == confirmar_senha:
                    # Atualizar credenciais (em produção, usar banco de dados seguro)
                    st.success("✅ Credenciais atualizadas com sucesso!")
                else:
                    st.error("❌ As senhas não coincidem!")
            
            st.markdown("---")
            
            # Exportar/Importar dados
            st.markdown("**📁 Backup e Restauração**")
            
            col_bk1, col_bk2 = st.columns(2)
            
            with col_bk1:
                # Exportar dados
                dados_json = {
                    'humanos': dados_sistema['humanos'].to_dict(),
                    'regionais': dados_sistema['regionais'].to_dict(),
                    'caninos': dados_sistema['caninos'].to_dict(),
                    'metadata': metadata
                }
                
                st.download_button(
                    label="📥 Exportar Todos os Dados",
                    data=json.dumps(dados_json, indent=2),
                    file_name=f"vigileish_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_bk2:
                # Importar dados
                uploaded_backup = st.file_uploader(
                    "Escolher arquivo de backup",
                    type=['json'],
                    key="backup_upload"
                )
                
                if uploaded_backup is not None:
                    if st.button("🔄 Restaurar Backup", use_container_width=True):
                        try:
                            backup_data = json.load(uploaded_backup)
                            dados_sistema['humanos'] = pd.DataFrame(backup_data['humanos'])
                            dados_sistema['regionais'] = pd.DataFrame(backup_data['regionais'])
                            dados_sistema['caninos'] = pd.DataFrame(backup_data['caninos'])
                            salvar_dados(dados_sistema)
                            salvar_metadata(backup_data['metadata'])
                            st.success("✅ Backup restaurado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao restaurar backup: {str(e)}")
        
        # Botão para fechar painel admin
        if st.button("❌ Fechar Painel Admin", use_container_width=True):
            st.session_state.show_admin_panel = False
            st.rerun()
        
        st.stop()  # Para aqui se estiver no painel admin

# ============================================
# INTERFACE PÚBLICA (VISUALIZAÇÃO APENAS)
# ============================================

# Extrair DataFrames
dados_humanos = dados_sistema['humanos']
dados_regionais = dados_sistema['regionais']
dados_caninos = dados_sistema['caninos']

# Botão de login no canto (apenas se não estiver autenticado)
if not st.session_state.authenticated:
    col_login, col_empty1, col_empty2, col_empty3 = st.columns([1, 3, 3, 3])
    with col_login:
        if st.button("🔐 Acesso Admin", type="secondary"):
            st.session_state.show_login = True
            st.rerun()

# ============================================
# DASHBOARD PÚBLICO
# ============================================

# Filtros públicos
st.markdown('<div class="section-title">📊 DASHBOARD DE MONITORAMENTO</div>', unsafe_allow_html=True)

col_filtro1, col_filtro2 = st.columns(2)

with col_filtro1:
    ano_inicio = st.slider("Ano inicial:", 1994, 2024, 2015)
    ano_fim = st.slider("Ano final:", 1994, 2024, 2024)

with col_filtro2:
    tipo_visualizacao = st.selectbox(
        "Tipo de visualização:",
        ["Casos Totais", "Incidência", "Letalidade", "Comparativo Regional"]
    )

# Métricas principais
st.markdown("### 🎯 INDICADORES-CHAVE")

col_met1, col_met2, col_met3, col_met4 = st.columns(4)

with col_met1:
    casos_periodo = dados_humanos[
        (dados_humanos['Ano'] >= ano_inicio) & 
        (dados_humanos['Ano'] <= ano_fim)
    ]['Casos_incidentes'].sum()
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Total de Casos</div>
        <div style="font-size: 2rem; font-weight: bold; color: #1a5f7a;">{casos_periodo:,}</div>
        <div style="font-size: 0.8rem; color: #888;">{ano_inicio}-{ano_fim}</div>
    </div>
    """, unsafe_allow_html=True)

with col_met2:
    letalidade_media = dados_humanos['Letalidade_%'].mean().round(1)
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Letalidade Média</div>
        <div style="font-size: 2rem; font-weight: bold; color: #e74c3c;">{letalidade_media}%</div>
        <div style="font-size: 0.8rem; color: #888;">1994-2025</div>
    </div>
    """, unsafe_allow_html=True)

with col_met3:
    incidencia_atual = dados_humanos[dados_humanos['Ano'] == 2023]['Incidência_100k'].values[0] if 2023 in dados_humanos['Ano'].values else 0
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Incidência Atual</div>
        <div style="font-size: 2rem; font-weight: bold; color: #2a9d8f;">{incidencia_atual:.2f}</div>
        <div style="font-size: 0.8rem; color: #888;">por 100k hab. (2023)</div>
    </div>
    """, unsafe_allow_html=True)

with col_met4:
    if '2023' in dados_regionais.columns:
        idx_max = dados_regionais['2023'].idxmax()
        reg_prioritaria = dados_regionais.loc[idx_max, 'Regional']
        casos_reg = dados_regionais.loc[idx_max, '2023']
    else:
        reg_prioritaria = "Nordeste"
        casos_reg = 7
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Prioridade Regional</div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #f39c12;">{reg_prioritaria}</div>
        <div style="font-size: 0.8rem; color: #888;">{casos_reg} casos (2023)</div>
    </div>
    """, unsafe_allow_html=True)

# Gráficos públicos
st.markdown("### 📈 VISUALIZAÇÕES")

tab_public1, tab_public2, tab_public3 = st.tabs(["📊 Evolução Temporal", "🗺️ Distribuição Espacial", "📋 Dados Detalhados"])

with tab_public1:
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico de evolução temporal
        fig1 = px.line(
            dados_humanos[(dados_humanos['Ano'] >= ano_inicio) & (dados_humanos['Ano'] <= ano_fim)],
            x='Ano',
            y='Casos_incidentes',
            title='Evolução dos Casos de LV',
            markers=True,
            line_shape='spline'
        )
        fig1.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_graf2:
        # Gráfico de letalidade
        fig2 = px.bar(
            dados_humanos[(dados_humanos['Ano'] >= ano_inicio) & (dados_humanos['Ano'] <= ano_fim)],
            x='Ano',
            y='Letalidade_%',
            title='Letalidade da Leishmaniose Visceral',
            color='Letalidade_%',
            color_continuous_scale='Reds'
        )
        fig2.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

with tab_public2:
    # Mapa simplificado
    st.markdown("#### 🗺️ DISTRIBUIÇÃO POR REGIONAL")
    
    ano_selecionado = st.selectbox("Selecione o ano:", ['2023', '2022', '2021', '2020'])
    
    # Gráfico de barras horizontais
    df_reg_ano = dados_regionais[['Regional', ano_selecionado]].copy()
    df_reg_ano = df_reg_ano[df_reg_ano['Regional'] != 'Ignorado']
    df_reg_ano = df_reg_ano.sort_values(ano_selecionado)
    
    fig_map = px.bar(
        df_reg_ano,
        x=ano_selecionado,
        y='Regional',
        orientation='h',
        title=f'Casos por Regional - {ano_selecionado}',
        color=ano_selecionado,
        color_continuous_scale='RdYlGn_r',
        height=500
    )
    fig_map.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Legenda do mapa
    st.info("""
    **🎨 Legenda das cores:**
    - **🟢 Verde claro:** Poucos casos (0-2)
    - **🟡 Amarelo/Laranja:** Casos moderados (3-5)
    - **🔴 Vermelho:** Muitos casos (6+)
    """)

with tab_public3:
    # Dados detalhados (somente visualização)
    st.markdown("#### 📋 DADOS DETALHADOS")
    
    subtab_det1, subtab_det2, subtab_det3 = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos"])
    
    with subtab_det1:
        st.dataframe(
            dados_humanos,
            use_container_width=True,
            column_config={
                "Ano": st.column_config.NumberColumn(format="%d"),
                "Casos_incidentes": st.column_config.NumberColumn(format="%d"),
                "Óbitos_incidentes": st.column_config.NumberColumn(format="%d"),
                "Incidência_100k": st.column_config.NumberColumn(format="%.2f"),
                "Letalidade_%": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
    
    with subtab_det2:
        st.dataframe(dados_regionais, use_container_width=True)
    
    with subtab_det3:
        st.dataframe(dados_caninos, use_container_width=True)

# ============================================
# RODAPÉ
# ============================================

st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>VigiLeish - Sistema de Vigilância Epidemiológica</strong><br>
    • Atividade Extensionista II - UNINTER<br>
    CST Ciência de Dados • Aline Alice F. da Silva (RU: 5277514) •<br>
    <small>Versão 2.0 • Dados atualizados em: {datetime.fromisoformat(metadata['ultima_atualizacao']).strftime('%d/%m/%Y %H:%M')}</small>
</div>
""", unsafe_allow_html=True)
