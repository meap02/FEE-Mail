import smtplib
from email.message import EmailMessage
import email
import json
import sys
import imaplib
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
        self.smtp = None
        self.imap = None

    def eprint(self, *args, **kwargs):
        '''Prints to stderr'''
        print(*args, file=sys.stderr, **kwargs)
    
    def connect(self):
        '''Connects to the SMTP server and logs in as the user'''
        self.smtp = smtplib.SMTP(self.smtp_server, self.smtp_port) # Establishes the connection to the server with smtplib
        self.eprint("Connected to {:s}:{:d}".format(self.smtp_server, self.smtp_port)) 
        # The following is for testing with Gmail server, will not be used with our server
        #'''
        self.smtp.starttls() 
        self.smtp.login(self.username, self.password)
        #'''
        self.eprint("Logged in as {:s}".format(self.username))

        # Setting up IMAP connection to receive emails
        
        self.imap = imaplib.IMAP4_SSL(host=self.imap_server, port=self.imap_port)
        self.imap.login(self.username, self.password)
        self.eprint("Connected to IMAP server")


    def disconnect(self):
        '''Disconnects from the SMTP server'''
        self.smtp.quit()
        self.eprint("Disconnected from {:s}:{:d}".format(self.smtp_server, self.smtp_port))
        self.imap.logout()
        self.imap.close()
        self.eprint("Disconnected from IMAP server")

    def send_email(self, to_address, subject, body):
        '''Sends an email to the specified address with the specified subject and body'''
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        frm = "{:s}@{:s}".format(self.username, self.smtp_server.split(".",1)[1])
        msg['From'] =  frm
        msg['To'] = to_address
        self.smtp.send_message(msg)
        self.eprint("Sent email to {:s}".format(to_address))
        
    
    def get_mail(self, mailbox="INBOX", filter="ALL"):
        '''Receives emails from the server and returns them as a list of EmailMessage objects'''
        valid_filters = ["ALL", "UNSEEN", "SEEN", "ANSWERED", "UNANSWERED", "DELETED", "UNDELETED", "DRAFT", "UNDRAFT", "FLAGGED", "UNFLAGGED", "RECENT", "OLD", "NEW"]
        valid_value_filters = ["BEFORE", "ON", "SINCE", "SUBJECT", "BODY", "TEXT", "FROM", "TO", "CC", "BCC"]
        # Dates to be formatted as dd MMM yyyy HH:mm:ss Z
        self.imap.select(mailbox)
        search_string = "(ALL "
        filter_list = re.split(r'\s(?=(?:[^\'\"`]*([\'\"`])[^\'\"`]*\1)*[^\'\"`]*$)', filter)
        for i in range(len(filter_list)-1):
            if '=' in filter_list[i]:
                filter_list[i] = filter_list[i].split('=')
                if filter_list[i][0] in valid_value_filters:
                    search_string += f"({filter_list[i][0]} {filter_list[i][1]}) "
                else:
                    self.eprint("Invalid filter")
            else:
                if filter_list[i] in valid_filters:
                    search_string += f"({filter_list[i]}) "
                else:
                    self.eprint("Invalid filter")
        if '=' in filter_list[-1]:
                filter_list[-1] = filter_list[-1].split('=')
                if filter_list[-1][0] in valid_value_filters:
                    search_string += f"({filter_list[-1][0]} {filter_list[-1][1]})"
                else:
                    self.eprint("Invalid filter")
        else:
            if filter_list[-1] in valid_filters:
                search_string += f"({filter_list[-1]})"
            else:
                self.eprint("Invalid filter")
        search_string += ")"
        typ, data = self.imap.search(None, search_string)
        if typ == 'OK':   
            email_list = []
            for num in data[0].split():
                typ, data = self.imap.fetch(num, '(RFC822)')
                if typ == 'OK':
                    email_list.append(email.message_from_bytes(data[0][1]))
                else:
                    self.eprint(f"Error fetching mail {num}")
            return email_list
        else:
            self.eprint(f"Error searching for mailbox for {filter} with error code {typ}")
            

    def list_mailboxes(self):
        '''Lists all mailboxes'''
        return [x.decode().split(' "/" ')[-1].replace('"', "") for x in self.imap.list()[1]]
    
    
    def status(self, mailbox):
        '''Returns the status of a mailbox, including the total number of messages and the number of unread messages [total, unread]'''
        return re.findall(r'((?<=MESSAGES\s)\d+|(?<=UNSEEN\s)\d+)', self.imap.status(mailbox, "(MESSAGES UNSEEN)")[1][0].decode())

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
    print(client.get_mail(filter='FROM="kjjust7@gmail.com" SUBJECT="LOOK AT ME!"', mailbox="INBOX")[0]["Subject"])
