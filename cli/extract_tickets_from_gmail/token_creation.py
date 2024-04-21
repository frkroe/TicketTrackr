from google_auth_oauthlib.flow import InstalledAppFlow

PATH = '../secrets/'

# Replace with the path to your downloaded client secrets file
CLIENT_SECRETS_FILE = PATH + 'gmail_client_secret.json'

# This scope will allow the application to access and modify your Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def overwrite_env_variable(variable, value):
    # Read the .env file into memory
    with open(PATH + '.env', 'r') as file:
        lines = file.readlines()

    # Modify the variable if it exists, otherwise append it
    for i, line in enumerate(lines):
        if line.startswith(f"{variable}="):
            lines[i] = f"{variable}={value}\n"
            break
    else:
        lines.append(f"{variable}={value}\n")

    # Write the .env file back to disk
    with open(PATH + '.env', 'w') as file:
        file.writelines(lines)


if __name__ == '__main__':
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    refresh_token = credentials.refresh_token
    print(f"Refresh Token: {refresh_token}")
    # Add the refresh token to the .env file
    # Usage
    overwrite_env_variable("REFRESH_TOKEN", refresh_token)

    print("Refresh token added to .env file.")
