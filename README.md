# 🔒 SafeVault Web

> **Segurança offline, interface moderna.** Um cofre de senhas local construído para manter suas credenciais 100% sob o seu controle.

O SafeVault é um projeto focado em proteger informações sensíveis utilizando criptografia forte em um ambiente totalmente local (Client-Server na própria máquina). Diferente de serviços na nuvem, aqui nenhum dado seu viaja pela internet.

## 💡 Por que usar o SafeVault?

- **Criptografia Real:** Utilizamos a biblioteca `cryptography` (algoritmo Fernet) para embaralhar suas senhas no banco de dados. Sem a sua Senha Mestra (guardada em um `.dat` separado), o banco de dados é ilegível.
- **Área de Transferência Inteligente:** Copiou uma senha? O SafeVault apaga ela da memória do seu PC após 30 segundos (via `pyperclip`) para evitar que softwares maliciosos leiam o que você copiou.
- **Gerador Embutido:** Crie senhas aleatórias, longas e seguras com um único clique na hora de adicionar um novo serviço.
- **Design Clean:** Uma interface web moderna, escura e responsiva, focada na usabilidade.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3 + Flask
- **Banco de Dados:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Segurança:** Fernet (Criptografia Simétrica)

## 🚀 Rodando o projeto na sua máquina

1. Faça o clone deste repositório:
   git clone [https://github.com/AlexLins33/safevault.git](https://github.com/AlexLins33/safevault.git)

2. Entre na pasta do projeto:
   cd safevault

3. Entre na pasta do projeto:
   pip install flask cryptography pyperclip

4. Inicie o servidor:
   python app.py

5. Abra o seu navegador e acesse:
   http://127.0.0.1:5000 ou dê crtl+click no endereço no propio terminal
