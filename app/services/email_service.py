import os
import smtplib
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request

# Chave secreta usada para assinar o token de e-mail (idealmente em .env)
SECRET_KEY = "chave-super-secreta"
SECURITY_SALT = "email-confirm-salt"

def generate_confirmation_token(email: str):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_SALT)

def confirm_token(token: str, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECURITY_SALT,
            max_age=expiration
        )
        return email
    except Exception:
        return False

def send_confirmation_email(request: Request, user_email: str, user_name: str):
    token = generate_confirmation_token(user_email)
    
    # URL base da requisição (ex: http://localhost:8000)
    base_url = str(request.base_url).strip("/")
    confirm_url = f"{base_url}/users/confirm/{token}"
    
    # Assunto e corpo do email
    subject = "Confirme seu cadastro no CRM Turismo"
    body = f"""Olá {user_name},

Seu usuário foi criado no CRM Turismo.
Para ativar sua conta e acessar o painel, clique no link abaixo:

{confirm_url}

Se você não solicitou este cadastro, ignore este e-mail.
"""

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", 587)
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")

    if smtp_host and smtp_user and smtp_pass:
        # Tenta enviar e-mail real
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = user_email

            server = smtplib.SMTP(smtp_host, int(smtp_port))
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"E-mail de confirmação enviado para {user_email}")
        except Exception as e:
            print(f"Erro ao enviar e-mail SMTP: {e}")
            print(f"URL de Confirmação (Fallback): {confirm_url}")
    else:
        # Fallback (Mock) caso as credenciais não existam no .env
        print(f"--- MOCK EMAIL PARA {user_email} ---")
        print(body)
        print(f"--------------------------------------")
