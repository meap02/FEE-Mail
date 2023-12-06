
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
            imap_server = creds['imap_server']
            imap_port = creds['imap_port']
            username = creds['username']
            password = creds['password']
        else:
            smtp_server = input('Enter SMTP server: ')
            smtp_port = input('Enter SMTP port: ')
            if smtp_port != '':
                smtp_port = int(smtp_port)
            imap_server = input('Enter IMAP server: ')
            imap_port = input('Enter IMAP port: ')
            if imap_port != '':
                imap_port = int(imap_port)
            username = input('Enter username (all text before the @ symbol): ')
            password = getpass('Enter password: ')

        self.client_utils = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, imap_server=imap_server, imap_port=imap_port, username=username, password=password)
        self.current_mailbox = None
        self.client_utils.connect()

    def pause(self):
        programPause = input("Press the <ENTER> key to continue...")

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
            self.client_utils.send_mail(address, subject, body)
            print('Email sent successfully to ' + address)

    def do_get(self, arg):
        'Get messages in the current mailbox. Usage: get <filters>'
        self.display(self.client_utils.get_mail(mailbox=self.current_mailbox, filter=arg))

    def display(self, emails):
        running = True
        if len(emails) == 0:
                print('No emails')
        elif len(emails) > 10:
            choice = input(f"There are {len(emails)} emails retrived. Would you like to display all of them? (y/n)")
        else:
            choice = 'y'
        if choice == 'y':
            print("Entering display view, press 'q' to leave display view")
            while running:
                for email in enumerate(emails, 1):
                    print(f'{email[0]}) {email[1]["subject"]}\tFrom:({email[1]["from"]})')
                index = input('Select an email to read (enter a number): ')
                if index=='q':
                    running = False
                    print("Leaving display view")
                elif index.isdigit():
                    index = int(index)
                    if index < len(emails):
                        print(emails[index].__dict__.keys())
                        print(f'{emails[index]["subject"]}\nFrom:({emails[index]["from"]})\nCC:({emails[index]["cc"]})\nbCC:({emails[index]["bcc"]})\n{emails[index].get_payload()}')
                        self.pause()
                    else:
                        print('Invalid index')
                else:
                    print('Invalid index')



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
        for mailbox in enumerate(mailboxes, 1):
            print(str(mailbox[0]) + ") " + mailbox[1])
        selection = input("Which mailbox would you like to view? (Select a number) ")
        if selection.isdigit():
            selection = int(selection)
            if selection < len(mailboxes):
                self.current_mailbox = mailboxes[selection]
                print(f'Selected mailbox {self.current_mailbox}')
                self.set_prompt()
            else:
                print('Invalid index')
        else:
            print('Invalid index')
    
    def do_unselect(self, arg):
        'Unselect a mailbox. Usage: unselect'
        if self.current_mailbox:
            self.current_mailbox = None
            print('Unselected mailbox')
            self.set_prompt()
        else:
            print('No mailbox selected')

    def set_prompt(self):
        if self.current_mailbox:
            ClientShell.prompt = f'(FEE-Mail)-({self.current_mailbox})$ '
        else:
            ClientShell.prompt = '(FEE-Mail)$ '

if __name__ == '__main__':
    ClientShell().cmdloop()
