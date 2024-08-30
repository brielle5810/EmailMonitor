import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests

# env variables
GMAIL_USERNAME = os.getenv('GMAIL_USERNAME')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
# im only looking for a specific email/emailer:
SPECIAL_EMAIL = os.getenv('SPECIAL_EMAIL')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
DISCORD_USER = os.getenv('DISCORD_USER')

def connect_email():
    # conenct to gmail server and login
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USERNAME, GMAIL_PASSWORD)

    # search for unseen emails from desired email
    imap.select("INBOX")
    status, messages = imap.search(None, f'(UNSEEN FROM "{SPECIAL_EMAIL}")')

    # check messages is not empty byte string
    if messages[0] != b'':
        statusgood, messagesgood = imap.search(None,
                                               f'UNSEEN FROM "{SPECIAL_EMAIL}" (OR (TEXT "Congratulations") (OR (TEXT "Congratulations!") (TEXT "congratulations")))')
        statusbad, messagesbad = imap.search(None,
                                             f'UNSEEN FROM "{SPECIAL_EMAIL}" (OR (TEXT "unfortunately") (OR (TEXT "Unfortunately") (TEXT "Unfortunately,")))')

        # if the email contains the word "Congratulations" -> send GOOD email and ping,
        # "unfortunately" -> send BAD email and ping, neither -> send neutral email and ping
        note = "Couldn't tell importance of email."

        if messagesgood[0] != b'':
            note = "Congratulations!"

        elif messagesbad[0] != b'':
            note = "Bad news."

        # email my school email
        send_email(note)
        # send discord alert, ping me!
        send_discord_alert(note)

    # close, logout!
    imap.close()
    imap.logout()

def send_email(note):
    # set up SMTP server -> sending the email
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(GMAIL_USERNAME, GMAIL_PASSWORD)

    # create message with subject
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USERNAME
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"IMPORTANT: You've received an email from {SPECIAL_EMAIL}"
    body = f"{note} You've received an email from {SPECIAL_EMAIL}."

    msg.attach(MIMEText(body, 'plain'))
    smtp_server.sendmail(GMAIL_USERNAME, RECEIVER_EMAIL, msg.as_string())
    smtp_server.quit()

    print(f"Notification email sent to {RECEIVER_EMAIL}.")

def send_discord_alert(note):
    #discord_user is the id, this allows us to ping the user
    discord_alert = {
        "content": f"{note} <@{DISCORD_USER}> You've received an email from {SPECIAL_EMAIL}"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=discord_alert)
    if response.status_code == 204:
        print("Discord message sent successfully.")
    else:
        print(f"Failed to send Discord message. Status code: {response.status_code}")

if __name__ == '__main__':
    connect_email()
