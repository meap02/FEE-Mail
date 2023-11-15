
import cmd
from ClientUtils import ClientUtils
import json
from getpass import getpass

class ClientShell(cmd.Cmd):
    intro = 'Welcome to the FEE-Mail client shell. Type help or ? to list commands.\n'
    prompt = '(FEE-Mail)$'

    def __init__(self):
        super().__init__()
        creds_exists = input('Do you have a creds.json file? (y/n) ')
        if creds_exists == 'y':
            creds_file = input('Enter creds.json file path: ')
            with open(creds_file) as f:
                creds = json.load(f)
            name = input('Enter your name: ')
            smtp_server = creds[name]['smtp_server']
            smtp_port = creds[name]['smtp_port']
            username = creds[name]['username']
            password = creds[name]['password']
        else:
            smtp_server = input('Enter SMTP server: ')
            smtp_port = int(input('Enter SMTP port: '))
            username = input('Enter username (all text before the @ symbol): ')
            password = getpass('Enter password: ')
        self.client_utils = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, username=username, password=password)
        self.client_utils.connect()

    def do_send(self, arg):
        'Send an email and be prompted for the to, subject, and body. Usage: send'
        to = input('To: ')
        subject = input('Subject: ')
        body = input('Body: ')
        self.client_utils.send_email(to, subject, body)
        print('Email sent successfully.')

    def do_list(self, arg):
        'List all emails. Usage: list'
        emails = self.client_utils.receive_emails()
        for email in emails:
            print(f'{email["id"]}: {email["subject"]} ({email["from"]})')

    def do_quit(self, arg):
        'Exit the shell. Usage: quit'
        print('Goodbye!')
        return True

if __name__ == '__main__':
    ClientShell().cmdloop()
