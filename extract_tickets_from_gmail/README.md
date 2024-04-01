# Gmail Ticket Extraction

This directory contains the code for extracting ticket information sent as pdf attachments in gmail.

## Setup

1. **Create a `.env` file in the root directory of the project and add the following environment variables:**
```bash
SENDER_EMAIL= # Email address of the sender
```

2. **Create Credentials for the Gmail API by following these instructions:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/), choose the project you want to use, and enable the Gmail API for the project.
    - Open the [Credentials tab](https://console.cloud.google.com/apis/credentials), and create credentials for the Gmail API.
        - Credentials type: OAuth client ID
        - Application type: Desktop app 
        - Name: anything you want
    - Download the credentials file and save it as `gmail_client_secret.json` in the [secrets directory](../secrets/).
    - Open the [OAuth consent screen tab](https://console.cloud.google.com/apis/credentials/consent) and add your personal email address to the test users.


3. **In a virtual environment, install the required packages and execute the code:**
```bash
pip install virtualenv

# Create a virtual environment
virtualenv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Run the code
python token_creation.py
python extract_tickets.py

# Deactivate the virtual environment
deactivate
```

## Code Structure

- `token_creation.py`: This script creates a refresh token for the Gmail API and saves it as environment variable `REFRESH_TOKEN` in the `.env` file. The refresh token is used to generate an access token for the Gmail API, with which the code can access the user's Gmail account.
- `extract_tickets.py`: This script extracts ticket information from pdf attachments in the user's Gmail account and saves the information in a csv file.

