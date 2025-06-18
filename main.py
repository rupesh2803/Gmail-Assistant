from LLM import load_result
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    cred = None
    if os.path.exists('token.json'):
        cred = Credentials.from_authorized_user_file('token.json',SCOPES)
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json',SCOPES)
            cred = flow.run_local_server(port=0)
        with open('token.json','w') as token:
            token.write(cred.to_json())
    service = build(serviceName="gmail",version="v1",credentials=cred)
    return service

def create_msg(sender,to,sub,body):
    message = MIMEMultipart()
    message['from']=sender
    message['to']=to
    message['subject']=sub

    message.attach(MIMEText(body,'plain'))

    raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return raw_msg

def send_email(service,to,sub,body,sender='projectchatbot.v1@gmail.com'):
    try:
        raw_msg = create_msg(sender,to,sub,body)
        service.users().messages().send(userId='me',body={'raw':raw_msg}).execute()
        print(f"Email sent to {to}")
    except HttpError as e:
        print(f"An error occured {e}")

def get_email(service,user_id='me'):
    try:
        results = service.users().messages().list(userId=user_id,q="is:unread",maxResults=1).execute()
        if not results :
            return None
        multi_messages = results['messages']
        thread_id = multi_messages[0]['threadId']

        messages = service.users().messages().get(userId=user_id,id=multi_messages[0]['id'],format='metadata').execute()
        sub = None
        body = messages['snippet']
        for header in messages['payload']['headers']:
            if header['name'].lower()=='content-type':
                content_type = header['value'].split(";")[0]
            elif header['name'].lower()=='from':
                to = header['value']
            elif header['name'].lower()=='subject':
                sub = header['value']

        return {
            'id':multi_messages[0]['id'],
            'threadId':thread_id,
            'subject':sub,
            'body':body,
            'to':to,
            'content_type':content_type
        }

    except Exception as e:
        print(f"An error occured:{e}")

def mark_as_read(service,id):
    msg_label = {
        'removeLabelIds':['UNREAD']
    }
    service.users().messages().modify(userId='me',id=id,body=msg_label).execute()
    print('Marked Read Successful')


service = authenticate_gmail()

email_details = get_email(service)

if email_details is None:
    print("No email is unread")
else:
    response = load_result(email_details['body'])
    send_email(service,email_details['to'],'RE+'+email_details['subject'],response)
    print("\nMail sent Successfully")
    mark_as_read(service,email_details['id'])