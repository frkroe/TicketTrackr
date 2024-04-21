import base64
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SAVE_DIR = os.getenv('SAVE_DIR')
GMAIL_CLIENT_SECRET_PATH = os.getenv('GMAIL_CLIENT_SECRET_PATH')


class GmailService:
    def __init__(self, refresh_token=REFRESH_TOKEN, sender_email=SENDER_EMAIL,
                 save_dir=SAVE_DIR, client_secret_path=GMAIL_CLIENT_SECRET_PATH):
        self.refresh_token = refresh_token
        self.sender_email = sender_email
        self.save_dir = save_dir
        self.client_secret_path = client_secret_path

        with open(self.client_secret_path) as f:
            data = json.load(f)

        self.client_id = data['installed']['client_id']
        self.client_secret = data['installed']['client_secret']

        self.scopes = ['https://www.googleapis.com/auth/gmail.modify']

    def gmail_authenticate(self):
        creds = Credentials(None, refresh_token=self.refresh_token,
                            token_uri='https://oauth2.googleapis.com/token',
                            client_id=self.client_id, client_secret=self.client_secret,
                            scopes=self.scopes)
        creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)

    def dowload_messages(self, service):
        try:
            # Search for unread emails from the specified sender
            query = f'is:unread from:{self.sender_email} has:attachment'
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No unread messages with attachments found.")
                return
            print(f"Found {len(messages)} messages with for PDF attachments")
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')

    def download_pdfs_from_messages(self, service, messages):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        for message in messages:
            msg = service.users().messages().get(userId='me',
                                                 id=message['id'],
                                                 format='full').execute()
            parts = [part for part in msg['payload'].get('parts', [])
                     if part['mimeType'] == 'application/pdf']
            # Download PDF attachments
            for part in parts:
                if 'filename' in part and part['filename'].lower().endswith('.pdf'):
                    att_id = part['body']['attachmentId']
                    att = service.users() \
                        .messages().attachments().get(userId='me',
                                                      messageId=message['id'],
                                                      id=att_id).execute()
                    data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    path = os.path.join(self.save_dir, part['filename'])

                    with open(path, 'wb') as f:
                        f.write(file_data)

                    print(f"PDF attachment {part['filename']} saved to {path}.")

    def mark_messages_as_read(self, service, messages):
        for message in messages:
            # Mark email as read
            service.users().messages(). \
                modify(userId='me', id=message['id'],
                       body={'removeLabelIds': ['UNREAD']}).execute()


if __name__ == "__main__":
    gmail_service = GmailService()
    service = gmail_service.gmail_authenticate()
    messages = gmail_service.dowload_messages(service)
    gmail_service.download_pdfs_from_messages(service, messages)
    gmail_service.mark_messages_as_read(service, messages)
