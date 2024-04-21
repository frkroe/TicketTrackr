import argparse
import logging
import os
import subprocess

from dotenv import load_dotenv

# import yaml


logger = logging.getLogger('cli')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

dotenv_path = "./secrets/.env"
load_dotenv(dotenv_path)


class TicketTrackrETL:

    def extract_tickets_from_gmail(self, refresh_token, sender_email, gmail_secret_path,
                                   save_dir):
        os.environ['REFRESH_TOKEN'] = refresh_token
        os.environ['SENDER_EMAIL'] = sender_email
        os.environ['GMAIL_CLIENT_SECRET_PATH'] = gmail_secret_path
        os.environ['SAVE_DIR'] = save_dir
        subprocess.run(['python3', './extract_tickets_from_gmail/main.py'], check=True)

    def convert_pdf_to_avro(self, pdf_dir):
        os.environ['PDF_DIR'] = pdf_dir
        subprocess.run(['python3', './convert_pdf_to_avro/main.py'], check=True)

    def upload_files_to_nas(self, synology_ip, synology_port, synology_username,
                            synology_password, synology_dir):
        os.environ['SYNOLOGY_IP'] = synology_ip
        os.environ['SYNOLOGY_PORT'] = synology_port
        os.environ['SYNOLOGY_USERNAME'] = synology_username
        os.environ['SYNOLOGY_PASSWORD'] = synology_password
        os.environ['SYNOLOGY_DIRECTORY'] = synology_dir
        subprocess.run(['python3', './upload_files_to_nas/main.py'], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract_tickets_from_gmail",
                        action="store_true",
                        help="Execute gmail tickets extraction")
    parser.add_argument("--convert_pdf_to_avro",
                        action="store_true",
                        help="Execute convert pdfs to avros")
    parser.add_argument("--upload_files_to_nas",
                        action="store_true",
                        help="Execute uplaod files to nas")
    args = parser.parse_args()
    ticket_tracker = TicketTrackrETL()
    if args.extract_tickets_from_gmail:
        logger.info('Starting gmail ticket extraction')
        refresh_token = os.getenv('REFRESH_TOKEN')
        sender_email = os.getenv('SENDER_EMAIL')
        gmail_secret_path = os.getenv('GMAIL_CLIENT_SECRET_PATH')
        save_dir = os.getenv('SAVE_DIR')
        ticket_tracker.extract_tickets_from_gmail(refresh_token, sender_email,
                                                  gmail_secret_path, save_dir)
    if args.convert_pdf_to_avro:
        logger.info('Starting conversion from pdf to avro')
        pdf_dir = './extract_tickets_from_gmail/emails'
        ticket_tracker.convert_pdf_to_avro(pdf_dir)

    if args.upload_files_to_nas:
        logger.info('Starting load of files to NAS')
        synology_ip = os.getenv("SYNOLOGY_IP")
        synology_port = os.getenv("SYNOLOGY_PORT")
        synology_username = os.getenv("SYNOLOGY_USERNAME")
        synology_password = os.getenv("SYNOLOGY_PASSWORD")
        synology_dir = os.getenv("SYNOLOGY_DIRECTORY")
        ticket_tracker.upload_files_to_nas(synology_ip, synology_port, synology_username,
                                           synology_password, synology_dir)
