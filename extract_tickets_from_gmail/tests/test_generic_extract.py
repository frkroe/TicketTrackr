import os

import pytest
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from extract_tickets_from_gmail.main import GmailService

# Load variables from .env
load_dotenv('./secrets/.env')

REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SAVE_DIR = os.getenv('SAVE_DIR')
GMAIL_CLIENT_SECRET_PATH = os.getenv('GMAIL_CLIENT_SECRET_PATH')


@pytest.fixture
def gmail_service():
    return GmailService(REFRESH_TOKEN, SENDER_EMAIL, SAVE_DIR, GMAIL_CLIENT_SECRET_PATH)


def test_gmail_authenticate(gmail_service):
    service = gmail_service.gmail_authenticate()
    assert isinstance(service, type(build('gmail', 'v1', credentials=Credentials(None))))
