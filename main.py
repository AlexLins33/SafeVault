import os
from crypto_utils import gerar_ou_carregar_chave, proteger_senha, revelar_senha
from storage import salvar_no_arquivo, carregar_tudo, atualizar_arquivo, buscar_indice

def gerenciar_acesso(chave_cripto):
    """Verifica se existe uma senha mestra ou pede para criar uma."""
    arquivo_senha = "mestra.dat"
    
    if not os.path.exists(arquivo_senha):
        print("\n=== CONFIGURAÇÃO DE PRIMEIRO ACESSO ===")
        nova_senha = input("Defina sua SENHA MESTRA para proteger o cofre: ")
     
        p_mestra = proteger_senha(nova_senha, chave_cripto)
        with open(arquivo_senha, "wb") as f:
            f.write(p_mestra)
        print("[!] Senha Mestra configurada!\n")
        return True
    else:
        with open(arquivo_senha, "rb") as f:
            senha_salva_cripto = f.read()
        
        senha_correta = revelar_senha(senha_salva_cripto, chave_cripto)
        
        tentativa = input("Digite a SENHA MESTRA: ")
        if tentativa == senha_correta:
            print("[V] Acesso Liberado!")
            return True
        else:
            print("[X] Senha Incorreta!")
            return False

def iniciar():
    chave = gerar_ou_carregar_chave()
    
 
    if not gerenciar_acesso(chave):
        return

    while True:
        print("\n--- SAFEVAULT - MENU PRINCIPAL ---")
        print("1. Salvar Nova Senha")
        print("2. Ver Todas as Senhas")
        print("3. Editar Senha")
        print("4. Apagar Senha")
        print("5. Sair")
        
        op = input("Escolha uma opção: ")

        if op == "1":
            serv = input("Serviço (ex: Instagram): ")
            user = input("Usuário: ")
            pw = input("Senha: ")
            
            p_protegida = proteger_senha(pw, chave)
            salvar_no_arquivo(serv, user, p_protegida)
            print("[OK] Dados salvos com sucesso!")

        elif op == "2":
            lista = carregar_tudo()
            if not lista:
                print("\n[!] O cofre está vazio.")
            else:
                print("\n--- CREDENCIAIS SALVAS ---")
                for item in lista:
                
                    real = revelar_senha(item['senha'].encode(), chave)
                    print(f"Site: {item['servico']} | User: {item['usuario']} | Senha: {real}")

        elif op == "3":
            serv_editar = input("Qual serviço deseja EDITAR?: ")
            lista = carregar_tudo()
            idx = buscar_indice(serv_editar, lista)
            
            if idx != -1:
                novo_user = input("Novo usuário: ")
                nova_pw = input("Nova senha: ")
                p_nova = proteger_senha(nova_pw, chave)
                
                lista[idx]['usuario'] = novo_user
                lista[idx]['senha'] = p_nova.decode()
                
                atualizar_arquivo(lista)
                print(f"[*] {serv_editar} atualizado!")
            else:
                print("[X] Serviço não encontrado.")

        elif op == "4":
            serv_apagar = input("Qual serviço deseja APAGAR?: ")
            lista = carregar_tudo()
            idx = buscar_indice(serv_apagar, lista)
            
            if idx != -1:
                lista.pop(idx)
                atualizar_arquivo(lista)
                print(f"[!] {serv_apagar} removido!")
            else:
                print("[X] Serviço não encontrado.")

        elif op == "5":
            print("Saindo do SafeVault. Até logo!")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    iniciar()
