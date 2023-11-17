
import smtplib
from email.message import EmailMessage
import email
import json
import sys
import imaplib



class ClientUtils:
    def __init__(self, smtp_server, smtp_port, username, password):
        '''Initializes the client utils class with the specified SMTP server, port, username, and password'''
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.smtp_connection = None
        self.inbox = None

    def eprint(self, *args, **kwargs):
        '''Prints to stderr'''
        print(*args, file=sys.stderr, **kwargs)
    
    def connect(self):
        '''Connects to the SMTP server and logs in as the user'''
        self.smtp_connection = smtplib.SMTP(self.smtp_server, self.smtp_port) # Establishes the connection to the server with smtplib
        self.eprint("Connected to {:s}:{:d}".format(self.smtp_server, self.smtp_port)) 
        # The following is for testing with Gmail server, will not be used with our server
        #'''
        self.smtp_connection.starttls() 
        self.smtp_connection.login(self.username, self.password)
        #'''
        self.eprint("Logged in as {:s}".format(self.username))

        # Setting up IMAP connection to receive emails
        self.inbox = imaplib.IMAP4_SSL(self.smtp_server)
        self.inbox.login(self.username, self.password)
        self.inbox.select("inbox")
        self.eprint("Connected to IMAP server")


    def disconnect(self):
        '''Disconnects from the SMTP server'''
        self.smtp_connection.quit()
        self.eprint("Disconnected from {:s}:{:d}".format(self.smtp_server, self.smtp_port))

    def send_email(self, to_address, subject, body):
        '''Sends an email to the specified address with the specified subject and body'''
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] =  "{:s}@{:s}".format(self.username, self.smtp_server.split(".",1)[1])
        msg['To'] = to_address
        self.smtp_connection.send_message(msg)
        self.eprint("Sent email to {:s}".format(to_address))
        
    def receive_emails(self):
        '''Receives emails from the server and returns them as a list of EmailMessage objects'''
        self.inbox.select("inbox")
        _, data = self.inbox.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()
        emails = []
        for id in id_list:
            _, data = self.inbox.fetch(id, "(RFC822)")
            raw_email = data[0][1]
            mail = email.message_from_bytes(raw_email)
            emails.append(mail)
        return emails

if __name__ == "__main__":
    '''
    The layout for creds.json is as follows:
    {
        "FirstName": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "
            "password": "
        }
    }

    This is for gmail specifically, but the same format can be used for other servers
    '''
    with open("Client/creds.json", "r") as f:
        creds = json.load(f)
    creds = creds["Kyle"] # Change this to your name during testing
    client = ClientUtils(creds['smtp_server'], creds['smtp_port'], creds['username'], creds['password']) # Creation of the client class
    client.connect()
    client.receive_emails()