import argparse
import logging
import os
import subprocess
import yaml

from dotenv import load_dotenv

logger = logging.getLogger('cli')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

dotenv_path = "../secrets/.env"
load_dotenv(dotenv_path)

filename = '20240316 Mercadona 103,45 €.pdf'
pdf_dir = '../gmail_ticket_extraction/emails'


class TicketTrackrETL:

    def upload_files_to_nas(self, synology_ip, synology_port,
                            synology_username, synology_password):
        os.environ['SYNOLOGY_IP'] = synology_ip
        os.environ['SYNOLOGY_PORT'] = synology_port
        os.environ['SYNOLOGY_USERNAME'] = synology_username
        os.environ['SYNOLOGY_PASSWORD'] = synology_password
        subprocess.run(['python3', './upload_files_to_nas/main.py'], check=True)

    def convert_pdf_to_avro(self, pdf_dir):
        os.environ['PDF_DIR'] = pdf_dir
        subprocess.run(['python3', './convert_pdf_to_avro/main.py'], check=True)

    d
