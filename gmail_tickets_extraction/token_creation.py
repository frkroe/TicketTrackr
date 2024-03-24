from google_auth_oauthlib.flow import InstalledAppFlow

# Replace with the path to your downloaded client secrets file
CLIENT_SECRETS_FILE = '../secrets/gmail_client_secret.json'

# This scope will allow the application to access and modify your Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    refresh_token = credentials.refresh_token
    print(f"Refresh Token: {refresh_token}")
    # Add the refresh token to the .env file
    with open('../secrets/.env', 'a') as f:
        f.write(f"\nREFRESH_TOKEN={refresh_token}")

    print("Refresh token added to .env file.")


if __name__ == '__main__':
    main()
