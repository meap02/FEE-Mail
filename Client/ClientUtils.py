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
        self.eprint(f"Disconnected from SMTP server {self.smtp_server}:{self.smtp_port}")
        try:
            self.imap.close()
        except:
            pass
        self.imap.logout()
        self.eprint(f"Disconnected from IMAP server {self.imap_server}:{self.imap_port}")

    def send_mail(self, to_address, subject, body, cc=None, bcc=None):
        '''Sends an email to the specified address with the specified subject and body'''
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        frm = "{:s}@{:s}".format(self.username, self.smtp_server.split(".",1)[1])
        msg['From'] =  frm
        msg['To'] = to_address
        if cc:
            msg['CC'] = cc
        if bcc:
            msg['BCC'] = bcc
        self.smtp.send_message(msg)
        self.eprint("Sent email to {:s}".format(to_address))

    def reply_mail(self, email, body):
        '''Replies to an email with the specified body'''
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = "Re: " + email["Subject"]
        msg['From'] = email["To"]
        msg['To'] = email["From"]
        msg['CC'] = email["CC"]
        msg['In-Reply-To'] = email["Message-ID"]
        self.smtp.send_message(msg)
        self.eprint("Sent email reply to {:s}".format(email["From"]))
        
    
    def get_mail(self, mailbox="INBOX", filter="UNSEEN"):
        '''Receives emails from the server and returns them as a list of EmailMessage objects
        filter is a string that can be used to filter the emails received. It is formatted as follows:
        "FILTER1 FILTER2 FILTER3"  "FILTER4=VALUE1 FILTER5=VALUE2"
        Valid filters are: ALL, UNSEEN, SEEN, ANSWERED, UNANSWERED, DELETED, UNDELETED, DRAFT, UNDRAFT, FLAGGED, UNFLAGGED, RECENT, OLD, NEW
        Valid value filters are: BEFORE, ON, SINCE, SUBJECT, BODY, TEXT, FROM, TO, CC, BCC'''
        valid_filters = ["ALL", "UNSEEN", "SEEN", "ANSWERED", "UNANSWERED", "DELETED", "UNDELETED", "DRAFT", "UNDRAFT", "FLAGGED", "UNFLAGGED", "RECENT", "OLD", "NEW"]
        valid_value_filters = ["BEFORE", "ON", "SINCE", "SUBJECT", "BODY", "TEXT", "FROM", "TO", "CC", "BCC"]
        # Dates to be formatted as dd MMM yyyy HH:mm:ss Z
        self.imap.select(mailbox)
        search_string = "(ALL "
        filter_list = re.split(r'\s(?=(?:[^\'\"`]*([\'\"`])[^\'\"`]*\1)*[^\'\"`]*$)', filter)
        print(filter_list)
        for i in range(len(filter_list)-1):
            if '=' in filter_list[i]:
                filter_list[i] = filter_list[i].split('=')
                filter_list[i][0] = filter_list[i][0].upper()
                if filter_list[i][0] in valid_value_filters:
                    search_string += f"({filter_list[i][0]} {filter_list[i][1]}) "
                else:
                    self.eprint("Invalid filter")
            else:
                filter_list[i] = filter_list[i].upper()
                if filter_list[i] in valid_filters:
                    search_string += f"({filter_list[i]}) "
                else:
                    self.eprint("Invalid filter")
        if '=' in filter_list[-1]:
                filter_list[-1] = filter_list[-1].split('=')
                filter_list[-1][0] = filter_list[-1][0].upper()
                if filter_list[-1][0] in valid_value_filters:
                    search_string += f"({filter_list[-1][0]} {filter_list[-1][1]})"
                else:
                    self.eprint("Invalid filter")
        else:
            filter_list[-1] = filter_list[-1].upper()
            if filter_list[-1] in valid_filters:
                search_string += f"({filter_list[-1]})"
            else:
                self.eprint("Invalid filter")
        search_string += ")"
        print(search_string)
        typ, data = self.imap.search(None, search_string)
        if typ == 'OK':
            email_list = []
            for num in data[0].split():
                typ, data = self.imap.fetch(num, '(RFC822)')
                if typ == 'OK':
                    email_list.append(email.message_from_bytes(data[0][1]))
                else:
                    self.eprint(f"Error fetching mail {num}")
        else:
            self.eprint(f"Error searching for mailbox for {filter} with error code {typ}")
        return email_list


    def list_mailboxes(self):
        '''Lists all mailboxes'''
        return [x.decode().split(' "/" ')[-1].replace('"', "") for x in self.imap.list()[1]]

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
