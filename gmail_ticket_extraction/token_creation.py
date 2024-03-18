from google_auth_oauthlib.flow import InstalledAppFlow

# Replace with the path to your downloaded client secrets file
CLIENT_SECRETS_FILE = '../secrets/client_secret_mimove.json'

# This scope will allow the application to access and modify your Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    print(f"Refresh Token: {credentials.refresh_token}")
    # Save the refresh token securely, you'll need it in your application

if __name__ == '__main__':
    main()
