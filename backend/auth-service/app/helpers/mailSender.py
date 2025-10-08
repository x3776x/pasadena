import smtplib
from email.mime.text import MIMEText
import os 

#bruh
def send_recovery_email(to_email: str, code: str):
    mail_address = os.getenv("MAIL_ADDRESS")
    mail_password = os.getenv("MAIL_PASS")

    if not mail_address or not mail_password:
        print("Email credentials not configured.")
        print(f"Recovery code for {to_email}: {code}")
        return
    
    msg = MIMEText(f"Your password recovery code is: {code}")
    msg["Subject"] = "Account password recovery"
    msg["From"] = mail_address
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_address, mail_password)
            server.sendmail(mail_address, [to_email], msg.as_string())
        print(f"Recovery email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(f"Recovery code for {to_email}: {code}")
