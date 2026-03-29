from cryptography.fernet import Fernet
import os

def gerar_ou_carregar_chave():
    if not os.path.exists("chave.key"):
        chave = Fernet.generate_key()
        with open("chave.key", "wb") as chave_file:
            chave_file.write(chave)
    else:
        with open("chave.key", "rb") as chave_file:
            chave = chave_file.read()
    return chave

def proteger_senha(senha_limpa, chave):
    f = Fernet(chave)
    return f.encrypt(senha_limpa.encode())

def revelar_senha(senha_cripto, chave):
    f = Fernet(chave)
    return f.decrypt(senha_cripto).decode()

import string
import secrets

def gerar_senha_forte(tamanho=12, usar_especiais=True):
    caracteres = string.ascii_letters + string.digits
   
    simbolos = "!@*-_" 
    
    if usar_especiais:
        caracteres += simbolos
    
    while True:
        senha = ''.join(secrets.choice(caracteres) for _ in range(tamanho))
      
        if (any(c.islower() for c in senha) 
            and any(c.isupper() for c in senha) 
            and sum(c.isdigit() for c in senha) >= 2):
            
           
            if usar_especiais and not any(c in simbolos for c in senha):
                continue
            return senha
