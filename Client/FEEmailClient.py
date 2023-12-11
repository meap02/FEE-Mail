from tkinter import *
from tkinter import messagebox, ttk
from ClientUtils import ClientUtils
import json
import html

# Initialize the main application window
app = Tk()
app.title('FEE-MAIL')
app.geometry("1000x600")

# Create a tab control
tabControl = ttk.Notebook(app)

# SMTP and IMAP configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
username = ''  # Replace with actual username
password = ''  # Replace with actual password

# ClientUtils instance
cu = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, username=username, password=password)
cu.connect()
cu.connect_imap()  # Connect to IMAP server

# Send Email Tab
send_tab = ttk.Frame(tabControl)
tabControl.add(send_tab, text='Send Email')

# Inbox Tab
inbox_tab = ttk.Frame(tabControl)
tabControl.add(inbox_tab, text='Inbox') 
tabControl.pack(expand=1, fill="both")

# Email sending section on Send Email Tab
to_address = StringVar()
subject = StringVar()
body = StringVar()

Label(send_tab, text='Send To:').grid(row=0, column=0, sticky=W)
Entry(send_tab, textvariable=to_address).grid(row=0, column=1, sticky=(W, E))
Label(send_tab, text='Subject:').grid(row=1, column=0, sticky=W)
Entry(send_tab, textvariable=subject).grid(row=1, column=1, sticky=(W, E))
Label(send_tab, text='Message:').grid(row=2, column=0, sticky=W)
bodyEntry = Text(send_tab)
bodyEntry.grid(row=2, column=1, sticky=(W, E), pady=5)

def sendEmail():
    address = to_address.get()
    subj = subject.get()
    input_body = bodyEntry.get("1.0", "end")
    cu.send_email(to_address=address, subject=subj, body=input_body)
    messagebox.showinfo("Email", f"Email sent to {address}")
    to_address.set("")
    subject.set("")
    bodyEntry.delete("1.0", END)

Button(send_tab, text='Send', command=sendEmail).grid(row=3, column=1, pady=10, sticky=E)

# Email listing section on Inbox Tab
email_list = StringVar(value=[])
Label(inbox_tab, text='Inbox:').grid(row=0, column=0, sticky=W)
listbox = Listbox(inbox_tab, listvariable=email_list, height=20)
listbox.grid(row=1, column=0, columnspan=2, sticky=(W, E), padx=5, pady=5)

# Email reading section
email_content = Text(inbox_tab, state='disabled', wrap='word')
email_content.grid(row=1, column=2, sticky=(N, S, E, W), padx=5, pady=5)

inbox_tab.grid_columnconfigure(2, weight=1)  # Allows the email content to expand
inbox_tab.grid_rowconfigure(1, weight=1)  # Allows the email content to expand

def fetchEmails():
    try:
        emails = cu.fetch_emails(limit=10)
        email_subjects = [email['Subject'] for email in emails if email['Subject'] is not None]
        email_list.set(email_subjects)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch emails: {e}")

import html2text

def showEmailContent(event):
    # Ensure that an email is selected in the listbox
    if not listbox.curselection():
        return

    try:
        # Clear the email content Text widget first
        email_content.config(state='normal')
        email_content.delete('1.0', END)

        # Get the index of the selected email
        index = listbox.curselection()[0]
        selected_email = cu.fetch_emails(limit=10)[index]

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
        email_content.insert('1.0', plain_text)
        email_content.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show email content: {e}")
        email_content.config(state='disabled')

# Bind the Listbox select event to the showEmailContent function
listbox.bind('<<ListboxSelect>>', showEmailContent)

Button(inbox_tab, text='Refresh Inbox', command=fetchEmails).grid(row=2, column=0, sticky=W, padx=5, pady=10)

# Run the main loop
app.mainloop()
