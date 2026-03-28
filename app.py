import sqlite3
import os
import string
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# Certifique-se de que a importação inclui proteger_senha!
from crypto_utils import gerar_ou_carregar_chave, revelar_senha, proteger_senha 

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura_do_safevault' 
chave = gerar_ou_carregar_chave()

# --- LÓGICA DO GERADOR DE SENHAS ---
def gerar_senha_forte(tamanho=12, usar_especiais=True):
    caracteres = string.ascii_letters + string.digits
    simbolos = "!@*-_"
    if usar_especiais:
        caracteres += simbolos
    while True:
        senha = ''.join(secrets.choice(caracteres) for _ in range(tamanho))
        if (any(c.islower() for c in senha) and any(c.isupper() for c in senha) and sum(c.isdigit() for c in senha) >= 2):
            if usar_especiais and not any(c in simbolos for c in senha):
                continue
            return senha

# --- ROTAS DE LOGIN E COFRE (As que já tínhamos) ---
@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        senha_digitada = request.form.get('senha')
        if os.path.exists("mestra.dat"):
            with open("mestra.dat", "rb") as f:
                senha_salva = revelar_senha(f.read(), chave)
            if senha_digitada == senha_salva:
                session['logado'] = True
                return redirect(url_for('cofre'))
            else:
                erro = "Senha mestra incorreta."
        else:
            erro = "Cofre não configurado."
    return render_template('login.html', erro=erro)

@app.route('/cofre')
def cofre():
    if not session.get('logado'): return redirect(url_for('login'))
    conexao = sqlite3.connect('safevault.db')
    cursor = conexao.cursor()
    cursor.execute("SELECT servico, usuario, senha FROM credenciais")
    linhas = cursor.fetchall()
    conexao.close()
    
    lista_credenciais = []
    for linha in linhas:
        senha_aberta = revelar_senha(linha[2].encode() if isinstance(linha[2], str) else linha[2], chave)
        lista_credenciais.append({'servico': linha[0], 'usuario': linha[1], 'senha': senha_aberta})
        
    return render_template('cofre.html', senhas=lista_credenciais)

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

# --- NOVAS ROTAS (CRUD E GERADOR) ---

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if not session.get('logado'): return redirect(url_for('login'))
    
    if request.method == 'POST':
        servico = request.form.get('servico')
        usuario = request.form.get('usuario')
        senha_limpa = request.form.get('senha')
        is_edit = request.form.get('is_edit') == 'true'
        
        # Criptografa a nova senha antes de salvar
        senha_cripto = proteger_senha(senha_limpa, chave).decode('utf-8')
        
        conexao = sqlite3.connect('safevault.db')
        cursor = conexao.cursor()
        
        if is_edit:
            cursor.execute("UPDATE credenciais SET usuario = ?, senha = ? WHERE servico = ?", (usuario, senha_cripto, servico))
        else:
            cursor.execute("INSERT INTO credenciais (servico, usuario, senha) VALUES (?, ?, ?)", (servico, usuario, senha_cripto))
            
        conexao.commit()
        conexao.close()
        return redirect(url_for('cofre')) # Volta para a lista
        
    # Se for GET, verifica se estamos a tentar Editar um serviço existente
    servico_edit = request.args.get('servico')
    credencial = None
    if servico_edit:
        conexao = sqlite3.connect('safevault.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT servico, usuario, senha FROM credenciais WHERE servico = ?", (servico_edit,))
        linha = cursor.fetchone()
        conexao.close()
        if linha:
            senha_aberta = revelar_senha(linha[2].encode() if isinstance(linha[2], str) else linha[2], chave)
            credencial = {'servico': linha[0], 'usuario': linha[1], 'senha': senha_aberta}
            
    return render_template('cadastro.html', credencial=credencial)

@app.route('/excluir/<servico>')
def excluir(servico):
    if not session.get('logado'): return redirect(url_for('login'))
    conexao = sqlite3.connect('safevault.db')
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM credenciais WHERE servico = ?", (servico,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('cofre'))

@app.route('/api/gerar_senha')
def api_gerar_senha():
    if not session.get('logado'): return jsonify({'erro': 'Acesso negado'}), 403
    tamanho = int(request.args.get('tamanho', 12))
    especiais = request.args.get('especiais', 'true') == 'true'
    senha = gerar_senha_forte(tamanho, especiais)
    return jsonify({'senha': senha}) # Envia a senha em formato JSON para o navegador ler

# Não se esqueça de adicionar esta importação lá no topo do arquivo!
import pyperclip 
from flask import jsonify # Adicione o jsonify nas importações do flask lá em cima também

# ... (resto do seu código) ...

@app.route('/api/limpar_clipboard', methods=['POST'])
def limpar_clipboard():
    # O JavaScript vai enviar a senha que foi copiada
    dados = request.get_json()
    senha_copiada = dados.get('senha')
    
    try:
        # Só limpa se a senha que está atualmente na área de transferência 
        # for a mesma que o usuário copiou há 30s. Isso evita apagar algo 
        # importante que ele tenha copiado de outro lugar nesse meio tempo!
        if pyperclip.paste() == senha_copiada:
            pyperclip.copy(" ") 
            return jsonify({"status": "limpo"})
    except Exception as e:
        print(f"Erro ao acessar clipboard: {e}")
        
    return jsonify({"status": "ignorado"})

if __name__ == '__main__':
    app.run(debug=True)