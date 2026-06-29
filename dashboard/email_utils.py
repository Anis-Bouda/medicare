import smtplib
from email.mime.text import MIMEText

EXPEDITEUR = "projetmedicarepro@gmail.com"
MOT_DE_PASSE_APP = ""    

def envoyer_email(destinataire, sujet, message):
    # envoie un mail renvoie true si cest bon ou false avec lerreur
    try:
        msg = MIMEText(message)
        msg["Subject"] = sujet
        msg["From"] = EXPEDITEUR
        msg["To"] = destinataire

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
            serveur.login(EXPEDITEUR, MOT_DE_PASSE_APP.replace(" ", "").replace("\xa0", ""))
            serveur.send_message(msg)
        return True, "Email envoyé !"
    except Exception as e:
        return False, f"Erreur d'envoi : {e}"