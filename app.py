import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import bcrypt

st.set_page_config(page_title="SisVenda", layout="wide", page_icon="🛒")

# ===================== CONEXÃO COM O BANCO =====================
conn = sqlite3.connect('sisvenda.db', check_same_thread=False)
c = conn.cursor()

# ===================== CRIAÇÃO DAS TABELAS =====================
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
                total REAL)''')

conn.commit()

# ===================== FUNÇÕES =====================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verificar_login(username, password):
    c.execute("SELECT password, nome, id FROM usuarios WHERE username = ?", (username,))
    result = c.fetchone()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True, result[1], result[2]
    return False, None, None

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

# ===================== SESSÃO DO USUÁRIO =====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome = None
    st.session_state.user_id = None

# ===================== TELA DE LOGIN =====================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 SisVenda")
        st.markdown("### Faça login para continuar")
        
        username = st.text_input("Usuário", placeholder="admin")
        password = st.text_input("Senha", type="password", placeholder="admin123")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            ok, nome, user_id = verificar_login(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.nome = nome
                st.session_state.user_id = user_id
                st.success(f"Bem-vindo, {nome}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

    # Cria usuário admin padrão
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        criar_usuario("admin", "admin123", "Administrador", "Admin")
    
    st.stop()

# ===================== MENU LATERAL =====================
st.sidebar.success(f"👤 {st.session_state.nome} ({st.session_state.username})")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Menu Principal",
    ["🏠 Início", "🛍️ Nova Venda", "📦 Produtos", "👥 Clientes", "📊 Relatórios", "👤 Usuários"]
)

if st.sidebar.button("🚪 Sair"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===================== PÁGINAS =====================
st.title("🛒 SisVenda - Sistema de Vendas")

# ===================== INÍCIO =====================
if menu == "🏠 Início":
    st.success(f"Bem-vindo ao sistema, {st.session_state.nome}!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_produtos = pd.read_sql("SELECT COUNT(*) as total FROM produtos", conn).iloc[0]['total']
        st.metric("Produtos", total_produtos)
    with col2:
        total_clientes = pd.read_sql("SELECT COUNT(*) as total FROM clientes", conn).iloc[0]['total']
        st.metric("Clientes", total_clientes)
    with col3:
        total_vendas = pd.read_sql("SELECT COUNT(*) as total FROM vendas", conn).iloc[0]['total']
        st.metric("Vendas Realizadas", total_vendas)

# ===================== NOVA VENDA =====================
elif menu == "🛍️ Nova Venda":
    st.header("🛍️ Nova Venda")
    st.info("🔧 Módulo de Vendas completo em breve...")

# ===================== PRODUTOS =====================
elif menu == "📦 Produtos":
    st.header("📦 Gerenciar Produtos")
    tab1, tab2 = st.tabs(["Cadastrar", "Lista de Produtos"])
    
    with tab1:
        with st.form("form_produto"):
            nome = st.text_input("Nome do Produto *")
            preco = st.number_input("Preço R$", min_value=0.01, format="%.2f")
            estoque = st.number_input("Estoque Inicial", min_value=0, value=0)
            categoria = st.text_input("Categoria")
            
            if st.form_submit_button("Cadastrar Produto"):
                if nome:
                    c.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (?, ?, ?, ?)",
                             (nome, preco, estoque, categoria))
                    conn.commit()
                    st.success("✅ Produto cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Nome do produto é obrigatório!")

    with tab2:
        st.dataframe(pd.read_sql("SELECT * FROM produtos", conn), use_container_width=True, hide_index=True)

# ===================== CLIENTES =====================
elif menu == "👥 Clientes":
    st.header("👥 Gerenciar Clientes")
    with st.form("form_cliente"):
        nome = st.text_input("Nome Completo *")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        endereco = st.text_area("Endereço")
        
        if st.form_submit_button("Cadastrar Cliente"):
            if nome:
                try:
                    c.execute("""INSERT INTO clientes (nome, cpf, telefone, endereco, data_cadastro)
                               VALUES (?, ?, ?, ?, ?)""",
                             (nome, cpf, telefone, endereco, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    st.success("✅ Cliente cadastrado com sucesso!")
                    st.rerun()
                except:
                    st.error("Erro: CPF já cadastrado ou outro erro.")
            else:
                st.error("Nome é obrigatório!")

# ===================== RELATÓRIOS =====================
elif menu == "📊 Relatórios":
    st.header("📊 Relatórios")
    tab1, tab2, tab3 = st.tabs(["📦 Estoque", "👥 Clientes", "📈 Vendas"])
    
    with tab1:
        df_estoque = pd.read_sql("""
            SELECT nome, categoria, estoque, preco, (estoque * preco) as valor_total 
            FROM produtos ORDER BY estoque ASC
        """, conn)
        st.dataframe(df_estoque, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Produtos", len(df_estoque))
        with col2:
            st.metric("Valor Total em Estoque", f"R$ {df_estoque['valor_total'].sum():.2f}")

    with tab2:
        st.dataframe(pd.read_sql("SELECT * FROM clientes", conn), use_container_width=True, hide_index=True)

    with tab3:
        st.info("🔧 Módulo de Vendas completo em desenvolvimento...")

# ===================== USUÁRIOS (Apenas Admin) =====================
elif menu == "👤 Usuários":
    if st.session_state.nome == "Administrador":
        st.header("👤 Gerenciar Usuários")
        with st.form("form_usuario"):
            username = st.text_input("Nome de Usuário")
            nome = st.text_input("Nome Completo")
            password = st.text_input("Senha", type="password")
            cargo = st.selectbox("Cargo", ["Vendedor", "Admin"])
            
            if st.form_submit_button("Cadastrar Usuário"):
                if username and nome and password:
                    if criar_usuario(username, password, nome, cargo):
                        st.success("✅ Usuário cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário já existe!")
                else:
                    st.error("Preencha todos os campos!")
        
        st.dataframe(pd.read_sql("SELECT id, username, nome, cargo FROM usuarios", conn), hide_index=True)
    else:
        st.error("Acesso restrito aos Administradores.")

conn.close()