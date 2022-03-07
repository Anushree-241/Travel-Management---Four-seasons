from ast import List
from distutils import debug
import smtplib, ssl
from email.mime.text import MIMEText

class Email:

    def __init__(self, loginmail, password) -> None:
        self.port = 465
        self.smtp_server_domain_name = "smtp.gmail.com"
        self.loginemail = loginmail
        self.password = password
    
    def sendMail(self,to:List,subject,message) -> bool:
        try:
            with smtplib.SMTP(self.smtp_server_domain_name) as service:
                ssl_context = ssl.create_default_context()
                service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
                service.login(self.loginemail, self.password)
               #msg = MIMEText(message)
                result = service.sendmail(self.loginemail, to, f"Subject: {subject}\n{message}")
                return result
        except smtplib.SMTPException as s:
            print("Something went wrong...", str(s)) 
            
  