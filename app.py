import json
import base64
import os.path
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


def get_attachment_files(creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        # list messages from some sender
        results = service.users().messages().list(userId='me',q='from:sender <noreply@sender.com>').execute()
        message_count = len(results['messages'])
        for i in range(message_count):
            # Get Message Id to scrape every message alone
            messageI = results['messages'][i]['id']
            result2 = service.users().messages().get(userId='me',id=messageI).execute()
            try:
                pdf = result2['payload']['parts'][1]['body']['attachmentId']
                fileName = result2['payload']['parts'][1]['filename']
                isExist = os.path.exists(fileName)
                if (isExist):
                    print('pass')
                    pass
                else:
                    result3 = service.users().messages().attachments().get(userId='me', messageId=messageI, id=pdf, x__xgafv=None).execute()
                    file_64_decode = base64.urlsafe_b64decode(result3['data'].encode('UTF-8'))
                    file = open(fileName, 'wb') # create a writable file and write the decoding result
                    file.write(file_64_decode)
                    print(f'[+] Downloaded {fileName}')
                   
            except Exception as error:
                print(f'An error occurred: {error}')

    except HttpError as error:
        print(f'An error occurred: {error}')


def auth_create_token():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


if __name__ == '__main__':
    creds = auth_create_token()
    get_attachment_files(creds)
    pass