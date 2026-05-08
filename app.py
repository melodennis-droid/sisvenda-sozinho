import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import bcrypt

st.set_page_config(page_title="SisVenda", layout="wide", page_icon="🛒")

# ===================== CONEXÃO COM BANCO =====================
conn = sqlite3.connect('sisvenda.db')
c = conn.cursor()

# ===================== TABELAS =====================
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nome TEXT,
                cargo TEXT,
                data_cadastro TEXT)''')

# Tabelas existentes
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
                total REAL)''')

conn.commit()

# ===================== FUNÇÕES DE LOGIN =====================
def criar_usuario(username, password, nome, cargo="Vendedor"):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO usuarios (username, password, nome, cargo, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                 (username, hashed, nome, cargo, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except:
        return False

def verificar_login(username, password):
    c.execute("SELECT password FROM usuarios WHERE username = ?", (username,))
    result = c.fetchone()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

# ===================== LOGIN =====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome = None

# Se não estiver logado, mostra tela de login
if not st.session_state.logged_in:
    st.title("🔐 Login - SisVenda")
    st.markdown("### Entre com suas credenciais")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Usuário", placeholder="admin")
        password = st.text_input("Senha", type="password", placeholder="123456")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            if verificar_login(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                c.execute("SELECT nome FROM usuarios WHERE username = ?", (username,))
                st.session_state.nome = c.fetchone()[0]
                st.success(f"Bem-vindo, {st.session_state.nome}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

        st.markdown("---")
        st.caption("Usuário padrão: `admin` | Senha: `admin123`")

    # Criar usuário admin padrão na primeira execução
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        criar_usuario("admin", "admin123", "Administrador", "Admin")
    
    st.stop()  # Para a execução aqui se não estiver logado

# ===================== MENU (Só aparece após login) =====================
st.sidebar.success(f"👤 {st.session_state.nome}")
menu = st.sidebar.selectbox(
    "Menu Principal",
    ["Início", "🛍️ Nova Venda", "📦 Produtos", "👥 Clientes", "📊 Relatórios"]
)

if st.sidebar.button("🚪 Sair"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome = None
    st.rerun()

# ===================== RESTO DO CÓDIGO (seu código original) =====================
st.title("🛒 SisVenda - Sistema de Vendas")
st.markdown("### Gerencie suas vendas, clientes e estoque")

# ... (coloque aqui o resto do seu código original - Início, Produtos, Clientes, Relatórios)

# ===================== INÍCIO =====================
if menu == "Início":
    st.success("✅ Sistema carregado com sucesso!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Produtos", pd.read_sql("SELECT COUNT(*) as c FROM produtos", conn).iloc[0]['c'])
    with col2:
        st.metric("Clientes", pd.read_sql("SELECT COUNT(*) as c FROM clientes", conn).iloc[0]['c'])
    with col3:
        st.metric("Vendas Realizadas", pd.read_sql("SELECT COUNT(*) as c FROM vendas", conn).iloc[0]['c'])

# ===================== PRODUTOS =====================
elif menu == "📦 Produtos":
    st.header("📦 Gerenciar Produtos")
    tab1, tab2 = st.tabs(["Cadastrar", "Lista de Produtos"])
    
    with tab1:
        with st.form("form_produto"):
            nome = st.text_input("Nome do Produto *")
            preco = st.number_input("Preço R$", min_value=0.01, format="%.2f")
            estoque = st.number_input("Estoque Inicial", min_value=0, value=10)
            categoria = st.text_input("Categoria")
            
            if st.form_submit_button("Cadastrar Produto"):
                if nome:
                    c.execute("INSERT INTO produtos (nome, preco, estoque, categoria) VALUES (?, ?, ?, ?)",
                             (nome, preco, estoque, categoria))
                    conn.commit()
                    st.success("✅ Produto cadastrado!")
                    st.rerun()

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
                    st.error("Erro: CPF já cadastrado?")
            else:
                st.error("Nome é obrigatório!")

# ===================== RELATÓRIOS =====================
elif menu == "📊 Relatórios":
    st.header("📊 Relatórios")
    tab1, tab2, tab3 = st.tabs(["📦 Estoque", "👥 Clientes", "📈 Vendas"])
    
    with tab1:
        st.subheader("Situação do Estoque")
        df_estoque = pd.read_sql("""
            SELECT nome, categoria, estoque, preco, (estoque * preco) as valor_estoque 
            FROM produtos 
            ORDER BY estoque ASC
        """, conn)
        st.dataframe(df_estoque, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Produtos", len(df_estoque))
        with col2:
            st.metric("Valor Total em Estoque", f"R$ {df_estoque['valor_estoque'].sum():.2f}")
    
    with tab2:
        st.subheader("Lista de Clientes")
        st.dataframe(pd.read_sql("SELECT * FROM clientes", conn), use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Vendas")
        st.info("🔧 Módulo de Vendas completo em desenvolvimento...")

conn.close()