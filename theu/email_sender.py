from theu import app
import sendgrid
import os
from sendgrid.helpers.mail import *

def send_email(to_email, subject, email_text, from_email="theu@gmail.com"):
    sg = sendgrid.SendGridAPIClient(apikey=app.config["SENDGRID_API_KEY"])
    content = Content("text/plain", email_text)
    mail = Mail(Email(from_email), subject, Email(to_email), content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response
