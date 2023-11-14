
import argparse
from ClientUtils import *

# Create the parser
parser = argparse.ArgumentParser(description='FEE-Mail Client')

# Add the arguments
parser.add_argument('command', type=str, help='The command to execute')
parser.add_argument('--username', type=str, help='The username for authentication')
parser.add_argument('--password', type=str, help='The password for authentication')
parser.add_argument('--smtp-server', type=str, help='The SMTP server to connect to')
parser.add_argument('--smtp-port', type=int, help='The port to connect to the SMTP server on')
parser.add_argument('--to', type=str, help='The recipient of the email')
parser.add_argument('--subject', type=str, help='The subject of the email')
parser.add_argument('--body', type=str, help='The body of the email')

# Parse the arguments
args = parser.parse_args()

if(args.username == None):
    args.username = input("Username: ")
if(args.password == None):
    args.password = input("Password: ")
if(args.smtp_server == None):
    args.smtp_server = input("SMTP Server: ")
if(args.smtp_port == None):
    args.smtp_port = input("SMTP Port: ")
if(args.to != None):
    args.to = args.to.split(",")
    utils = ClientUtils(args.smtp_server, args.smtp_port, args.username, args.password)
    utils.connect()
    for recipient in args.to:
        utils.send_email(recipient, args.subject, args.body)

# Execute the command
if args.command == 'login':
    login(args.username, args.password)
elif args.command == 'send':
    send_email(args.username, args.password, args.to, args.subject, args.body)
elif args.command == 'list':
    list_emails(args.username, args.password)
else:
    print('Invalid command')
