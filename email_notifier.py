import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_notification(video_id, title):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    if not sender or not password or not recipient:
        print("Email configuration is missing. Cannot send notification.")
        return False

    subject = f"YouTube Bot Processed: {title}"
    body = f"The YouTube Description Bot has successfully optimized and updated the video: '{title}'.\n\nVideo ID: {video_id}\nLink: https://www.youtube.com/watch?v={video_id}"

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, recipient, text)
        server.quit()
        print(f"Email notification sent to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        return False
