import smtplib
from email.message import EmailMessage
import os
from config import GMAIL_USER, GMAIL_PASS

def enviar_correo(asunto, cuerpo, archivo_pdf, destino):
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = destino  # Usamos el parámetro destino en lugar de la constante
    msg["Subject"] = asunto
    msg.set_content(cuerpo)
    
    with open(archivo_pdf, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(archivo_pdf)
    
    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()  # Habilita cifrado TLS
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.send_message(msg)
        print(f"Correo enviado correctamente a {destino}.")
    except Exception as e:
        print(f"Error enviando correo: {e}")