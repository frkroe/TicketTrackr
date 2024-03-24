import os
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

# Load environment variables
dotenv_path = "../secrets/.env"
load_dotenv(dotenv_path)

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')

# Load client secrets values
GMAIL_CLIENT_SECRET_PATH = os.getenv('GMAIL_CLIENT_SECRET_PATH')

with open(GMAIL_CLIENT_SECRET_PATH) as f:
    data = json.load(f)

CLIENT_ID = data['installed']['client_id']
CLIENT_SECRET = data['installed']['client_secret']

SAVE_DIR = os.getenv('SAVE_DIR')
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailService:
    def gmail_authenticate():
        creds = Credentials(None, refresh_token=REFRESH_TOKEN,
                            token_uri='https://oauth2.googleapis.com/token',
                            client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                            scopes=SCOPES)
        creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)

    def download_attachments(service):
        try:
            # Search for unread emails from the specified sender
            query = f'is:unread from:{SENDER_EMAIL} has:attachment'
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No unread messages with attachments found.")
                return
            print(f"Found {len(messages)} messages. Checking for PDF attachments...")

            # Create a directory to save the attachments (if it doesn't exist)
            if not os.path.exists(SAVE_DIR):
                os.makedirs(SAVE_DIR)
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
                        path = os.path.join(SAVE_DIR, part['filename'])

                        with open(path, 'wb') as f:
                            f.write(file_data)

                        print(f"PDF attachment {part['filename']} saved to {path}.")

                # Mark email as read
                service.users().messages(). \
                    modify(userId='me', id=message['id'],
                           body={'removeLabelIds': ['UNREAD']}).execute()
        except HttpError as error:
            print(f'An error occurred: {error}')


if __name__ == "__main__":
    gmail_service = GmailService()
    service = gmail_service.gmail_authenticate()
    gmail_service.download_attachments(service)
