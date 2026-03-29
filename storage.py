import sqlite3

def conectar():
 
    conn = sqlite3.connect("safevault.db")
    cursor = conn.cursor()
   
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credenciais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico TEXT NOT NULL UNIQUE,
            usuario TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def salvar_no_arquivo(servico, usuario, senha_protegida):
    conn = conectar()
    cursor = conn.cursor()
    try:
        
        senha_texto = senha_protegida.decode() if isinstance(senha_protegida, bytes) else senha_protegida
        
        cursor.execute("INSERT INTO credenciais (servico, usuario, senha) VALUES (?, ?, ?)", 
                       (servico, usuario, senha_texto))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Erro: Serviço já existe!")
    finally:
        conn.close()

def carregar_tudo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT servico, usuario, senha FROM credenciais")
    rows = cursor.fetchall()
    conn.close()
  
    return [{'servico': r[0], 'usuario': r[1], 'senha': r[2]} for r in rows]

def excluir_no_db(servico):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credenciais WHERE servico = ?", (servico,))
    conn.commit()
    conn.close()

def atualizar_no_db(servico, novo_usuario, nova_senha_protegida):
    conn = conectar()
    cursor = conn.cursor()
  
    cursor.execute("""
        UPDATE credenciais 
        SET usuario = ?, senha = ? 
        WHERE servico = ?
    """, (novo_usuario, nova_senha_protegida, servico))
    conn.commit()
    conn.close()
