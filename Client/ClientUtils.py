import smtplib
from email.message import EmailMessage
import email
import json
import sys
import imaplib
from redbox import EmailBox, gmail
import re



class ClientUtils:
    def __init__(self, smtp_server, smtp_port, imap_server, imap_port, username, password):
        '''Initializes the client utils class with the specified SMTP server, port, username, and password'''
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.smtp_connection = None
        self.inbox = None
        self.selected_mailbox = None

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
        
        self.inbox = EmailBox(host=self.imap_server, port=self.imap_port, username=self.username, password=self.password)
        self.eprint("Connected to IMAP server")


    def disconnect(self):
        '''Disconnects from the SMTP server'''
        self.smtp_connection.quit()
        self.eprint("Disconnected from {:s}:{:d}".format(self.smtp_server, self.smtp_port))
        self.inbox.logout()
        self.eprint("Disconnected from IMAP server")

    def send_email(self, to_address, subject, body):
        '''Sends an email to the specified address with the specified subject and body'''
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        frm = "{:s}@{:s}".format(self.username, self.smtp_server.split(".",1)[1])
        msg['From'] =  frm
        msg['To'] = to_address
        self.smtp_connection.send_message(msg)
        self.eprint("Sent email to {:s}".format(to_address))
        
    def get_unread(self, mailbox):
        '''Receives emails from the server and returns them as a list of EmailMessage objects'''
        self.inbox.select(mailbox)
        emails = []
        _, data = self.inbox.search(None, "UNSEEN")
        ids = data[0]
        id_list = ids.split()
        for id in id_list:
            _, data = self.inbox.fetch(id, "(RFC822)")
            raw_email = data[0][1]
            mail = email.message_from_bytes(raw_email)
            emails.append(mail)
        self.inbox.close()
        return emails
    
    def get_mail(self, filter="ALL"):
        '''Receives emails from the server and returns them as a list of EmailMessage objects'''
        valid_filters = ["ALL", "UNSEEN", "SEEN", "ANSWERED", "UNANSWERED", "DELETED", "UNDELETED", "DRAFT", "UNDRAFT", "FLAGGED", "UNFLAGGED", "RECENT", "OLD", "NEW"]
        valid_value_filters = ["BEFORE", "ON", "SINCE", "SUBJECT", "BODY", "TEXT", "FROM", "TO", "CC", "BCC"]
        # Dates to be formatted as dd MMM yyyy HH:mm:ss Z
        if filter.upper in valid_filters:
            return self.selected_mailbox.search(filter)
        else:
            search_string = ""
            filetr_list = re.split(r'=|', filter)
            for i in range(len()):
                if i == 0:
                    search_string += filter.split("=")[i]
                else:
                    search_string += f' "{filter.split("=")[i]}"'
            return self.selected_mailbox.search(f"({self.selected_mailbox} {filter}")
            
        
    

    
    def select_mailbox(self, mailbox):
        '''Selects the specified mailbox'''
        self.selected_mailbox= self.inbox[mailbox]
    
    def unselect_mailbox(self):
        '''Unselect the current mailbox'''
        self.selected_mailbox = None

    def list_mailboxes(self):
        '''Lists all mailboxes'''
        return [x.name for x in self.inbox.mailfolders if "\\Noselect" not in x.flags]
    
    def status(self, mailbox):
        '''Returns the status of a mailbox, including the total number of messages and the number of unread messages [total, unread]'''
        return re.findall(r'((?<=MESSAGES\s)\d+|(?<=UNSEEN\s)\d+)', self.inbox.status(mailbox, "(MESSAGES UNSEEN)")[1][0].decode())

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
    client = ClientUtils(
        creds['smtp_server'], 
        creds['smtp_port'], 
        creds['imap_server'], 
        creds['imap_port'], 
        creds['username'], 
        creds['password']) # Creation of the client class
    client.connect()
    print(client.list_mailboxes())
