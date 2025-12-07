import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import hashlib
import sqlite3
import json
from pathlib import Path
import contextlib

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================

st.set_page_config(
    page_title="VigiLeish - Painel de Vigilância",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# BANCO DE DADOS SQLite
# ============================================

DB_PATH = Path("vigileish.db")

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários/admin
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'public',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Tabela de dados humanos anuais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dados_humanos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL UNIQUE,
        casos_incidentes INTEGER NOT NULL DEFAULT 0,
        obitos_incidentes INTEGER NOT NULL DEFAULT 0,
        populacao INTEGER NOT NULL DEFAULT 0,
        incidencia_100k REAL,
        letalidade_percent REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de dados regionais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dados_regionais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regional TEXT NOT NULL,
        ano INTEGER NOT NULL,
        casos INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(regional, ano)
    )
    ''')
    
    # Tabela de dados caninos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dados_caninos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL UNIQUE,
        sorologias_realizadas INTEGER NOT NULL DEFAULT 0,
        caes_soropositivos INTEGER NOT NULL DEFAULT 0,
        imoveis_borrifados INTEGER NOT NULL DEFAULT 0,
        positividade_percent REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de logs/auditoria
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        table_name TEXT,
        record_id INTEGER,
        old_values TEXT,
        new_values TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Tabela de configurações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave TEXT UNIQUE NOT NULL,
        valor TEXT NOT NULL,
        descricao TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Criar usuário admin padrão se não existir
    admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
    INSERT OR IGNORE INTO usuarios (username, password_hash, role) 
    VALUES (?, ?, ?)
    ''', ('admin_vigileish', admin_password_hash, 'admin'))
    
    # Inserir configurações padrão
    configs = [
        ('ultima_atualizacao', datetime.now().isoformat(), 'Data da última atualização dos dados'),
        ('versao_sistema', '2.0', 'Versão do sistema VigiLeish'),
        ('cidade_foco', 'Belo Horizonte - MG', 'Cidade de foco do monitoramento'),
        ('intervalo_atualizacao', '30', 'Dias entre atualizações recomendadas'),
        ('email_contato', 'vigileish@saude.bh.gov.br', 'E-mail para contato'),
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO configuracoes (chave, valor, descricao)
    VALUES (?, ?, ?)
    ''', configs)
    
    # Inserir dados padrão se as tabelas estiverem vazias
    if cursor.execute('SELECT COUNT(*) FROM dados_humanos').fetchone()[0] == 0:
        dados_humanos_padrao = [
            (1994, 34, 6, 2084100),
            (1995, 46, 4, 2106819),
            (1996, 50, 4, 2091371),
            (1997, 39, 3, 2109223),
            (1998, 25, 4, 2124176),
            (1999, 33, 3, 2139125),
            (2000, 46, 9, 2238332),
            (2001, 50, 10, 2238332),
            (2002, 76, 8, 2238332),
            (2003, 106, 9, 2238332),
            (2004, 136, 25, 2238332),
            (2005, 105, 9, 2238332),
            (2006, 128, 12, 2238332),
            (2007, 110, 6, 2238332),
            (2008, 160, 18, 2238332),
            (2009, 145, 31, 2238332),
            (2010, 131, 23, 2375151),
            (2011, 93, 14, 2375151),
            (2012, 54, 12, 2375151),
            (2013, 40, 5, 2375151),
            (2014, 39, 3, 2375151),
            (2015, 48, 7, 2375152),
            (2016, 51, 7, 2375152),
            (2017, 64, 12, 2375152),
            (2018, 39, 5, 2375152),
            (2019, 41, 7, 2375152),
            (2020, 30, 1, 2375152),
            (2021, 30, 3, 2375152),
            (2022, 24, 5, 2315560),
            (2023, 30, 6, 2315560),
            (2024, 29, 8, 2315560),
            (2025, 11, 0, 2315560),
        ]
        
        cursor.executemany('''
        INSERT INTO dados_humanos (ano, casos_incidentes, obitos_incidentes, populacao)
        VALUES (?, ?, ?, ?)
        ''', dados_humanos_padrao)
    
    # Inserir dados regionais padrão
    if cursor.execute('SELECT COUNT(*) FROM dados_regionais').fetchone()[0] == 0:
        regionais = ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 
                    'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado']
        
        dados_regionais_padrao = []
        for regional in regionais:
            for ano in range(2020, 2025):
                casos = np.random.randint(0, 8)  # Dados de exemplo
                dados_regionais_padrao.append((regional, ano, casos))
        
        cursor.executemany('''
        INSERT INTO dados_regionais (regional, ano, casos)
        VALUES (?, ?, ?)
        ''', dados_regionais_padrao)
    
    # Inserir dados caninos padrão
    if cursor.execute('SELECT COUNT(*) FROM dados_caninos').fetchone()[0] == 0:
        dados_caninos_padrao = [
            (2014, 44536, 6198, 54436),
            (2015, 20659, 3807, 56475),
            (2016, 22965, 5529, 5617),
            (2017, 33029, 6539, 19538),
            (2018, 31330, 6591, 26388),
            (2019, 27983, 6165, 14855),
            (2020, 28954, 5624, 73593),
            (2021, 17044, 3539, 78279),
            (2022, 23490, 4077, 64967),
            (2023, 43571, 5440, 51591),
            (2024, 49927, 4459, 30953),
        ]
        
        cursor.executemany('''
        INSERT INTO dados_caninos (ano, sorologias_realizadas, caes_soropositivos, imoveis_borrifados)
        VALUES (?, ?, ?, ?)
        ''', dados_caninos_padrao)
    
    conn.commit()
    conn.close()

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=(), fetchone=False, fetchall=False):
    """Executa uma query no banco de dados"""
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = None
        
        conn.commit()
        return result

def get_config(chave, default=None):
    """Obtém uma configuração do sistema"""
    result = execute_query(
        'SELECT valor FROM configuracoes WHERE chave = ?',
        (chave,),
        fetchone=True
    )
    return result[0] if result else default

def set_config(chave, valor):
    """Define uma configuração do sistema"""
    execute_query('''
    INSERT OR REPLACE INTO configuracoes (chave, valor, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (chave, valor))

# ============================================
# SISTEMA DE AUTENTICAÇÃO
# ============================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = "public"
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def verificar_login(username, password):
    """Verifica as credenciais do administrador"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    result = execute_query(
        'SELECT id, role FROM usuarios WHERE username = ? AND password_hash = ? AND is_active = 1',
        (username, password_hash),
        fetchone=True
    )
    
    if result:
        user_id, role = result
        # Atualizar último login
        execute_query(
            'UPDATE usuarios SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user_id,)
        )
        return user_id, role
    return None, None

def login_admin():
    """Interface de login para administradores"""
    with st.sidebar:
        st.title("🔐 Acesso Administrativo")
        
        username = st.text_input("Usuário", key="login_user")
        password = st.text_input("Senha", type="password", key="login_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Entrar", use_container_width=True):
                user_id, role = verificar_login(username, password)
                if user_id:
                    st.session_state.authenticated = True
                    st.session_state.user_role = role
                    st.session_state.user_id = user_id
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
    st.session_state.user_id = None
    st.session_state.show_login = False
    st.rerun()

# ============================================
# FUNÇÕES DE DADOS
# ============================================

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados_humanos():
    """Carrega dados humanos do banco de dados"""
    query = '''
    SELECT ano, casos_incidentes, obitos_incidentes, populacao,
           (casos_incidentes * 100000.0 / populacao) as incidencia_100k,
           (obitos_incidentes * 100.0 / CASE WHEN casos_incidentes = 0 THEN 1 ELSE casos_incidentes END) as letalidade_percent
    FROM dados_humanos
    ORDER BY ano
    '''
    
    result = execute_query(query, fetchall=True)
    
    df = pd.DataFrame(result, columns=[
        'ano', 'casos_incidentes', 'obitos_incidentes', 'populacao',
        'incidencia_100k', 'letalidade_percent'
    ])
    
    return df

@st.cache_data(ttl=300)
def carregar_dados_regionais():
    """Carrega dados regionais do banco de dados"""
    query = '''
    SELECT regional, ano, casos
    FROM dados_regionais
    ORDER BY regional, ano
    '''
    
    result = execute_query(query, fetchall=True)
    
    df = pd.DataFrame(result, columns=['regional', 'ano', 'casos'])
    
    # Transformar para formato pivot (anos como colunas)
    pivot_df = df.pivot_table(
        index='regional',
        columns='ano',
        values='casos',
        fill_value=0
    ).reset_index()
    
    return pivot_df

@st.cache_data(ttl=300)
def carregar_dados_caninos():
    """Carrega dados caninos do banco de dados"""
    query = '''
    SELECT ano, sorologias_realizadas, caes_soropositivos, imoveis_borrifados,
           (caes_soropositivos * 100.0 / CASE WHEN sorologias_realizadas = 0 THEN 1 ELSE sorologias_realizadas END) as positividade_percent
    FROM dados_caninos
    ORDER BY ano
    '''
    
    result = execute_query(query, fetchall=True)
    
    df = pd.DataFrame(result, columns=[
        'ano', 'sorologias_realizadas', 'caes_soropositivos', 
        'imoveis_borrifados', 'positividade_percent'
    ])
    
    return df

def atualizar_dados_humanos(dados_df):
    """Atualiza dados humanos no banco de dados"""
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        
        for _, row in dados_df.iterrows():
            cursor.execute('''
            INSERT OR REPLACE INTO dados_humanos 
            (ano, casos_incidentes, obitos_incidentes, populacao, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                int(row['ano']),
                int(row['casos_incidentes']),
                int(row['obitos_incidentes']),
                int(row['populacao'])
            ))
        
        conn.commit()
    
    # Limpar cache
    st.cache_data.clear()

def atualizar_dados_regionais(dados_df):
    """Atualiza dados regionais no banco de dados"""
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        
        # Primeiro, limpar dados existentes para os anos presentes
        anos_unicos = dados_df.columns[1:].tolist()
        
        for ano in anos_unicos:
            cursor.execute('DELETE FROM dados_regionais WHERE ano = ?', (int(ano),))
        
        # Inserir novos dados
        for _, row in dados_df.iterrows():
            regional = row['regional']
            for ano in anos_unicos:
                casos = int(row[ano])
                cursor.execute('''
                INSERT INTO dados_regionais (regional, ano, casos, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (regional, int(ano), casos))
        
        conn.commit()
    
    st.cache_data.clear()

def atualizar_dados_caninos(dados_df):
    """Atualiza dados caninos no banco de dados"""
    with contextlib.closing(get_connection()) as conn:
        cursor = conn.cursor()
        
        for _, row in dados_df.iterrows():
            cursor.execute('''
            INSERT OR REPLACE INTO dados_caninos 
            (ano, sorologias_realizadas, caes_soropositivos, imoveis_borrifados, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                int(row['ano']),
                int(row['sorologias_realizadas']),
                int(row['caes_soropositivos']),
                int(row['imoveis_borrifados'])
            ))
        
        conn.commit()
    
    st.cache_data.clear()

def log_acao(acao, tabela=None, registro_id=None, valores_antigos=None, valores_novos=None):
    """Registra uma ação no log do sistema"""
    if st.session_state.user_id:
        execute_query('''
        INSERT INTO logs_sistema 
        (user_id, action, table_name, record_id, old_values, new_values)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.user_id,
            acao,
            tabela,
            registro_id,
            json.dumps(valores_antigos) if valores_antigos else None,
            json.dumps(valores_novos) if valores_novos else None
        ))

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
    
    .database-info {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a9d8f;
        margin: 1rem 0;
        font-size: 0.9rem;
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
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAR BANCO DE DADOS
# ============================================

init_database()

# ============================================
# INTERFACE DE LOGIN
# ============================================

if st.session_state.show_login:
    login_admin()
    st.stop()

# ============================================
# CARREGAR DADOS
# ============================================

with st.spinner("🔄 Carregando dados do banco de dados..."):
    dados_humanos = carregar_dados_humanos()
    dados_regionais = carregar_dados_regionais()
    dados_caninos = carregar_dados_caninos()

# ============================================
# CABEÇALHO PRINCIPAL
# ============================================

admin_badge = ""
if st.session_state.authenticated and st.session_state.user_role == "admin":
    admin_badge = '<div class="admin-badge">👑 MODO ADMINISTRADOR</div>'

ultima_atualizacao = get_config('ultima_atualizacao', datetime.now().isoformat())
try:
    data_formatada = datetime.fromisoformat(ultima_atualizacao).strftime('%d/%m/%Y %H:%M')
except:
    data_formatada = datetime.now().strftime('%d/%m/%Y %H:%M')

cidade_foco = get_config('cidade_foco', 'Belo Horizonte - MG')
versao_sistema = get_config('versao_sistema', '2.0')

st.markdown(f"""
<div class="main-header">
    {admin_badge}
    <h1 style="margin: 0; font-size: 2.2rem;">🏥 VIGILEISH - PAINEL DE VIGILÂNCIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
        Sistema de Monitoramento da Leishmaniose Visceral em {cidade_foco}
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            📅 Última atualização: {data_formatada}
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🗄️ Banco de Dados: SQLite
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🎓 Atividade Extensionista UNINTER
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# INFO DO BANCO DE DADOS
# ============================================

conn = get_connection()
total_humanos = conn.execute('SELECT COUNT(*) FROM dados_humanos').fetchone()[0]
total_regionais = conn.execute('SELECT COUNT(*) FROM dados_regionais').fetchone()[0]
total_caninos = conn.execute('SELECT COUNT(*) FROM dados_caninos').fetchone()[0]
conn.close()

st.markdown(f"""
<div class="database-info">
    <strong>🗄️ Banco de Dados Ativo:</strong> SQLite • 
    <strong>👥 Dados Humanos:</strong> {total_humanos} anos • 
    <strong>🗺️ Dados Regionais:</strong> {total_regionais} registros • 
    <strong>🐕 Dados Caninos:</strong> {total_caninos} anos
</div>
""", unsafe_allow_html=True)

# ============================================
# BARRA DE CONTROLE ADMIN
# ============================================

if st.session_state.authenticated and st.session_state.user_role == "admin":
    with st.container():
        col_admin1, col_admin2, col_admin3, col_admin4 = st.columns(4)
        
        with col_admin1:
            if st.button("📤 Atualizar Dados", use_container_width=True):
                st.session_state.show_admin_panel = True
                st.rerun()
        
        with col_admin2:
            if st.button("📊 Estatísticas DB", use_container_width=True):
                st.session_state.show_db_stats = True
                st.rerun()
        
        with col_admin3:
            if st.button("🔄 Limpar Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache limpo com sucesso!")
        
        with col_admin4:
            if st.button("🚪 Sair", use_container_width=True):
                logout()

# ============================================
# PAINEL ADMINISTRATIVO
# ============================================

if st.session_state.authenticated and st.session_state.user_role == "admin":
    if 'show_admin_panel' not in st.session_state:
        st.session_state.show_admin_panel = False
    
    if st.session_state.show_admin_panel:
        st.markdown('<div class="section-title">👑 PAINEL ADMINISTRATIVO - BANCO DE DADOS</div>', unsafe_allow_html=True)
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
            "👥 Dados Humanos", 
            "🗺️ Dados Regionais", 
            "🐕 Dados Caninos",
            "⚙️ Configurações"
        ])
        
        with admin_tab1:
            st.markdown("#### 👥 EDITAR DADOS HUMANOS ANUAIS")
            
            # Carregar dados atuais
            df_humanos_edit = dados_humanos.copy()
            df_humanos_edit = df_humanos_edit.rename(columns={
                'ano': 'Ano',
                'casos_incidentes': 'Casos',
                'obitos_incidentes': 'Óbitos',
                'populacao': 'População',
                'incidencia_100k': 'Incidência/100k',
                'letalidade_percent': 'Letalidade (%)'
            })
            
            edited_humanos = st.data_editor(
                df_humanos_edit[['Ano', 'Casos', 'Óbitos', 'População']],
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
                    "Casos": st.column_config.NumberColumn(
                        "Casos",
                        min_value=0,
                        format="%d"
                    ),
                    "Óbitos": st.column_config.NumberColumn(
                        "Óbitos",
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
            
            if st.button("💾 Salvar Dados Humanos", use_container_width=True, key="save_humanos"):
                # Preparar dados para salvar
                df_to_save = edited_humanos.copy()
                df_to_save.columns = ['ano', 'casos_incidentes', 'obitos_incidentes', 'populacao']
                
                # Registrar log
                log_acao(
                    "ATUALIZAR_DADOS_HUMANOS",
                    "dados_humanos",
                    None,
                    dados_humanos[['ano', 'casos_incidentes', 'obitos_incidentes', 'populacao']].to_dict(),
                    df_to_save.to_dict()
                )
                
                # Salvar no banco
                atualizar_dados_humanos(df_to_save)
                
                # Atualizar configuração
                set_config('ultima_atualizacao', datetime.now().isoformat())
                set_config('atualizado_por', f"admin_{st.session_state.user_id}")
                
                st.success("✅ Dados humanos atualizados no banco de dados!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab2:
            st.markdown("#### 🗺️ EDITAR DADOS REGIONAIS")
            
            # Carregar dados atuais
            df_regionais_edit = dados_regionais.copy()
            
            edited_regionais = st.data_editor(
                df_regionais_edit,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "regional": st.column_config.TextColumn("Regional"),
                }
            )
            
            # Extrair anos das colunas
            anos_colunas = [col for col in edited_regionais.columns if col != 'regional']
            
            # Adicionar validação para anos
            for col in anos_colunas:
                if not str(col).isdigit():
                    st.error(f"Coluna '{col}' deve ser um ano (número)")
                    st.stop()
            
            if st.button("💾 Salvar Dados Regionais", use_container_width=True, key="save_regionais"):
                # Registrar log
                log_acao(
                    "ATUALIZAR_DADOS_REGIONAIS",
                    "dados_regionais",
                    None,
                    dados_regionais.to_dict(),
                    edited_regionais.to_dict()
                )
                
                # Salvar no banco
                atualizar_dados_regionais(edited_regionais)
                
                set_config('ultima_atualizacao', datetime.now().isoformat())
                set_config('atualizado_por', f"admin_{st.session_state.user_id}")
                
                st.success("✅ Dados regionais atualizados no banco de dados!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab3:
            st.markdown("#### 🐕 EDITAR DADOS CANINOS")
            
            # Carregar dados atuais
            df_caninos_edit = dados_caninos.copy()
            df_caninos_edit = df_caninos_edit.rename(columns={
                'ano': 'Ano',
                'sorologias_realizadas': 'Sorologias',
                'caes_soropositivos': 'Cães Positivos',
                'imoveis_borrifados': 'Imóveis Borrifados',
                'positividade_percent': 'Positividade (%)'
            })
            
            edited_caninos = st.data_editor(
                df_caninos_edit[['Ano', 'Sorologias', 'Cães Positivos', 'Imóveis Borrifados']],
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
                    "Sorologias": st.column_config.NumberColumn(
                        "Sorologias Realizadas",
                        min_value=0,
                        format="%d"
                    ),
                    "Cães Positivos": st.column_config.NumberColumn(
                        "Cães Soropositivos",
                        min_value=0,
                        format="%d"
                    ),
                    "Imóveis Borrifados": st.column_config.NumberColumn(
                        "Imóveis Borrifados",
                        min_value=0,
                        format="%d"
                    )
                }
            )
            
            if st.button("💾 Salvar Dados Caninos", use_container_width=True, key="save_caninos"):
                # Preparar dados para salvar
                df_to_save = edited_caninos.copy()
                df_to_save.columns = ['ano', 'sorologias_realizadas', 'caes_soropositivos', 'imoveis_borrifados']
                
                # Registrar log
                log_acao(
                    "ATUALIZAR_DADOS_CANINOS",
                    "dados_caninos",
                    None,
                    dados_caninos[['ano', 'sorologias_realizadas', 'caes_soropositivos', 'imoveis_borrifados']].to_dict(),
                    df_to_save.to_dict()
                )
                
                # Salvar no banco
                atualizar_dados_caninos(df_to_save)
                
                set_config('ultima_atualizacao', datetime.now().isoformat())
                set_config('atualizado_por', f"admin_{st.session_state.user_id}")
                
                st.success("✅ Dados caninos atualizados no banco de dados!")
                st.session_state.show_admin_panel = False
                st.rerun()
        
        with admin_tab4:
            st.markdown("#### ⚙️ CONFIGURAÇÕES DO SISTEMA")
            
            # Carregar configurações
            conn = get_connection()
            configs = conn.execute('SELECT chave, valor, descricao FROM configuracoes').fetchall()
            conn.close()
            
            config_df = pd.DataFrame(configs, columns=['Chave', 'Valor', 'Descrição'])
            
            # Editor de configurações
            edited_configs = st.data_editor(
                config_df,
                use_container_width=True,
                num_rows="dynamic",
                disabled=['Chave', 'Descrição'],
                column_config={
                    "Chave": st.column_config.TextColumn("Chave", disabled=True),
                    "Valor": st.column_config.TextColumn("Valor"),
                    "Descrição": st.column_config.TextColumn("Descrição", disabled=True)
                }
            )
            
            if st.button("💾 Salvar Configurações", use_container_width=True):
                # Atualizar configurações
                for _, row in edited_configs.iterrows():
                    set_config(row['Chave'], row['Valor'])
                
                st.success("✅ Configurações atualizadas!")
        
        # Botão para fechar
        if st.button("❌ Fechar Painel Admin", use_container_width=True):
            st.session_state.show_admin_panel = False
            st.rerun()
        
        st.stop()

# ============================================
# INTERFACE PÚBLICA
# ============================================

if not st.session_state.authenticated:
    col_login, _, _, _ = st.columns([1, 3, 3, 3])
    with col_login:
        if st.button("🔐 Acesso Admin", type="secondary"):
            st.session_state.show_login = True
            st.rerun()

# ============================================
# DASHBOARD P
