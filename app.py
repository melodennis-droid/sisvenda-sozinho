import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import bcrypt

st.set_page_config(page_title="SisVenda", layout="wide", page_icon="🛒")

# ===================== CONEXÃO =====================
conn = sqlite3.connect('sisvenda.db', check_same_thread=False)
c = conn.cursor()

# ===================== TABELAS =====================
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nome TEXT,
                cargo TEXT,
                data_cadastro TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,
                telefone TEXT,
                endereco TEXT,
                data_cadastro TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                preco REAL NOT NULL,
                estoque INTEGER DEFAULT 0,
                categoria TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY,
                data TEXT,
                cliente_id INTEGER,
                usuario_id INTEGER,
                total REAL,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id))''')

conn.commit()

# ===================== FUNÇÕES =====================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verificar_login(username, password):
    c.execute("SELECT password, nome FROM usuarios WHERE username = ?", (username,))
    result = c.fetchone()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True, result[1]
    return False, None

def criar_usuario(username, password, nome, cargo="Vendedor"):
    try:
        hashed = hash_password(password)
        c.execute("""INSERT INTO usuarios (username, password, nome, cargo, data_cadastro)
                    VALUES (?, ?, ?, ?, ?)""",
                 (username, hashed, nome, cargo, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except:
        return False

# ===================== SESSÃO =====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome = None
    st.session_state.user_id = None

# ===================== LOGIN =====================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 SisVenda")
        st.markdown("### Faça login para continuar")
        
        username = st.text_input("Usuário", placeholder="admin")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            ok, nome = verificar_login(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.nome = nome
                c.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
                st.session_state.user_id = c.fetchone()[0]
                st.success(f"Bem-vindo, {nome}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

    # Usuário admin padrão
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        criar_usuario("admin", "admin123", "Administrador", "Admin")
    
    st.stop()

# ===================== MENU LATERAL =====================
st.sidebar.success(f"👤 {st.session_state.nome}")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Menu",
    ["🏠 Início", "🛍️ Nova Venda", "📦 Produtos", "👥 Clientes", "📊 Relatórios", "👤 Usuários"]
)

if st.sidebar.button("🚪 Sair"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===================== PÁGINAS =====================
st.title("🛒 SisVenda - Sistema de Vendas")

if menu == "🏠 Início":
    st.success(f"Bem-vindo ao sistema, {st.session_state.nome}!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Produtos", pd.read_sql("SELECT COUNT(*) FROM produtos", conn).iloc[0][0])
    with col2:
        st.metric("Clientes", pd.read_sql("SELECT COUNT(*) FROM clientes", conn).iloc[0][0])
    with col3:
        st.metric("Vendas Hoje", pd.read_sql("SELECT COUNT(*) FROM vendas WHERE data = ?", 
                (datetime.now().strftime("%Y-%m-%d"),), conn).iloc[0][0])

elif menu == "🛍️ Nova Venda":
    st.header("🛍️ Nova Venda")
    # (Vou implementar completo na próxima mensagem se você confirmar que quer)

    st.info("🔧 Módulo de Vendas em fase de implementação...")
    # Podemos fazer completo agora se você quiser

elif menu == "👤 Usuários" and st.session_state.nome == "Administrador":
    st.header("👤 Gerenciar Usuários")
    with st.form("form_usuario"):
        username = st.text_input("Nome de Usuário")
        nome = st.text_input("Nome Completo")
        password = st.text_input("Senha", type="password")
        cargo = st.selectbox("Cargo", ["Vendedor", "Admin"])
        
        if st.form_submit_button("Cadastrar Usuário"):
            if username and nome and password:
                if criar_usuario(username, password, nome, cargo):
                    st.success("Usuário cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário já existe!")
    st.dataframe(pd.read_sql("SELECT id, username, nome, cargo FROM usuarios", conn), hide_index=True)

# ... (outros menus)

conn.close()