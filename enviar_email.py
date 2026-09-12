"""
Envia o relatório por e-mail via SMTP. Sem as variáveis de ambiente configuradas,
salva o HTML em disco (pasta saida/) em vez de falhar — assim dá pra testar o
projeto inteiro sem precisar configurar e-mail de verdade.

Variáveis de ambiente usadas:
  SMTP_HOST, SMTP_PORT (padrão 587), SMTP_USER, SMTP_PASS
  EMAIL_REMETENTE (padrão = SMTP_USER), EMAIL_DESTINO (pode ser uma lista separada por vírgula)
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def enviar_ou_salvar(html: str, assunto: str) -> str:
    """Envia por e-mail se SMTP estiver configurado; senão salva localmente.
    Retorna uma string descrevendo o que foi feito (pra log/print)."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    destino = os.getenv("EMAIL_DESTINO")

    if smtp_host and smtp_user and smtp_pass and destino:
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        remetente = os.getenv("EMAIL_REMETENTE", smtp_user)
        destinatarios = [d.strip() for d in destino.split(",") if d.strip()]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = ", ".join(destinatarios)
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(remetente, destinatarios, msg.as_string())

        return f"E-mail enviado para {', '.join(destinatarios)}."

    os.makedirs("saida", exist_ok=True)
    nome_arquivo = f"saida/relatorio_{datetime.now().strftime('%Y-%m-%d_%H%M')}.html"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(html)
    return (
        f"SMTP não configurado — relatório salvo em {nome_arquivo}. "
        "Configure SMTP_HOST, SMTP_USER, SMTP_PASS e EMAIL_DESTINO para enviar por e-mail de verdade."
    )
