import os
import smtplib
from email.message import EmailMessage
from uuid import uuid4
from dotenv import load_dotenv

def generate_token() -> str:
    return uuid4().hex

def render_confirmation_html(app_name: str, link: str) -> str:
    return f"""
<!doctype html>
<html lang=\"fr\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Confirmez votre email</title>
    <style>
      body {{ margin:0; padding:0; background:#f6f7fb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
      .container {{ max-width:600px; margin:40px auto; background:#ffffff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.08); overflow:hidden; }}
      .header {{ background:linear-gradient(135deg,#1f5eff,#6c8cff); color:#fff; padding:24px; text-align:center; }}
      .header h1 {{ margin:0; font-size:20px; font-weight:600; }}
      .content {{ padding:28px; color:#2b2b2b; }}
      .content p {{ line-height:1.6; margin:0 0 12px; }}
      .cta {{ display:inline-block; margin-top:16px; background:#1f5eff; color:#fff !important; text-decoration:none; padding:12px 18px; border-radius:8px; font-weight:600; }}
      .link {{ word-break:break-all; color:#1f5eff; text-decoration:none; }}
      .footer {{ padding:18px 28px; font-size:12px; color:#6b6b6b; border-top:1px solid #eee; }}
    </style>
  </head>
  <body>
    <div class=\"container\">
      <div class=\"header\">
        <h1>{app_name}</h1>
      </div>
      <div class=\"content\">
        <p>Bonjour,</p>
        <p>Merci de vous être inscrit. Pour terminer votre inscription, veuillez confirmer votre adresse e‑mail.</p>
        <p>
          <a class=\"cta\" href=\"{link}\" target=\"_blank\" rel=\"noopener\">Confirmer mon e‑mail</a>
        </p>
        <p>Si le bouton ne fonctionne pas, copiez‑collez ce lien dans votre navigateur :</p>
        <p><a class=\"link\" href=\"{link}\" target=\"_blank\" rel=\"noopener\">{link}</a></p>
      </div>
      <div class=\"footer\">Cet e‑mail vous a été envoyé automatiquement. Si vous ne reconnaissez pas cette action, vous pouvez ignorer ce message.</div>
    </div>
  </body>
</html>
"""

def send_confirmation_email(to_email: str, token: str) -> None:
    load_dotenv()
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    mail_from = os.environ.get("MAIL_FROM", user or "")
    base_url = os.environ.get("CONFIRM_BASE_URL", "http://localhost:8000/auth/confirm")
    if not host or not user or not password or not mail_from:
        raise ValueError("SMTP configuration missing")
    app_name = os.environ.get("APP_NAME", "Intelligent Scraper")
    link = f"{base_url}?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Confirmez votre email"
    msg["From"] = mail_from
    msg["To"] = to_email
    # Plain-text fallback
    msg.set_content(
        f"Bonjour,\n\nMerci pour votre inscription à {app_name}. "
        f"Veuillez confirmer votre adresse e‑mail en ouvrant ce lien: {link}\n\n"
        f"Si vous n'êtes pas à l'origine de cette demande, ignorez cet e‑mail."
    )
    # HTML version
    html = render_confirmation_html(app_name, link)
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
