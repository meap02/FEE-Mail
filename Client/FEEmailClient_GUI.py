from tkinter import *
from tkinter import messagebox, ttk
from ClientUtils import ClientUtils
import json
import html
import html2text

class GUIApp():
    def __init__(self):
        app = Tk() # Create the window
        app.title('FEE-MAIL') # Change the title
        app.geometry("1000x600") # Change the size
        tabControl = ttk.Notebook(app) # Create Tab Control
        with open('Client/creds.json') as f: # Load the credentials
            creds = json.load(f)
        smtp_server = creds['smtp_server']
        smtp_port =  creds['smtp_port']
        imap_server = creds['imap_server']
        imap_port = creds['imap_port']
        username = creds['username']
        password = creds['password']
        self.cu = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, imap_server=imap_server, imap_port=imap_port, username=username, password=password) # Create the ClientUtils object
        self.current_mailbox = None # Initialize the current mailbox
        self.cu.connect() # Connect to the server and login
        self.send_tab = ttk.Frame(tabControl) # Create the send tab
        tabControl.add(self.send_tab, text='Send Email') 
        self.inbox_tab = ttk.Frame(tabControl) # Create the inbox tab
        tabControl.add(self.inbox_tab, text='Inbox')
        tabControl.pack(expand=1, fill="both")
        self.to_address = StringVar() # Initialize the variables
        self.subject = StringVar() 
        self.body = StringVar()
        self.emails = [] # Initialize the emails

        Label(self.send_tab, text='Send To:').grid(row=0, column=0, sticky=W) # Add the labels and entries to the send tab
        Entry(self.send_tab, textvariable=self.to_address).grid(row=0, column=1, sticky=(W, E)) 
        Label(self.send_tab, text='Subject:').grid(row=1, column=0, sticky=W)
        Entry(self.send_tab, textvariable=self.subject).grid(row=1, column=1, sticky=(W, E))
        Label(self.send_tab, text='Message:').grid(row=2, column=0, sticky=W)
        self.bodyEntry = Text(self.send_tab)
        self.bodyEntry.grid(row=2, column=1, sticky=(W, E), pady=5)

        Button(self.send_tab, text='Send', command=self.sendEmail).grid(row=3, column=1, pady=10, sticky=E)

        # Email listing section on Inbox Tab
        self.email_list = StringVar(value=[])
        Label(self.inbox_tab, text='Inbox:').grid(row=0, column=0, sticky=W)
        self.listbox = Listbox(self.inbox_tab, listvariable=self.email_list, height=20)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky=(W, E), padx=5, pady=5)

        self.current_mailbox = ttk.Combobox(self.inbox_tab, values=self.cu.list_mailboxes(), state='readonly')
        self.current_mailbox.grid(row=0, column=1, sticky=E)
        self.current_mailbox.set("INBOX")


        # Email reading section
        self.email_content = Text(self.inbox_tab, state='disabled', wrap='word')
        self.email_content.grid(row=1, column=2, sticky=(N, S, E, W), padx=5, pady=5)

        self.inbox_tab.grid_columnconfigure(2, weight=1)  # Allows the email content to expand
        self.inbox_tab.grid_rowconfigure(1, weight=1)  # Allows the email content to expand

        # Bind the Listbox select event to the showEmailContent function
        self.listbox.bind('<<ListboxSelect>>', self.showEmailContent)
        Button(self.inbox_tab, text='Refresh Inbox', command=self.fetchEmails).grid(row=2, column=0, sticky=W, padx=5, pady=10)
        app.mainloop()

    def sendEmail(self):
        address = self.to_address.get()
        subj = self.subject.get()
        input_body = self.bodyEntry.get("1.0", "end")
        self.cu.send_email(to_address=address, subject=subj, body=input_body)
        messagebox.showinfo("Email", f"Email sent to {address}")
        self.to_address.set("")
        self.subject.set("")
        self.bodyEntry.delete("1.0", END)

    def showEmailContent(self, event):
        # Ensure that an email is selected in the listbox
        if not self.listbox.curselection():
            return

        try:
            # Clear the email content Text widget first
            self.email_content.config(state='normal')
            self.email_content.delete('1.0', END)

            # Get the index of the selected email
            index = self.listbox.curselection()[0]
            selected_email = self.emails[index]

            # Initialize a variable to hold the email content
            email_body = None

            # Check if the email is multipart
            if selected_email.is_multipart():
                for part in selected_email.walk():
                    # Check if the part has a content type of 'text/plain'
                    if part.get_content_type() == "text/plain":
                        content_disposition = part.get("Content-Disposition", "")
                        if "attachment" not in content_disposition:
                            email_body = part.get_payload(decode=True).decode()
                            break
            else:
                email_body = selected_email.get_payload(decode=True).decode()

            # Convert HTML to plain text if email_body is not None
            if email_body is not None:
                plain_text = html2text.html2text(email_body)
            else:
                plain_text = "This email has no text content."

            # Insert the plain text into the Text widget
            self.email_content.insert('1.0', plain_text)
            self.email_content.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show email content: {e}")
            self.email_content.config(state='disabled')

    def fetchEmails(self):
        try:
            self.emails = self.cu.get_mail(mailbox=self.current_mailbox.get(), filter="", limit=15)
            email_subjects = [email['Subject'] for email in self.emails if email['Subject'] is not None]
            self.email_list.set(email_subjects)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {e}")

if __name__ == '__main__':
    GUIApp()