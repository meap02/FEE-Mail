import smtplib
from email.message import EmailMessage
from email.header import decode_header, make_header
import email
import sys
import imaplib
import re
from typing import Literal, Union
from multipledispatch import dispatch

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

    def decode_mime_words(self, s):
        return u''.join(
            word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
            for word, encoding in decode_header(s))
    
    def connect(self):
        '''Connects to the SMTP server and logs in as the user'''
        self.smtp = smtplib.SMTP(self.smtp_server, self.smtp_port) # Establishes the connection to the server with smtplib
        self.eprint(f"Connected to {self.smtp_server}:{self.smtp_port}")
        # The following is for testing with Gmail server, will not be used with our server
        #'''
        #self.smtp.starttls()
        #self.smtp.login(self.username, self.password)
        #'''
        #self.eprint(f"Logged in as {self.username}")

        # Setting up IMAP connection to receive emails
        
        if self.imap_port != '' and self.imap_server != '':
            self.imap = imaplib.IMAP4_SSL(host=self.imap_server, port=self.imap_port)
            self.imap.login(self.username, self.password)
            self.eprint(f"Connected to IMAP server {self.imap_server}:{self.imap_port}")


    def disconnect(self):
        '''Disconnects from the SMTP server'''
        self.smtp.quit() # Disconnecting from the SMTP server
        self.eprint(f"Disconnected from SMTP server {self.smtp_server}:{self.smtp_port}")
        try:
            self.imap.close() # Closing the mailbox
        except: # This is to handle the case where the mailbox is already closed
            pass
        self.imap.logout() # Logging out of the IMAP server
        self.eprint(f"Disconnected from IMAP server {self.imap_server}:{self.imap_port}")

    @dispatch(str, str, str)
    def send_mail(self, to_address: str, subject: str, body: str, cc: str=None, bcc: str=None):
        '''Sends an email to the specified address with the specified subject and body'''
        msg = EmailMessage()
        msg.set_content(body) # Setting the body of the email
        msg['Subject'] = subject # Setting the subject of the email
        frm = f"{self.username}@{self.smtp_server.split('.',1)[1]}" # Setting the from address of the email
        msg['From'] =  frm
        msg['To'] = to_address # Setting the to address of the email
        if cc: # Setting the cc address of the email if it exists
            msg['CC'] = cc
        if bcc: # Setting the bcc address of the email if it exists
            msg['BCC'] = bcc
        self.smtp.send_message(msg) # Sending the email
        self.eprint(f"Sent email to {to_address}")

    @dispatch(EmailMessage)
    def send_mail(self, msg: EmailMessage):
        '''Sends an email with an EmailMessage object'''
        self.smtp.send_message(msg) # Sending the email
        self.eprint(f"Sent email to {msg['To']}")

    def reply_mail(self, email: EmailMessage, body: str, quoting: Union[Literal['prepend', 'append'], None] = 'prepend') -> EmailMessage:
        '''Replies to an email with the specified body'''
        msg = EmailMessage()
        if quoting == 'append': # This is to handle the case where the user wants to append their response to the original email
            body = f"> {email['From']}\n> {email['Subject']}\n> {email['Date']}\n{email.get_content()}\n\n{body}"
        elif quoting == 'prepend': # This is to handle the case where the user wants to prepend their response to the original email
            body = f"{body}\n\n> {email['From']}\n> {email['Subject']}\n> {email['Date']}\n{email.get_content()}"
        
        msg.set_content(body)  # Setting the body of the email
        msg['Subject'] = "Re: " + email["Subject"]
        msg['From'] = email["To"] 
        msg['To'] = email["From"]
        msg['CC'] = email["CC"]
        msg['In-Reply-To'] = email["Message-ID"]
        self.smtp.send_message(msg)
        self.eprint(f"Sent email reply to {email['From']}")
        
    
    def get_mail(self, filter: str, mailbox: str="INBOX", limit=10) -> list[EmailMessage]:
        '''Receives emails from the server and returns them as a list of EmailMessage objects
        filter is a string that can be used to filter the emails received. It is formatted as follows:
        "FILTER1 FILTER2 FILTER3"  "FILTER4=VALUE1 FILTER5=VALUE2"
        Valid filters are: ALL, UNSEEN, SEEN, ANSWERED, UNANSWERED, DELETED, UNDELETED, DRAFT, UNDRAFT, FLAGGED, UNFLAGGED, RECENT, OLD, NEW
        Valid value filters are: BEFORE, ON, SINCE, SUBJECT, BODY, TEXT, FROM, TO, CC, BCC'''
        if self.imap: # Checking if the IMAP connection exists
            valid_filters = ["ALL", "UNSEEN", "SEEN", "ANSWERED", "UNANSWERED", "DELETED", "UNDELETED", "DRAFT", "UNDRAFT", "FLAGGED", "UNFLAGGED", "RECENT", "OLD", "NEW"]
            valid_value_filters = ["BEFORE", "ON", "SINCE", "SUBJECT", "BODY", "TEXT", "FROM", "TO", "CC", "BCC"]
            # Dates to be formatted as dd MMM yyyy HH:mm:ss Z
            self.imap.select("\"" + mailbox + "\"") # Note that this mailbox must be kept track of by the interface
            search_string = "(ALL "
            if filter == "": # This is to handle the case where there is no filter
                typ, data = self.imap.search(None, "ALL") # Searching for the emails
                if typ == 'OK':
                    email_list = []
                    data_list = data[0].split()
                    for num in range(1, min(limit, len(data_list))): # This is to handle the case where there is a limit
                        typ, data = self.imap.fetch(data_list[-num], '(RFC822)')
                        if typ == 'OK':
                            toadd = email.message_from_bytes(data[0][1])
                            if "=?UTF-8?" in toadd["Subject"]:
                                toadd["Subject"] = self.decode_mime_words(toadd["Subject"])
                            email_list.append(toadd)
                        else:
                            self.eprint(f"Error fetching mail with search string {search_string} with error code {typ}")
                else:
                    self.eprint(f"Error searching for mailbox for {filter} with error code {typ}")
            else:
                filter_list = re.split(r'\s(?=(?:[^\'\"`]*([\'\"`])[^\'\"`]*\1)*[^\'\"`]*$)', filter)
                for i in range(len(filter_list)-1): # This is to handle the case where there are multiple filters
                    if '=' in filter_list[i]: # This is to handle the case where there is a value filter
                        filter_list[i] = filter_list[i].split('=') # Splitting the filter into the filter and the value
                        filter_list[i][0] = filter_list[i][0].upper() # Making the filter uppercase
                        if filter_list[i][0] in valid_value_filters: # Checking if the filter is valid
                            search_string += f"({filter_list[i][0]} {filter_list[i][1]}) " # Adding the filter to the search string
                        else:
                            self.eprint("Invalid filter: " + filter_list[i][0])
                    else: # This is to handle the case where there is no value filter
                        filter_list[i] = filter_list[i].upper() # Making the filter uppercase
                        if filter_list[i] in valid_filters: # Checking if the filter is valid
                            search_string += f"({filter_list[i]}) " # Adding the filter to the search string
                        else:
                            self.eprint("Invalid filter: " + filter_list[i])
                if '=' in filter_list[-1]: # Repeat of the previous code, but for the last filter
                        filter_list[-1] = filter_list[-1].split('=')
                        filter_list[-1][0] = filter_list[-1][0].upper()
                        if filter_list[-1][0] in valid_value_filters:
                            search_string += f"({filter_list[-1][0]} {filter_list[-1][1]})" # Note that there is no space after the last filter
                        else:
                            self.eprint("Invalid filter: " + filter_list[-1][0])
                else:
                    filter_list[-1] = filter_list[-1].upper()
                    if filter_list[-1] in valid_filters:
                        search_string += f"({filter_list[-1]})" # Note that there is no space after the last filter
                    else:
                        self.eprint("Invalid filter: " + filter_list[-1])
                search_string += ")" # Closing the search string
                typ, data = self.imap.search(None, search_string) # Searching for the emails
                if typ == 'OK': # Checking if the search was successful
                    email_list = []
                    for num in data[0].split():
                        typ, data = self.imap.fetch(num, '(RFC822)') # Fetching the email
                        if typ == 'OK': # Checking if the fetch was successful
                            toadd = email.message_from_bytes(data[0][1])
                            if "=?UTF-8?" in toadd["Subject"]:
                                toadd["Subject"] = self.decode_mime_words(toadd["Subject"])
                            email_list.append(toadd) # Adding the email to the list
                        else:
                            self.eprint(f"Error fetching mail with search string {search_string} with error code {typ}")
                else:
                    self.eprint(f"Error searching for mailbox for {filter} with error code {typ}")
        return email_list # Returning the list of emails


    def list_mailboxes(self):
        '''Lists all mailboxes'''
        if self.imap: # Checking if the IMAP connection exists
            return [x.decode().split(' "/" ')[-1].replace('"', "") for x in self.imap.list()[1] if "\\Noselect" not in x.decode()]
        else:
            return []
    '''
    The layout for creds.json is as follows:
    {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_server": "imap.gmail.com",
        "imap_port": "993",
        "username": "
        "password": "
    }

    This is for gmail specifically, but the same format can be used for other servers
    '''   
