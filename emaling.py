import smtplib
import imghdr
import os
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

sender = os.getenv("SENDER")
psw = os.getenv("PSW")
recipient = os.getenv("RECIPIENT")


def send_email(image_path):
    email_msg = EmailMessage()
    email_msg["Subject"] = "Movement detected on cam!"
    email_msg["From"] = f"Motion Detection <{sender}>"
    email_msg.set_content("Hey, something's moving over there! Go see what it's about.")

    with open(image_path, "rb") as f:
        img_to_attach = f.read()

    email_msg.add_attachment(img_to_attach, maintype="image", subtype=imghdr.what(None, img_to_attach))

    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(sender, psw)
    gmail.sendmail(sender, recipient, email_msg.as_string())
    gmail.quit()


# For testing purposes
if __name__ == "__main__":
    send_email(image_path="img/20240731094249945670.png")
    print("Sent")