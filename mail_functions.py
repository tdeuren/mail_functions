"""This are some basic functions for handling mails"""

import imaplib, ssl, email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import getpass

def show_inbox(username, password):
    """This function prints for every mail in your inbox the sender and the subject and returns True if no errors occured.
    This only works for gmail, telenet and outlook."""
    
    # Login
    imap = None # Which imap server
    service = username.split('@')[1].split('.')[0]
    if service == "gmail":
        imap = 'imap.gmail.com'
    if service == "telenet":
        imap = 'imap.telenet.be'
    if service == "outlook":
        imap = 'imap-mail.outlook.com'
    try:
        mail = imaplib.IMAP4_SSL(imap, 993) # Connect
        mail.login(username, password) # Login
    except:
        print("Login failed")
        return False
    
    # Read every mail
    mail.select('Inbox') # Go to inbox
    typ, data = mail.search(None, 'ALL') # Search all mails
    ids = data[0] # Get all ids
    id_list = ids.split()
    maxi = len(id_list) # Number of ids
    latest_email_id = int( id_list[-1] ) # Latest mail id
    print("\n")
    for i in range( latest_email_id, latest_email_id-maxi, -1 ): # Every mail, latest first
        typ, data = mail.fetch( b'%d'%i, '(RFC822)' ) # Fetch mail i
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1]) # Get message
                varSubject = msg['subject']
                varFrom = msg['from']
                print(varFrom)
                try:
                    if (varSubject[0] == '='): # Don't print nonsense
                        print("\tCan't read this")
                    else:
                        print("\t", varSubject)
                except:
                    print("\tCan't read this")
    print("\n")

    # Close connection
    mail.close()
    mail.logout()
    return True

def send_email(username, password, message, to, subject):
    """This function sends a mail and returns True if no errors occured.
    This only works for telenet."""
    
    # Message
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Send mail
    try:
        server = smtplib.SMTP('smtp.telenet.be', 587) # Connect to smtp server
        server.starttls() # Start tls enscription
        server.login(username, password) # Login
        server.sendmail(msg['From'], msg['To'], msg.as_string()) # Send mail
        server.quit()
        return True
    except:
        return False

def move_email(username, password, subject, destination):
    """This function moves all mails with subject to destination and returns True if no errors occured.
    This only works for telenet."""

    try:
        # Login
        mail = imaplib.IMAP4_SSL('imap.telenet.be', 993) # Connect to imap server
        mail.login(username, password) # Login
        mail.select('Inbox') # Go to inbox

        # Move mails
        typ, [response] = mail.search(None, '(SUBJECT %s)' %subject.split()[0]) # Search all mails with subject
        msg_ids = ','.join(response.decode("utf-8").split(' ')) # Get all mail ids from search
        mail.copy(msg_ids, destination) # copy mails to new location
        mail.store(msg_ids, '+FLAGS', r'(\Deleted)') # Move mails to \Deleted
        mail.expunge() # Delete mails in \Deleted
        
        # Close connection
        mail.close()
        mail.logout()
        return True
    except:
        return False

def commandline_input():
    """This function lets you call the above functions in a simple way on the commandline."""
    
    print("Tasks: 'showinbox', 'sendemail', 'moveemail' and 'quit'")
    print("Example: Task: showinbox\n")
    while(True):
        inp = input("Task: ").strip()
        if inp == "showinbox":
            username = input("Username: ")
            password = getpass.getpass(prompt='Password: ')
            if show_inbox(username, password):
                print("Task succeeded!")
            else:
                print("Task failed!")
            inp = ""
        if inp == "sendemail":
            username = input("Username: ")
            password = getpass.getpass(prompt='Password: ')
            msg = input("Message: ")
            dest = input("To: ")
            subject = input("Subject: ")
            if send_email(username, password, msg, dest, subject):
                print("Task succeeded!")
            else:
                print("Task failed!")
            inp = ""
        if inp == "moveemail":
            username = input("Username: ")
            password = getpass.getpass(prompt='Password: ')
            subject = input("Subject keyword: ")
            dest = input("Destination: ")
            if move_email(username, password, subject, dest):
                print("Task succeeded!")
            else:
                print("Task failed!")
            inp = ""
        if inp == "quit":
            break
        print("\n")

if __name__ == "__main__":
    commandline_input()