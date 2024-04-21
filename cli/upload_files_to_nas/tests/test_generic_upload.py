import os

import pytest
import requests_mock
from dotenv import load_dotenv

from upload_files_to_nas.main import FileStation

# Load variables from .env
load_dotenv('./secrets/.env')

synology_ip = os.getenv("SYNOLOGY_IP")
synology_port = os.getenv("SYNOLOGY_PORT")
synology_username = os.getenv("SYNOLOGY_USERNAME")
synology_password = os.getenv("SYNOLOGY_PASSWORD")


@pytest.fixture
def nas_service():
    with requests_mock.Mocker() as m:
        m.get(f'https://{synology_ip}:{synology_port}/webapi/query.cgi',
              json={'data': {'sid': 'mock_sid'}})
        return FileStation(synology_ip,
                           synology_port,
                           synology_username,
                           synology_password)


def test_login(nas_service):
    assert hasattr(nas_service, 'sid')
    assert nas_service.sid == 'mock_sid'
