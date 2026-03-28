import smtplib
import secrets
from email.message import EmailMessage

def enviar_codigo_mfa(email_destino):
    codigo = "".join(secrets.choice("0123456789") for _ in range(6))
    
    msg = EmailMessage()
    msg['Subject'] = "SafeVault - Código de Acesso"
    msg['From'] = "teste12teste3409@gmail.com"
    msg['To'] = "linsalex33@gmail.com"
    msg.set_content(f"Seu código de segurança é: {codigo}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("teste12teste3409@gmail.com", "kdanobijimvcdpfo")
            smtp.send_message(msg)
            return codigo 
    except Exception:
        return None