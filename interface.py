import customtkinter as ctk
from crypto_utils import gerar_ou_carregar_chave, proteger_senha, revelar_senha, gerar_senha_forte
from storage import carregar_tudo, salvar_no_arquivo, excluir_no_db, atualizar_no_db
from mail_utils import enviar_codigo_mfa
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppSafeVault(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SafeVault Pro")
        self.geometry("750x650")
        
        # Inicialização de variáveis essenciais
        self.chave = gerar_ou_carregar_chave()
        self.codigo_gerado = None
        self.job_inatividade = None 

        # Configuração de segurança e inatividade
        self.bind_all("<Any-KeyPress>", self.resetar_cronometro_inatividade)
        self.bind_all("<Any-Button>", self.resetar_cronometro_inatividade)
        
        self.tela_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        ctk.CTkLabel(self, text="SAFEVAULT", font=("Roboto", 28, "bold")).pack(pady=40)
        self.label = ctk.CTkLabel(self, text="Digite sua Senha Mestra", font=("Roboto", 14))
        self.label.pack(pady=5)
        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha Mestra", show="*", width=250)
        self.entry_senha.pack(pady=10)
        self.btn_login = ctk.CTkButton(self, text="Acessar Cofre", command=self.verificar_senha)
        self.btn_login.pack(pady=20)

    def verificar_senha(self):
        senha_digitada = self.entry_senha.get()
        if not os.path.exists("mestra.dat"):
            if senha_digitada:
                p_pw = proteger_senha(senha_digitada, self.chave)
                with open("mestra.dat", "wb") as f: f.write(p_pw)
                self.tela_principal() 
            return

        with open("mestra.dat", "rb") as f:
            senha_salva = revelar_senha(f.read(), self.chave)
        
        if senha_digitada == senha_salva:
            self.label.configure(text="Enviando código MFA...", text_color="yellow")
            self.update()
            self.codigo_gerado = enviar_codigo_mfa("linsalex33@gmail.com")
            if self.codigo_gerado: self.tela_verificacao_mfa() 
        else:
            self.label.configure(text="Senha Incorreta!", text_color="red")

    def tela_verificacao_mfa(self):
        self.limpar_tela()
        ctk.CTkLabel(self, text="Verificação MFA", font=("Roboto", 20, "bold")).pack(pady=20)
        self.sublabel_mfa = ctk.CTkLabel(self, text="Digite o código enviado ao seu e-mail:")
        self.sublabel_mfa.pack(pady=5)
        self.entry_mfa = ctk.CTkEntry(self, placeholder_text="000000", width=120, justify="center")
        self.entry_mfa.pack(pady=10)
        ctk.CTkButton(self, text="Confirmar", command=self.validar_mfa, fg_color="green").pack(pady=20)

    def validar_mfa(self):
        if self.entry_mfa.get() == self.codigo_gerado: self.tela_principal() 
        else: self.sublabel_mfa.configure(text="Código Inválido!", text_color="red")

    def resetar_cronometro_inatividade(self, event=None):
        if self.job_inatividade:
            self.after_cancel(self.job_inatividade)
        self.job_inatividade = self.after(120000, self.logout_automatico)

    def logout_automatico(self):
        if hasattr(self, 'entry_busca'): 
            print("Sessão expirada por inatividade.")
            self.tela_login()

    def tela_principal(self):
        self.limpar_tela()
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="Suas Credenciais", font=("Roboto", 22, "bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Nova Senha", width=120, command=self.janela_cadastro).pack(side="right")

        self.entry_busca = ctk.CTkEntry(self, placeholder_text="🔍 Buscar serviço...", width=600)
        self.entry_busca.pack(pady=(0, 15), padx=20)
        self.entry_busca.bind("<KeyRelease>", lambda e: self.atualizar_lista_interface())

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=700, height=450, fg_color="transparent")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.atualizar_lista_interface()

    def atualizar_lista_interface(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        termo = self.entry_busca.get().lower()
        dados = carregar_tudo()
        for item in dados:
            if termo in item['servico'].lower():
                card = ctk.CTkFrame(self.scroll_frame, fg_color="#1e1e1e", border_width=1, border_color="#333333")
                card.pack(fill="x", pady=6, padx=10)
                senha_real = revelar_senha(item['senha'].encode(), self.chave)
                ctk.CTkLabel(card, text=f"{item['servico'].upper()}", font=("Roboto", 13, "bold"), text_color="#3b8ed0").pack(side="left", padx=(15, 5), pady=12)
                ctk.CTkLabel(card, text=f"({item['usuario']})", font=("Roboto", 11), text_color="gray").pack(side="left", pady=12)
                ctk.CTkButton(card, text="🗑", fg_color="transparent", text_color="#e74c3c", width=35, command=lambda s=item['servico']: self.excluir_senha(s)).pack(side="right", padx=5)
                ctk.CTkButton(card, text="✎", fg_color="transparent", text_color="#f1c40f", width=35, command=lambda i=item: self.janela_cadastro(i)).pack(side="right", padx=5)
                btn_copy = ctk.CTkButton(card, text="📋 Copiar", fg_color="#2c3e50", width=80)
                btn_copy.configure(command=lambda s=senha_real, b=btn_copy: self.copiar_senha(s, b))
                btn_copy.pack(side="right", padx=10)

    def janela_cadastro(self, edit_item=None):
        top = ctk.CTkToplevel(self)
        top.title("Gerenciar Credencial")
        top.geometry("400x600")
        top.grab_set() 
        ctk.CTkLabel(top, text="Dados da Credencial", font=("Roboto", 16, "bold")).pack(pady=15)
        ent_serv = ctk.CTkEntry(top, placeholder_text="Serviço", width=250)
        ent_serv.pack(pady=5)
        ent_user = ctk.CTkEntry(top, placeholder_text="Usuário", width=250)
        ent_user.pack(pady=5)
        ent_pw = ctk.CTkEntry(top, placeholder_text="Senha", width=250)
        ent_pw.pack(pady=5)
        
        check_especiais = ctk.CTkCheckBox(top, text="Incluir Símbolos (!@*-_)")
        check_especiais.select()
        check_especiais.pack(pady=10)
        slider_tamanho = ctk.CTkSlider(top, from_=8, to=32, number_of_steps=24)
        slider_tamanho.set(12)
        slider_tamanho.pack(pady=5)
        label_valor = ctk.CTkLabel(top, text="Tamanho: 12")
        label_valor.pack()
        slider_tamanho.configure(command=lambda v: label_valor.configure(text=f"Tamanho: {int(v)}"))

        def acao_gerar():
            nova_senha = gerar_senha_forte(int(slider_tamanho.get()), usar_especiais=bool(check_especiais.get()))
            ent_pw.delete(0, 'end')
            ent_pw.insert(0, nova_senha)

        ctk.CTkButton(top, text="Gerar Senha Forte", fg_color="#27ae60", command=acao_gerar).pack(pady=15)

        def salvar():
            serv, user, pw = ent_serv.get(), ent_user.get(), ent_pw.get()
            if serv and user and pw:
                p_pw = proteger_senha(pw, self.chave)
                if edit_item: atualizar_no_db(serv, user, p_pw.decode())
                else: salvar_no_arquivo(serv, user, p_pw)
                top.destroy()
                self.atualizar_lista_interface()

        ctk.CTkButton(top, text="Salvar", width=200, command=salvar).pack(pady=25)

        if edit_item:
            ent_serv.insert(0, edit_item['servico'])
            ent_serv.configure(state="disabled")
            ent_user.insert(0, edit_item['usuario'])
            ent_pw.insert(0, revelar_senha(edit_item['senha'].encode(), self.chave))

    def excluir_senha(self, servico):
        excluir_no_db(servico)
        self.atualizar_lista_interface()

    def copiar_senha(self, senha, botao):
        self.clipboard_clear()
        self.clipboard_append(senha)
        self.update()
        orig_text, orig_color = botao.cget("text"), botao.cget("fg_color")
        botao.configure(text="✓ Copiado", fg_color="#27ae60")
        self.after(1200, lambda: botao.configure(text=orig_text, fg_color=orig_color))
        self.after(30000, self.limpar_clipboard_seguro, senha)

    def limpar_clipboard_seguro(self, senha_copiada):
        try:
            if self.clipboard_get() == senha_copiada:
                self.clipboard_clear()
                self.clipboard_append(" ")
        except: pass

if __name__ == "__main__":
    app = AppSafeVault()
    app.mainloop()