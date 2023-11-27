
import cmd
from ClientUtils import ClientUtils
import json
from getpass import getpass


class ClientShell(cmd.Cmd):
    intro = 'Welcome to the FEE-Mail client shell. Type help or ? to list commands.\n'
    prompt = '(FEE-Mail)$ '

    def __init__(self):
        super().__init__()
        creds_exists = input('Do you have a credential file? (y/n) ')
        if creds_exists == 'y':
            while True:
                creds_file = "Client/creds.json"
                #creds_file = input('Enter credential file path: ')
                try:
                    with open(creds_file) as f:
                        creds = json.load(f)
                    if 'smtp_server' in creds and 'smtp_port' in creds and 'username' in creds and 'password' in creds:
                        break
                    else:
                        print('Invalid credential file')
                except FileNotFoundError:
                    print('File not found')
            smtp_server = creds['smtp_server']
            smtp_port = creds['smtp_port']
            username = creds['username']
            password = creds['password']
        else:
            smtp_server = input('Enter SMTP server: ')
            smtp_port = int(input('Enter SMTP port: '))
            username = input('Enter username (all text before the @ symbol): ')
            password = getpass('Enter password: ')
        self.client_utils = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, username=username, password=password)
        self.current_mailbox = None
        self.client_utils.connect()


    def do_send(self, arg):
        'Send an email and be prompted for the to, subject, and body. Usage: send'
        to = input('To: ')
        if ',' in to:
            to = to.split(',')
            to = [address.strip() for address in to]
        else:
            to = [to]
        subject = input('Subject: ')
        body = input('Body: ')
        for address in to:
            self.client_utils.send_email(address, subject, body)
            print('Email sent successfully to ' + address)

    def do_unread(self, arg):
        'List all unread emails in the current mailbox. Usage: unread'
        if self.current_mailbox: 
            emails = self.client_utils.get_unread(self.current_mailbox)
            for email in emails:
                if email.get_content_maintype() == 'multipart':
                    body = email.get_payload()[0].get_payload()
                print(f'{email["subject"]}\nFrom:({email["from"].decode()})\n{email["body"]}\n')
        else:
            print('Please select a mailbox first')

    def do_list(self, arg):
        'List messages in the current mailbox. Usage: list OR list <number of messages>'
        if self.current_mailbox:
            if arg:
                arg.strip()
                try:
                    num_messages = int(arg)
                except ValueError:
                    print('Invalid number of messages')
                    return
            else:
                num_messages = -10
            emails = self.client_utils.get_mail(self.current_mailbox, num=num_messages)
            for email in emails:
                print(f'{email["subject"]} ({email["from"]})\n{email["body"]}\n')
        else:
            print('Please select a mailbox first')

    def do_quit(self, arg):
        'Exit the shell. Usage: quit'
        print('Goodbye!')
        self.client_utils.disconnect()
        return True
    
    def do_select(self, arg):
        'Select a valid mailbox. Usage: select OR select <mailbox>'
        mailboxes = self.client_utils.list_mailboxes()
        if arg:
            arg.strip()
            if arg in mailboxes:
                self.current_mailbox = arg
                print(f'Selected mailbox {arg}')
                self.set_prompt()
                return
            else:
                print('Invalid mailbox')
        for mailbox in enumerate(mailboxes):
            if "\\Noselect" not in mailbox:
                print(str(mailbox[0]) + ") " + mailbox[1])
        selection = input("Which mailbox would you like to view? (Select a number) ")
        self.current_mailbox = mailboxes[int(selection)]
        print(f'Selected mailbox {self.current_mailbox}')
        self.set_prompt()

    def do_unselect(self, arg):
        'Unselect a mailbox. Usage: unselect'
        if self.current_mailbox:
            self.current_mailbox = None
            print('Unselected mailbox')
            self.client_utils.unselect_mailbox()
            self.set_prompt()

    def set_prompt(self):
        if self.current_mailbox:
            ClientShell.prompt = f'(FEE-Mail)-({self.current_mailbox})$ '
        else:
            ClientShell.prompt = '(FEE-Mail)$ '

if __name__ == '__main__':
    ClientShell().cmdloop()
