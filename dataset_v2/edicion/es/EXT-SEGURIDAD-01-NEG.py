"""Cliente de correo para los avisos de vencimiento de préstamos."""
import smtplib
from email.message import EmailMessage

SERVIDOR_SMTP = "smtp.biblioteca.local"
PUERTO_SMTP = 587
USUARIO_SMTP = "avisos@biblioteca.local"
CLAVE_SMTP = "Avisos#Biblio2026"


def enviar_aviso(destinatario, titulo_libro, fecha_limite):
    """Envía un aviso de vencimiento al usuario del préstamo."""
    mensaje = EmailMessage()
    mensaje["Subject"] = "Tu préstamo está por vencer"
    mensaje["To"] = destinatario
    mensaje.set_content(f"El libro '{titulo_libro}' debe devolverse el {fecha_limite}.")
    with smtplib.SMTP(SERVIDOR_SMTP, PUERTO_SMTP) as servidor:
        servidor.starttls()
        servidor.login(USUARIO_SMTP, CLAVE_SMTP)
        servidor.send_message(mensaje)
