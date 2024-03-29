# from synology_api import filestation
import os
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3 import disable_warnings

'''

SYNOLOGY FILE STATION API GUIDE:
https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf

'''

# Accessing variables from .env file in secrets folder
dotenv_path = "../secrets/.env"
load_dotenv(dotenv_path)

synology_ip = os.getenv("SYNOLOGY_IP")
synology_port = os.getenv("SYNOLOGY_PORT")
synology_username = os.getenv("SYNOLOGY_USERNAME")
synology_password = os.getenv("SYNOLOGY_PASSWORD")


# Disable warnings for API requests
disable_warnings()



class FileStation():
    def __init__(self, synology_ip: str, synology_port: str, synology_username: str, synology_password: str):
        try:
            # Base URL of the API endpoint
            self.base_url = f"https://{synology_ip}:{synology_port}/webapi/query.cgi"

            # Step 1: Retrieve API Information
            params_info = {
                'api': 'SYNO.API.Info',
                'version': '1',
                'method': 'query',
                'query': 'all'
            }
            print("\nRetrieve API Information...\n")
            response_info = requests.get(self.base_url, params=params_info,verify=False)
            # print(response_info.text)
            
            # Step 2: Login
            if not 'error' in response_info.json():
                params_login = {
                    'api': 'SYNO.API.Auth',
                    'version': '3',
                    'method': 'login',
                    'account': synology_username,
                    'passwd': synology_password,
                    'session': 'FileStation',
                    'format': 'sid'
                } 
                print("\nLogging in...\n")
                response = requests.get(self.base_url, params=params_login,verify=False)
                print(response.text)

                self.sid = response.json()['data']['sid']

        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def logout(self):
        try: 
            params_logout = {
                'api': 'SYNO.API.Auth',
                'version': '6',
                'method': 'logout',
                'session': 'FileStation'
            }
            print("\nLogging out...\n")
            response = requests.get(self.base_url, params=params_logout,verify=False)
            print(response.text)
            
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def list_directories(self):
        try: 
            params_list = {
            'api': 'SYNO.FileStation.List',
            'version': '2',
            'method': 'list_share',
            '_sid': self.sid
            }
            print("\nList directories...\n")
            response = requests.get(self.base_url, params=params_list,verify=False)
            print(response.text)

        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def upload_file(self, dest_path: str, file_path: str):
        try:
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as payload:
                params_upload = {
                    'api': 'SYNO.FileStation.Upload',
                    'version': '2',
                    'method': 'upload',
                    '_sid': self.sid
                }
                args = {
                    'path': dest_path,
                    'create_parents': False,
                    'overwrite': True,
                }
                files = {'file': (filename, payload, 'application/octet-stream')}
                
                print(f"\nUpload file {file_path}...\n")
                response = requests.post(self.base_url, params=params_upload, data=args, files=files, verify=False)
                print(response.text)

        except requests.exceptions.RequestException as e:
            print("Error:", e)



# Initiate the class and call desired functions
nas_class = FileStation(synology_ip, synology_port, synology_username, synology_password)

nas_class.list_directories()
nas_class.upload_file('/Miguel', './test.txt')
nas_class.logout()