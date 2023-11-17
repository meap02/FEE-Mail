
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
                creds_file = "C:\\Users\\kjjus\\github\\FEE-Mail\\Client\\creds.json"
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
        self.selected_mailbox = False
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
        'List all unread emails in the current mailbox. Usage: list'
        if self.selected_mailbox:  
            emails = self.client_utils.receive_new_emails()
            for email in emails:
                print(f'{email["id"]}: {email["subject"]} ({email["from"]})')
        else:
            print('Please select a mailbox first')

    def do_quit(self, arg):
        'Exit the shell. Usage: quit'
        print('Goodbye!')
        return True
    
    def do_select(self, arg):
        'Select a mailbox. Usage: select'
        if arg:
            self.client_utils.select_mailbox(arg)
        else:
            for mailbox in enumerate(self.client_utils.list_mailboxes()):
                if "\\Noselect" not in mailbox:
                    print(str(mailbox[0]) + ") " + mailbox[1])
            selection = input("Which mailbox would you like to view? (Select a number) ")
            self.client_utils.select_mailbox(selection)
        self.selected_mailbox = True

if __name__ == '__main__':
    ClientShell().cmdloop()
