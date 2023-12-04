from tkinter import *
import cmd
from ClientUtils import ClientUtils
import json
from getpass import getpass



m = Tk()
m.title('FEE-MAIL')

smtp_server = 'smtp.gmail.com'
smtp_port = 587
username = ''
password = ''
to_address = StringVar()
subject = StringVar()
body = StringVar()

def printBody():
    address=to_address.get()
    input = bodyEntry.get("1.0","end")
    print(address)
    print(input)
    print("hellop")
    to_address.set("")



cu = ClientUtils(smtp_server=smtp_server, smtp_port=smtp_port, username=username, password=password)
cu.connect()
toAddressLabel = Label(m, text='Send To:').place(x=0,y=10)
toAddressEntry = Entry(m,textvariable=to_address).place(x=60,y=10)
subjectLabel = Label(m, text='Subject:').place(x=0,y=30)
subjectEntry = Entry(m, textvariable=subject).place(x=60,y=30)
bodyLabel = Label(m, text='Message:').place(x=0,y=50)

bodyEntry = Text(m)
bodyEntry.place(height=100, width=500, x=60, y=50)

def sendEmail():
    address = to_address.get()
    subj = subject.get()
    input_body = bodyEntry.get("1.0", "end")

    cu.send_email(to_address=address, subject=subj, body=input_body)

    print(f"Email sent to {address}")
    to_address.set("")
    subject.set("")
    bodyEntry.delete("1.0", END)


sendButton = Button(m, text='Send', width=25, command=sendEmail).place(x=60, y=150)

m.geometry("600x300")
m.mainloop()
